from __future__ import annotations

import asyncio
import os
from datetime import datetime
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session

from .database import get_db, generate_instance_id
from . import crud, models
from .utils.network import check_tcp, check_udp, check_ping
from .utils.alert_sender import AlertSender, AlertEvaluator


class MonitorScheduler:
    def __init__(self, poll_interval: float = 2.0, lease_ttl: int = 10) -> None:
        self.poll_interval = poll_interval
        self.lease_ttl = lease_ttl
        self.instance_id = generate_instance_id()
        self._running = False

    async def start(self) -> None:
        self._running = True
        while self._running and os.getenv("PMON_SCHEDULER_ENABLED", "true").lower() == "true":
            await self._tick()
            await asyncio.sleep(self.poll_interval)

    async def stop(self) -> None:
        self._running = False

    async def _tick(self) -> None:
        # Tek leader davranışı için lease kullan
        for db in _db_iter():
            if not crud.try_acquire_lease(db, owner_id=self.instance_id, ttl_seconds=self.lease_ttl):
                return
            # due monitors
            now = datetime.utcnow()
            monitors = crud.due_monitors(db, now=now, limit=50)
            if not monitors:
                crud.renew_lease(db, owner_id=self.instance_id, ttl_seconds=self.lease_ttl)
                return
            await self._run_batch(db, monitors)
            crud.renew_lease(db, owner_id=self.instance_id, ttl_seconds=self.lease_ttl)

    async def _run_batch(self, db: Session, monitors: list[models.Monitor]) -> None:
        tasks = [self._run_one(db, m) for m in monitors]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _run_one(self, db: Session, monitor: models.Monitor) -> None:
        server = monitor.server
        service = monitor.service
        
        # Port kontrolü yap
        if service.protocol == models.ProtocolEnum.tcp:
            success, latency, error = await check_tcp(server.host, service.port)
        elif service.protocol == models.ProtocolEnum.udp:
            success, latency, error = await check_udp(server.host, service.port)
        elif service.protocol == models.ProtocolEnum.ping:
            success, latency, error = await check_ping(server.host)
        else:
            success, latency, error = False, None, f"Unsupported protocol: {service.protocol}"
        
        # Monitor durumunu güncelle
        monitor.last_status = "up" if success else "down"
        monitor.last_latency_ms = latency
        monitor.last_error = error
        monitor.last_checked_at = datetime.utcnow()
        
        # İstatistikleri güncelle
        crud.update_monitor_stats(db, monitor, success, latency)
        
        # Alert kurallarını değerlendir
        await self._evaluate_alerts(db, monitor)
        
        # Sonraki çalışma zamanını planla
        crud.schedule_next_run(db, monitor, now=monitor.last_checked_at)

    async def _evaluate_alerts(self, db: Session, monitor: models.Monitor) -> None:
        """Monitor için alert kurallarını değerlendirir ve tetikler"""
        try:
            # Monitor için alert kurallarını al
            alert_rules = crud.get_monitor_alert_rules(db, monitor.id)
            if not alert_rules:
                return
            
            # Alert kurallarını değerlendir
            triggered_alerts = AlertEvaluator.evaluate_alerts(monitor, alert_rules)
            
            # Tetiklenen alert'leri gönder
            for rule, message, details in triggered_alerts:
                if crud.can_trigger_alert(db, rule):
                    await self._send_alert(db, rule, message, details)
                    
        except Exception as e:
            print(f"Alert değerlendirme hatası: {e}")

    async def _send_alert(self, db: Session, alert_rule: models.AlertRule, message: str, details: dict) -> None:
        """Alert'i gönderir ve geçmişe kaydeder"""
        try:
            # Alert'i gönder
            success, error = await AlertSender.send_alert(alert_rule, message, details)
            
            # Geçmişe kaydet
            crud.create_alert_history(
                db=db,
                alert_rule_id=alert_rule.id,
                alert_type=alert_rule.alert_type,
                message=message,
                details=str(details),
                sent_successfully=success,
                error_message=error
            )
            
            # Alert kuralını tetiklendi olarak işaretle
            if success:
                crud.mark_alert_triggered(db, alert_rule)
                
        except Exception as e:
            print(f"Alert gönderme hatası: {e}")


def _db_iter():
    # Basit senkron DB generator'ını async döngü içinde kullanmak için
    db = None
    try:
        from .database import SessionLocal
        db = SessionLocal()
        yield db
    finally:
        if db is not None:
            db.close()

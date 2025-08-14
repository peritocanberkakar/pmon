from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, or_, func
import json

from . import models


# Tenants
def create_tenant(db: Session, name: str, api_key: str) -> models.Tenant:
    tenant = models.Tenant(name=name, api_key=api_key)
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


def get_tenant_by_api_key(db: Session, api_key: str) -> Optional[models.Tenant]:
    return db.scalars(select(models.Tenant).where(models.Tenant.api_key == api_key)).first()


def list_tenants(db: Session) -> List[models.Tenant]:
    return list(db.scalars(select(models.Tenant).order_by(models.Tenant.id)))


# Servers
def create_server(db: Session, tenant_id: int, name: str, host: str) -> models.Server:
    server = models.Server(tenant_id=tenant_id, name=name, host=host)
    db.add(server)
    db.commit()
    db.refresh(server)
    return server


def list_servers(db: Session, tenant_id: int) -> List[models.Server]:
    return list(db.scalars(select(models.Server).where(models.Server.tenant_id == tenant_id).order_by(models.Server.id)))


def get_server(db: Session, tenant_id: int, server_id: int) -> Optional[models.Server]:
    return db.get(models.Server, server_id) if server_id else None


def update_server(db: Session, tenant_id: int, server: models.Server, name: Optional[str], host: Optional[str]) -> models.Server:
    if name is not None:
        server.name = name
    if host is not None:
        server.host = host
    db.commit()
    db.refresh(server)
    return server


def delete_server(db: Session, tenant_id: int, server: models.Server) -> None:
    db.delete(server)
    db.commit()


# PingLocations
def create_ping_location(db: Session, name: str, country: str, city: str, region: Optional[str] = None, 
                        isp: Optional[str] = None, ip_range: Optional[str] = None) -> models.PingLocation:
    location = models.PingLocation(
        name=name,
        country=country,
        city=city,
        region=region,
        isp=isp,
        ip_range=ip_range
    )
    db.add(location)
    db.commit()
    db.refresh(location)
    return location


def list_ping_locations(db: Session, active_only: bool = True) -> List[models.PingLocation]:
    stmt = select(models.PingLocation)
    if active_only:
        stmt = stmt.where(models.PingLocation.is_active.is_(True))
    return list(db.scalars(stmt.order_by(models.PingLocation.id)))


def get_ping_location(db: Session, location_id: int) -> Optional[models.PingLocation]:
    return db.get(models.PingLocation, location_id)


def get_ping_location_by_name(db: Session, name: str) -> Optional[models.PingLocation]:
    return db.scalars(select(models.PingLocation).where(models.PingLocation.name == name)).first()


def update_ping_location(db: Session, location: models.PingLocation, **kwargs) -> models.PingLocation:
    for key, value in kwargs.items():
        if value is not None:
            setattr(location, key, value)
    db.commit()
    db.refresh(location)
    return location


def delete_ping_location(db: Session, location: models.PingLocation) -> None:
    db.delete(location)
    db.commit()


# Services
def create_service(db: Session, tenant_id: Optional[int], name: str, protocol: models.ProtocolEnum, port: int, is_global: bool,
                   location: Optional[str] = None, country: Optional[str] = None, city: Optional[str] = None,
                   ping_location_id: Optional[int] = None) -> models.ServiceDefinition:
    service = models.ServiceDefinition(
        tenant_id=None if is_global else tenant_id,
        name=name,
        protocol=protocol,
        port=port,
        is_global=is_global,
        location=location,
        country=country,
        city=city,
        ping_location_id=ping_location_id
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


def list_services(db: Session, tenant_id: int) -> List[models.ServiceDefinition]:
    stmt = select(models.ServiceDefinition).where(
        or_(models.ServiceDefinition.tenant_id == tenant_id, models.ServiceDefinition.is_global.is_(True))
    ).order_by(models.ServiceDefinition.id)
    return list(db.scalars(stmt))


def get_service(db: Session, tenant_id: int, service_id: int) -> Optional[models.ServiceDefinition]:
    service = db.get(models.ServiceDefinition, service_id)
    if not service:
        return None
    if service.is_global or service.tenant_id == tenant_id:
        return service
    return None


def update_service(db: Session, tenant_id: int, service: models.ServiceDefinition, **kwargs) -> models.ServiceDefinition:
    for key, value in kwargs.items():
        if value is None:
            continue
        setattr(service, key, value)
    db.commit()
    db.refresh(service)
    return service


def delete_service(db: Session, tenant_id: int, service: models.ServiceDefinition) -> None:
    db.delete(service)
    db.commit()


# Monitors
def create_monitor(db: Session, tenant_id: int, server_id: int, service_id: int, interval_seconds: int, enabled: bool) -> models.Monitor:
    monitor = models.Monitor(
        tenant_id=tenant_id,
        server_id=server_id,
        service_id=service_id,
        interval_seconds=interval_seconds,
        enabled=enabled,
        next_run_at=datetime.utcnow(),
    )
    db.add(monitor)
    db.commit()
    db.refresh(monitor)
    return monitor


def list_monitors(db: Session, tenant_id: int) -> List[models.Monitor]:
    return list(db.scalars(select(models.Monitor).where(models.Monitor.tenant_id == tenant_id).order_by(models.Monitor.id)))


def get_monitor(db: Session, tenant_id: int, monitor_id: int) -> Optional[models.Monitor]:
    monitor = db.get(models.Monitor, monitor_id)
    if not monitor:
        return None
    return monitor if monitor.tenant_id == tenant_id else None


def update_monitor(db: Session, tenant_id: int, monitor: models.Monitor, interval_seconds: Optional[int], enabled: Optional[bool]) -> models.Monitor:
    if interval_seconds is not None:
        monitor.interval_seconds = interval_seconds
    if enabled is not None:
        monitor.enabled = enabled
    db.commit()
    db.refresh(monitor)
    return monitor


def delete_monitor(db: Session, tenant_id: int, monitor: models.Monitor) -> None:
    db.delete(monitor)
    db.commit()


def due_monitors(db: Session, now: datetime, limit: int = 50) -> List[models.Monitor]:
    stmt = (
        select(models.Monitor)
        .where(
            models.Monitor.enabled.is_(True),
            models.Monitor.next_run_at.is_not(None),
            models.Monitor.next_run_at <= now,
        )
        .order_by(models.Monitor.next_run_at)
        .limit(limit)
    )
    return list(db.scalars(stmt))


def schedule_next_run(db: Session, monitor: models.Monitor, now: datetime) -> None:
    monitor.next_run_at = now + timedelta(seconds=max(5, monitor.interval_seconds))
    db.commit()


def update_monitor_stats(db: Session, monitor: models.Monitor, success: bool, latency_ms: Optional[float] = None) -> None:
    """Monitor istatistiklerini günceller ve uptime hesaplar"""
    monitor.total_checks += 1
    
    if success:
        monitor.consecutive_successes += 1
        monitor.consecutive_failures = 0
    else:
        monitor.consecutive_failures += 1
        monitor.consecutive_successes = 0
        monitor.total_failures += 1
    
    # Uptime yüzdesini hesapla
    if monitor.total_checks > 0:
        monitor.uptime_percentage = ((monitor.total_checks - monitor.total_failures) / monitor.total_checks) * 100.0
    
    db.commit()


# Alert Channels
def create_alert_channel(db: Session, tenant_id: int, name: str, channel_type: models.AlertChannelTypeEnum, config: dict, enabled: bool) -> models.AlertChannel:
    alert_channel = models.AlertChannel(
        tenant_id=tenant_id,
        name=name,
        channel_type=channel_type,
        config=json.dumps(config),
        enabled=enabled,
    )
    db.add(alert_channel)
    db.commit()
    db.refresh(alert_channel)
    return alert_channel


def list_alert_channels(db: Session, tenant_id: int) -> List[models.AlertChannel]:
    return list(db.scalars(select(models.AlertChannel).where(models.AlertChannel.tenant_id == tenant_id).order_by(models.AlertChannel.id)))


def get_alert_channel(db: Session, tenant_id: int, channel_id: int) -> Optional[models.AlertChannel]:
    channel = db.get(models.AlertChannel, channel_id)
    if not channel:
        return None
    return channel if channel.tenant_id == tenant_id else None


def update_alert_channel(db: Session, tenant_id: int, channel: models.AlertChannel, name: Optional[str], config: Optional[dict], enabled: Optional[bool]) -> models.AlertChannel:
    if name is not None:
        channel.name = name
    if config is not None:
        channel.config = json.dumps(config)
    if enabled is not None:
        channel.enabled = enabled
    db.commit()
    db.refresh(channel)
    return channel


def delete_alert_channel(db: Session, tenant_id: int, channel: models.AlertChannel) -> None:
    db.delete(channel)
    db.commit()


# Alert Rules
def create_alert_rule(db: Session, tenant_id: int, monitor_id: int, alert_channel_id: int, name: str, alert_type: models.AlertTypeEnum, **kwargs) -> models.AlertRule:
    alert_rule = models.AlertRule(
        tenant_id=tenant_id,
        monitor_id=monitor_id,
        alert_channel_id=alert_channel_id,
        name=name,
        alert_type=alert_type,
        consecutive_failures_threshold=kwargs.get('consecutive_failures_threshold'),
        latency_threshold_ms=kwargs.get('latency_threshold_ms'),
        uptime_threshold_percentage=kwargs.get('uptime_threshold_percentage'),
        enabled=kwargs.get('enabled', True),
        cooldown_minutes=kwargs.get('cooldown_minutes', 5),
    )
    db.add(alert_rule)
    db.commit()
    db.refresh(alert_rule)
    return alert_rule


def list_alert_rules(db: Session, tenant_id: int) -> List[models.AlertRule]:
    return list(db.scalars(select(models.AlertRule).where(models.AlertRule.tenant_id == tenant_id).order_by(models.AlertRule.id)))


def get_alert_rule(db: Session, tenant_id: int, rule_id: int) -> Optional[models.AlertRule]:
    rule = db.get(models.AlertRule, rule_id)
    if not rule:
        return None
    return rule if rule.tenant_id == tenant_id else None


def update_alert_rule(db: Session, tenant_id: int, rule: models.AlertRule, **kwargs) -> models.AlertRule:
    for key, value in kwargs.items():
        if value is None:
            continue
        setattr(rule, key, value)
    db.commit()
    db.refresh(rule)
    return rule


def delete_alert_rule(db: Session, tenant_id: int, rule: models.AlertRule) -> None:
    db.delete(rule)
    db.commit()


def get_monitor_alert_rules(db: Session, monitor_id: int) -> List[models.AlertRule]:
    """Bir monitor için tüm alert kurallarını getirir"""
    return list(db.scalars(select(models.AlertRule).where(models.AlertRule.monitor_id == monitor_id).order_by(models.AlertRule.id)))


def can_trigger_alert(db: Session, alert_rule: models.AlertRule) -> bool:
    """Alert kuralının tetiklenip tetiklenemeyeceğini kontrol eder (cooldown)"""
    if not alert_rule.enabled:
        return False
    
    if alert_rule.last_triggered_at is None:
        return True
    
    cooldown_until = alert_rule.last_triggered_at + timedelta(minutes=alert_rule.cooldown_minutes)
    return datetime.utcnow() >= cooldown_until


def mark_alert_triggered(db: Session, alert_rule: models.AlertRule) -> None:
    """Alert kuralının tetiklendiğini işaretler"""
    alert_rule.last_triggered_at = datetime.utcnow()
    db.commit()


# Alert History
def create_alert_history(db: Session, alert_rule_id: int, alert_type: models.AlertTypeEnum, message: str, details: Optional[str] = None, sent_successfully: bool = True, error_message: Optional[str] = None) -> models.AlertHistory:
    alert_history = models.AlertHistory(
        alert_rule_id=alert_rule_id,
        alert_type=alert_type,
        message=message,
        details=details,
        sent_successfully=sent_successfully,
        error_message=error_message,
    )
    db.add(alert_history)
    db.commit()
    db.refresh(alert_history)
    return alert_history


def list_alert_history(db: Session, tenant_id: int, limit: int = 100) -> List[models.AlertHistory]:
    """Tenant için alert geçmişini getirir"""
    stmt = (
        select(models.AlertHistory)
        .join(models.AlertRule)
        .where(models.AlertRule.tenant_id == tenant_id)
        .order_by(models.AlertHistory.sent_at.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt))


# Lease
def try_acquire_lease(db: Session, owner_id: str, ttl_seconds: int = 10) -> bool:
    lease = db.query(models.SchedulerLease).first()
    now = datetime.utcnow()
    if lease is None:
        lease = models.SchedulerLease(owner_id=owner_id, expires_at=now + timedelta(seconds=ttl_seconds))
        db.add(lease)
        db.commit()
        return True
    if lease.owner_id == owner_id or lease.expires_at <= now:
        lease.owner_id = owner_id
        lease.expires_at = now + timedelta(seconds=ttl_seconds)
        db.commit()
        return True
    return False


def renew_lease(db: Session, owner_id: str, ttl_seconds: int = 10) -> bool:
    lease = db.query(models.SchedulerLease).first()
    now = datetime.utcnow()
    if lease and lease.owner_id == owner_id:
        lease.expires_at = now + timedelta(seconds=ttl_seconds)
        db.commit()
        return True
    return False

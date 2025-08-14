import json
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from .. import models


class AlertSender:
    """Alert gönderme işlemlerini yöneten sınıf"""
    
    @staticmethod
    async def send_alert(alert_rule: models.AlertRule, message: str, details: Optional[Dict[str, Any]] = None) -> tuple[bool, Optional[str]]:
        """Alert'i belirtilen kanala gönderir"""
        try:
            config = json.loads(alert_rule.alert_channel.config)
            
            if alert_rule.alert_channel.channel_type == models.AlertChannelTypeEnum.email:
                return await AlertSender._send_email(config, message, details)
            elif alert_rule.alert_channel.channel_type == models.AlertChannelTypeEnum.sms:
                return await AlertSender._send_sms(config, message, details)
            elif alert_rule.alert_channel.channel_type == models.AlertChannelTypeEnum.push:
                return await AlertSender._send_push(config, message, details)
            elif alert_rule.alert_channel.channel_type == models.AlertChannelTypeEnum.webhook:
                return await AlertSender._send_webhook(config, message, details)
            else:
                return False, f"Desteklenmeyen kanal tipi: {alert_rule.alert_channel.channel_type}"
                
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    async def _send_email(config: Dict[str, Any], message: str, details: Optional[Dict[str, Any]] = None) -> tuple[bool, Optional[str]]:
        """E-posta gönderme (simüle edilmiş)"""
        try:
            # Gerçek implementasyonda SMTP kullanılacak
            # Örnek config: {"smtp_server": "smtp.gmail.com", "smtp_port": 587, "username": "user", "password": "pass", "to": "admin@example.com"}
            
            to_email = config.get("to", "admin@example.com")
            subject = config.get("subject", "PMON Alert")
            
            # Simüle edilmiş gönderim
            await asyncio.sleep(0.1)  # Network delay simülasyonu
            
            print(f"[EMAIL] To: {to_email}, Subject: {subject}, Message: {message}")
            return True, None
            
        except Exception as e:
            return False, f"E-posta gönderimi başarısız: {str(e)}"
    
    @staticmethod
    async def _send_sms(config: Dict[str, Any], message: str, details: Optional[Dict[str, Any]] = None) -> tuple[bool, Optional[str]]:
        """SMS gönderme (simüle edilmiş)"""
        try:
            # Gerçek implementasyonda SMS API kullanılacak
            # Örnek config: {"api_key": "key", "phone_number": "+905551234567"}
            
            phone_number = config.get("phone_number", "+905551234567")
            
            # Simüle edilmiş gönderim
            await asyncio.sleep(0.1)  # Network delay simülasyonu
            
            print(f"[SMS] To: {phone_number}, Message: {message}")
            return True, None
            
        except Exception as e:
            return False, f"SMS gönderimi başarısız: {str(e)}"
    
    @staticmethod
    async def _send_push(config: Dict[str, Any], message: str, details: Optional[Dict[str, Any]] = None) -> tuple[bool, Optional[str]]:
        """Push notification gönderme (simüle edilmiş)"""
        try:
            # Gerçek implementasyonda Firebase, OneSignal vb. kullanılacak
            # Örnek config: {"api_key": "key", "device_token": "token"}
            
            device_token = config.get("device_token", "sample_token")
            
            # Simüle edilmiş gönderim
            await asyncio.sleep(0.1)  # Network delay simülasyonu
            
            print(f"[PUSH] To: {device_token}, Message: {message}")
            return True, None
            
        except Exception as e:
            return False, f"Push notification gönderimi başarısız: {str(e)}"
    
    @staticmethod
    async def _send_webhook(config: Dict[str, Any], message: str, details: Optional[Dict[str, Any]] = None) -> tuple[bool, Optional[str]]:
        """Webhook gönderme (simüle edilmiş)"""
        try:
            # Gerçek implementasyonda HTTP client kullanılacak
            # Örnek config: {"url": "https://api.example.com/webhook", "method": "POST", "headers": {"Authorization": "Bearer token"}}
            
            import httpx
            
            url = config.get("url", "https://api.example.com/webhook")
            method = config.get("method", "POST")
            headers = config.get("headers", {})
            
            payload = {
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "details": details or {}
            }
            
            async with httpx.AsyncClient() as client:
                if method.upper() == "POST":
                    response = await client.post(url, json=payload, headers=headers)
                elif method.upper() == "PUT":
                    response = await client.put(url, json=payload, headers=headers)
                else:
                    return False, f"Desteklenmeyen HTTP metodu: {method}"
                
                if response.status_code >= 200 and response.status_code < 300:
                    return True, None
                else:
                    return False, f"Webhook yanıt kodu: {response.status_code}"
                    
        except Exception as e:
            return False, f"Webhook gönderimi başarısız: {str(e)}"


class AlertEvaluator:
    """Alert kurallarını değerlendiren sınıf"""
    
    @staticmethod
    def evaluate_alerts(monitor: models.Monitor, alert_rules: list[models.AlertRule]) -> list[tuple[models.AlertRule, str, dict]]:
        """Monitor durumuna göre alert kurallarını değerlendirir"""
        triggered_alerts = []
        
        for rule in alert_rules:
            if not rule.enabled:
                continue
                
            if rule.alert_type == models.AlertTypeEnum.status_change:
                result = AlertEvaluator._evaluate_status_change(monitor, rule)
            elif rule.alert_type == models.AlertTypeEnum.consecutive_failures:
                result = AlertEvaluator._evaluate_consecutive_failures(monitor, rule)
            elif rule.alert_type == models.AlertTypeEnum.latency_threshold:
                result = AlertEvaluator._evaluate_latency_threshold(monitor, rule)
            elif rule.alert_type == models.AlertTypeEnum.uptime_percentage:
                result = AlertEvaluator._evaluate_uptime_percentage(monitor, rule)
            else:
                continue
                
            if result:
                triggered_alerts.append((rule, result[0], result[1]))
        
        return triggered_alerts
    
    @staticmethod
    def _evaluate_status_change(monitor: models.Monitor, rule: models.AlertRule) -> Optional[tuple[str, dict]]:
        """Status değişikliği alert'ini değerlendirir"""
        if monitor.last_status == "down" and monitor.consecutive_failures == 1:
            message = f"⚠️ {monitor.server.name} ({monitor.server.host}:{monitor.service.port}) servisi DOWN oldu!"
            details = {
                "server": monitor.server.name,
                "host": monitor.server.host,
                "port": monitor.service.port,
                "protocol": monitor.service.protocol.value,
                "status": "down",
                "error": monitor.last_error
            }
            return message, details
        elif monitor.last_status == "up" and monitor.consecutive_successes == 1:
            message = f"✅ {monitor.server.name} ({monitor.server.host}:{monitor.service.port}) servisi UP oldu!"
            details = {
                "server": monitor.server.name,
                "host": monitor.server.host,
                "port": monitor.service.port,
                "protocol": monitor.service.protocol.value,
                "status": "up",
                "latency_ms": monitor.last_latency_ms
            }
            return message, details
        return None
    
    @staticmethod
    def _evaluate_consecutive_failures(monitor: models.Monitor, rule: models.AlertRule) -> Optional[tuple[str, dict]]:
        """Ardışık başarısızlık alert'ini değerlendirir"""
        if not rule.consecutive_failures_threshold:
            return None
            
        if monitor.consecutive_failures == rule.consecutive_failures_threshold:
            message = f"🚨 {monitor.server.name} ({monitor.server.host}:{monitor.service.port}) servisi {monitor.consecutive_failures} kez ardışık başarısız!"
            details = {
                "server": monitor.server.name,
                "host": monitor.server.host,
                "port": monitor.service.port,
                "protocol": monitor.service.protocol.value,
                "consecutive_failures": monitor.consecutive_failures,
                "threshold": rule.consecutive_failures_threshold,
                "error": monitor.last_error
            }
            return message, details
        return None
    
    @staticmethod
    def _evaluate_latency_threshold(monitor: models.Monitor, rule: models.AlertRule) -> Optional[tuple[str, dict]]:
        """Latency eşiği alert'ini değerlendirir"""
        if not rule.latency_threshold_ms or not monitor.last_latency_ms:
            return None
            
        if monitor.last_latency_ms > rule.latency_threshold_ms:
            message = f"🐌 {monitor.server.name} ({monitor.server.host}:{monitor.service.port}) servisi yavaş! Latency: {monitor.last_latency_ms:.1f}ms"
            details = {
                "server": monitor.server.name,
                "host": monitor.server.host,
                "port": monitor.service.port,
                "protocol": monitor.service.protocol.value,
                "current_latency_ms": monitor.last_latency_ms,
                "threshold_ms": rule.latency_threshold_ms
            }
            return message, details
        return None
    
    @staticmethod
    def _evaluate_uptime_percentage(monitor: models.Monitor, rule: models.AlertRule) -> Optional[tuple[str, dict]]:
        """Uptime yüzdesi alert'ini değerlendirir"""
        if not rule.uptime_threshold_percentage or not monitor.uptime_percentage:
            return None
            
        if monitor.uptime_percentage < rule.uptime_threshold_percentage:
            message = f"📉 {monitor.server.name} ({monitor.server.host}:{monitor.service.port}) servisi uptime düşük! %{monitor.uptime_percentage:.1f}"
            details = {
                "server": monitor.server.name,
                "host": monitor.server.host,
                "port": monitor.service.port,
                "protocol": monitor.service.protocol.value,
                "current_uptime_percentage": monitor.uptime_percentage,
                "threshold_percentage": rule.uptime_threshold_percentage,
                "total_checks": monitor.total_checks,
                "total_failures": monitor.total_failures
            }
            return message, details
        return None

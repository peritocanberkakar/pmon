from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ProtocolEnum(str, Enum):
    tcp = "tcp"
    udp = "udp"
    ping = "ping"


class AlertTypeEnum(str, Enum):
    status_change = "status_change"
    consecutive_failures = "consecutive_failures"
    latency_threshold = "latency_threshold"
    uptime_percentage = "uptime_percentage"


class AlertChannelTypeEnum(str, Enum):
    email = "email"
    sms = "sms"
    push = "push"
    webhook = "webhook"


# Tenant
class TenantCreate(BaseModel):
    name: str = Field(
        min_length=3, 
        max_length=200,
        description="Tenant (kiracı) şirket/organizasyon adı. Benzersiz olmalıdır.",
        example="Acme Corporation"
    )


class TenantOut(BaseModel):
    id: int = Field(description="Tenant'ın benzersiz ID'si")
    name: str = Field(description="Tenant adı")
    api_key: str = Field(description="API erişimi için kullanılan benzersiz anahtar. Tüm API isteklerinde X-API-Key header'ında kullanılır.")
    created_at: datetime = Field(description="Tenant'ın oluşturulma tarihi")

    class Config:
        from_attributes = True


# PingLocation
class PingLocationCreate(BaseModel):
    name: str = Field(
        description="Lokasyon için benzersiz isim",
        example="US-East-Virginia"
    )
    country: str = Field(
        description="Ülke kodu (ISO 3166-1 alpha-2)",
        example="US"
    )
    city: str = Field(
        description="Şehir adı",
        example="Virginia"
    )
    region: Optional[str] = Field(
        default=None,
        description="Bölge adı",
        example="East Coast"
    )
    isp: Optional[str] = Field(
        default=None,
        description="İnternet servis sağlayıcısı",
        example="AWS"
    )
    ip_range: Optional[str] = Field(
        default=None,
        description="IP aralığı (CIDR notasyonu)",
        example="52.0.0.0/8"
    )


class PingLocationUpdate(BaseModel):
    name: Optional[str] = Field(
        default=None,
        description="Lokasyon için yeni isim",
        example="US-East-VA"
    )
    country: Optional[str] = Field(
        default=None,
        description="Yeni ülke kodu",
        example="US"
    )
    city: Optional[str] = Field(
        default=None,
        description="Yeni şehir adı",
        example="Richmond"
    )
    region: Optional[str] = Field(
        default=None,
        description="Yeni bölge adı",
        example="Southeast"
    )
    isp: Optional[str] = Field(
        default=None,
        description="Yeni ISP adı",
        example="AWS"
    )
    ip_range: Optional[str] = Field(
        default=None,
        description="Yeni IP aralığı",
        example="52.0.0.0/8"
    )
    is_active: Optional[bool] = Field(
        default=None,
        description="Lokasyonun aktif olup olmadığı",
        example=True
    )


class PingLocationOut(BaseModel):
    id: int = Field(description="Lokasyonun benzersiz ID'si")
    name: str = Field(description="Lokasyon adı")
    country: str = Field(description="Ülke kodu")
    city: str = Field(description="Şehir adı")
    region: Optional[str] = Field(description="Bölge adı")
    isp: Optional[str] = Field(description="ISP adı")
    ip_range: Optional[str] = Field(description="IP aralığı")
    is_active: bool = Field(description="Aktif durumu")
    created_at: datetime = Field(description="Oluşturulma tarihi")

    class Config:
        from_attributes = True


# Server
class ServerCreate(BaseModel):
    name: str = Field(
        description="Sunucu için açıklayıcı isim",
        example="Web Server 1"
    )
    host: str = Field(
        description="Sunucu IP adresi veya hostname",
        example="192.168.1.100"
    )


class ServerUpdate(BaseModel):
    name: Optional[str] = Field(
        default=None,
        description="Sunucu için yeni açıklayıcı isim",
        example="Production Web Server"
    )
    host: Optional[str] = Field(
        default=None,
        description="Yeni sunucu IP adresi veya hostname",
        example="10.0.0.50"
    )


class ServerOut(BaseModel):
    id: int = Field(description="Sunucunun benzersiz ID'si")
    name: str = Field(description="Sunucu adı")
    host: str = Field(description="Sunucu IP adresi veya hostname")
    created_at: datetime = Field(description="Sunucunun oluşturulma tarihi")

    class Config:
        from_attributes = True


# Service
class ServiceCreate(BaseModel):
    name: str = Field(
        description="Servis için açıklayıcı isim",
        example="HTTP Web Service"
    )
    protocol: ProtocolEnum = Field(
        description="Protokol tipi: TCP veya UDP",
        example="tcp"
    )
    port: int = Field(
        description="Port numarası (1-65535)",
        example=80
    )
    is_global: bool = Field(
        default=False,
        description="True ise tüm tenant'lar kullanabilir, False ise sadece oluşturan tenant kullanabilir",
        example=False
    )
    # PING servisleri için lokasyon bilgileri
    location: Optional[str] = Field(
        default=None,
        description="PING servisi için lokasyon adı (örn: 'US-East', 'EU-West')",
        example="US-East"
    )
    country: Optional[str] = Field(
        default=None,
        description="PING servisi için ülke kodu (örn: 'US', 'TR', 'DE')",
        example="US"
    )
    city: Optional[str] = Field(
        default=None,
        description="PING servisi için şehir adı",
        example="New York"
    )


class ServiceUpdate(BaseModel):
    name: Optional[str] = Field(
        default=None,
        description="Servis için yeni açıklayıcı isim",
        example="HTTPS Web Service"
    )
    protocol: Optional[ProtocolEnum] = Field(
        default=None,
        description="Yeni protokol tipi: TCP veya UDP",
        example="tcp"
    )
    port: Optional[int] = Field(
        default=None,
        description="Yeni port numarası (1-65535)",
        example=443
    )
    is_global: Optional[bool] = Field(
        default=None,
        description="Global erişim durumu",
        example=False
    )


class ServiceOut(BaseModel):
    id: int = Field(description="Servisin benzersiz ID'si")
    name: str = Field(description="Servis adı")
    protocol: ProtocolEnum = Field(description="Protokol tipi")
    port: int = Field(description="Port numarası")
    is_global: bool = Field(description="Global erişim durumu")
    # PING servisleri için lokasyon bilgileri
    location: Optional[str] = Field(description="PING servisi lokasyon adı")
    country: Optional[str] = Field(description="PING servisi ülke kodu")
    city: Optional[str] = Field(description="PING servisi şehir adı")
    ping_location: Optional[PingLocationOut] = Field(description="PING servisi lokasyon detayları")
    created_at: datetime = Field(description="Servisin oluşturulma tarihi")

    class Config:
        from_attributes = True


# Monitor
class MonitorCreate(BaseModel):
    server_id: int = Field(
        description="İzlenecek sunucunun ID'si",
        example=1
    )
    service_id: int = Field(
        description="İzlenecek servisin ID'si",
        example=1
    )
    interval_seconds: int = Field(
        ge=5, 
        le=86400, 
        default=60,
        description="İzleme aralığı (saniye). Minimum 5, maksimum 86400 (24 saat)",
        example=30
    )
    enabled: bool = Field(
        default=True,
        description="İzlemenin aktif olup olmadığı",
        example=True
    )


class MonitorUpdate(BaseModel):
    interval_seconds: Optional[int] = Field(
        default=None, 
        ge=5, 
        le=86400,
        description="Yeni izleme aralığı (saniye)",
        example=60
    )
    enabled: Optional[bool] = Field(
        default=None,
        description="İzleme durumu",
        example=False
    )


class MonitorOut(BaseModel):
    id: int = Field(description="Monitor'ün benzersiz ID'si")
    server_id: int = Field(description="İzlenen sunucunun ID'si")
    service_id: int = Field(description="İzlenen servisin ID'si")
    interval_seconds: int = Field(description="İzleme aralığı (saniye)")
    enabled: bool = Field(description="İzleme durumu")
    last_status: Optional[str] = Field(description="Son kontrol sonucu: 'up', 'down' veya null")
    last_error: Optional[str] = Field(description="Son hata mesajı (varsa)")
    last_latency_ms: Optional[float] = Field(description="Son yanıt süresi (milisaniye)")
    last_checked_at: Optional[datetime] = Field(description="Son kontrol zamanı")
    next_run_at: Optional[datetime] = Field(description="Bir sonraki kontrol zamanı")
    consecutive_failures: int = Field(description="Ardışık başarısızlık sayısı")
    consecutive_successes: int = Field(description="Ardışık başarı sayısı")
    total_checks: int = Field(description="Toplam kontrol sayısı")
    total_failures: int = Field(description="Toplam başarısızlık sayısı")
    uptime_percentage: Optional[float] = Field(description="Uptime yüzdesi (0-100)")
    created_at: datetime = Field(description="Monitor'ün oluşturulma tarihi")

    class Config:
        from_attributes = True


class CheckResult(BaseModel):
    status: str = Field(description="Kontrol sonucu: 'up' veya 'down'")
    latency_ms: Optional[float] = Field(description="Yanıt süresi (milisaniye)")
    error: Optional[str] = Field(description="Hata mesajı (varsa)")


# Alert Channel
class AlertChannelCreate(BaseModel):
    name: str = Field(
        description="Alert kanalı için açıklayıcı isim",
        example="Admin Email Alerts"
    )
    channel_type: AlertChannelTypeEnum = Field(
        description="Alert kanal tipi: email, sms, push, webhook",
        example="email"
    )
    config: Dict[str, Any] = Field(
        description="Kanal konfigürasyonu (JSON formatında)",
        example={
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "admin@example.com",
            "password": "app_password",
            "to": "admin@example.com"
        }
    )
    enabled: bool = Field(
        default=True,
        description="Kanalın aktif olup olmadığı",
        example=True
    )


class AlertChannelUpdate(BaseModel):
    name: Optional[str] = Field(
        default=None,
        description="Alert kanalı için yeni isim",
        example="Emergency Email Alerts"
    )
    config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Yeni kanal konfigürasyonu",
        example={
            "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
            "method": "POST"
        }
    )
    enabled: Optional[bool] = Field(
        default=None,
        description="Kanal durumu",
        example=False
    )


class AlertChannelOut(BaseModel):
    id: int = Field(description="Alert kanalının benzersiz ID'si")
    name: str = Field(description="Kanal adı")
    channel_type: AlertChannelTypeEnum = Field(description="Kanal tipi")
    config: Dict[str, Any] = Field(description="Kanal konfigürasyonu")
    enabled: bool = Field(description="Kanal durumu")
    created_at: datetime = Field(description="Kanalın oluşturulma tarihi")

    class Config:
        from_attributes = True


# Alert Rule
class AlertRuleCreate(BaseModel):
    monitor_id: int = Field(
        description="İzlenecek monitor'ün ID'si",
        example=1
    )
    alert_channel_id: int = Field(
        description="Alert gönderilecek kanalın ID'si",
        example=1
    )
    name: str = Field(
        description="Alert kuralı için açıklayıcı isim",
        example="Server Down Alert"
    )
    alert_type: AlertTypeEnum = Field(
        description="Alert tipi: status_change, consecutive_failures, latency_threshold, uptime_percentage",
        example="status_change"
    )
    consecutive_failures_threshold: Optional[int] = Field(
        default=None, 
        ge=1,
        description="Ardışık başarısızlık eşiği (alert_type: consecutive_failures için)",
        example=3
    )
    latency_threshold_ms: Optional[float] = Field(
        default=None, 
        ge=0,
        description="Latency eşiği milisaniye (alert_type: latency_threshold için)",
        example=1000.0
    )
    uptime_threshold_percentage: Optional[float] = Field(
        default=None, 
        ge=0, 
        le=100,
        description="Uptime yüzde eşiği (alert_type: uptime_percentage için)",
        example=95.0
    )
    enabled: bool = Field(
        default=True,
        description="Alert kuralının aktif olup olmadığı",
        example=True
    )
    cooldown_minutes: int = Field(
        ge=1, 
        le=1440, 
        default=5,
        description="Aynı alert için bekleme süresi (dakika). Minimum 1, maksimum 1440 (24 saat)",
        example=10
    )


class AlertRuleUpdate(BaseModel):
    name: Optional[str] = Field(
        default=None,
        description="Alert kuralı için yeni isim",
        example="Critical Server Down Alert"
    )
    alert_channel_id: Optional[int] = Field(
        default=None,
        description="Yeni alert kanalı ID'si",
        example=2
    )
    consecutive_failures_threshold: Optional[int] = Field(
        default=None, 
        ge=1,
        description="Yeni ardışık başarısızlık eşiği",
        example=5
    )
    latency_threshold_ms: Optional[float] = Field(
        default=None, 
        ge=0,
        description="Yeni latency eşiği",
        example=500.0
    )
    uptime_threshold_percentage: Optional[float] = Field(
        default=None, 
        ge=0, 
        le=100,
        description="Yeni uptime eşiği",
        example=90.0
    )
    enabled: Optional[bool] = Field(
        default=None,
        description="Alert kuralı durumu",
        example=False
    )
    cooldown_minutes: Optional[int] = Field(
        default=None, 
        ge=1, 
        le=1440,
        description="Yeni bekleme süresi",
        example=15
    )


class AlertRuleOut(BaseModel):
    id: int = Field(description="Alert kuralının benzersiz ID'si")
    monitor_id: int = Field(description="İzlenen monitor'ün ID'si")
    alert_channel_id: int = Field(description="Alert kanalının ID'si")
    name: str = Field(description="Kural adı")
    alert_type: AlertTypeEnum = Field(description="Alert tipi")
    consecutive_failures_threshold: Optional[int] = Field(description="Ardışık başarısızlık eşiği")
    latency_threshold_ms: Optional[float] = Field(description="Latency eşiği")
    uptime_threshold_percentage: Optional[float] = Field(description="Uptime eşiği")
    enabled: bool = Field(description="Kural durumu")
    cooldown_minutes: int = Field(description="Bekleme süresi (dakika)")
    last_triggered_at: Optional[datetime] = Field(description="Son tetiklenme zamanı")
    created_at: datetime = Field(description="Kuralın oluşturulma tarihi")

    class Config:
        from_attributes = True


# Alert History
class AlertHistoryOut(BaseModel):
    id: int = Field(description="Alert geçmişi kaydının benzersiz ID'si")
    alert_rule_id: int = Field(description="İlgili alert kuralının ID'si")
    alert_type: AlertTypeEnum = Field(description="Alert tipi")
    message: str = Field(description="Gönderilen alert mesajı")
    details: Optional[str] = Field(description="Alert detayları (JSON formatında)")
    sent_at: datetime = Field(description="Alert gönderilme zamanı")
    sent_successfully: bool = Field(description="Alert'in başarıyla gönderilip gönderilmediği")
    error_message: Optional[str] = Field(description="Gönderim hatası (varsa)")

    class Config:
        from_attributes = True

from __future__ import annotations

from datetime import datetime, timedelta
import enum
from sqlalchemy import (
    Integer,
    String,
    DateTime,
    Boolean,
    Enum,
    ForeignKey,
    UniqueConstraint,
    Float,
    Text,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .database import Base


class ProtocolEnum(str, enum.Enum):
    tcp = "tcp"
    udp = "udp"
    ping = "ping"


class AlertTypeEnum(str, enum.Enum):
    status_change = "status_change"  # up -> down veya down -> up
    consecutive_failures = "consecutive_failures"  # ardışık başarısızlıklar
    latency_threshold = "latency_threshold"  # latency eşiği aşımı
    uptime_percentage = "uptime_percentage"  # uptime yüzdesi düşüşü


class AlertChannelTypeEnum(str, enum.Enum):
    email = "email"
    sms = "sms"
    push = "push"
    webhook = "webhook"


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    api_key: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    servers = relationship("Server", back_populates="tenant", cascade="all, delete-orphan")
    services = relationship("ServiceDefinition", back_populates="tenant", cascade="all, delete-orphan")
    monitors = relationship("Monitor", back_populates="tenant", cascade="all, delete-orphan")
    alert_rules = relationship("AlertRule", back_populates="tenant", cascade="all, delete-orphan")
    alert_channels = relationship("AlertChannel", back_populates="tenant", cascade="all, delete-orphan")


class Server(Base):
    __tablename__ = "servers"
    __table_args__ = (
        UniqueConstraint("tenant_id", "host", name="uq_server_tenant_host"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    host: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    tenant = relationship("Tenant", back_populates="servers")
    monitors = relationship("Monitor", back_populates="server", cascade="all, delete-orphan")


class ServiceDefinition(Base):
    __tablename__ = "service_definitions"
    __table_args__ = (
        UniqueConstraint("tenant_id", "protocol", "port", name="uq_service_tenant_proto_port"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int | None] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    protocol: Mapped[ProtocolEnum] = mapped_column(Enum(ProtocolEnum), nullable=False)
    port: Mapped[int] = mapped_column(Integer, nullable=False)
    is_global: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # PING servisleri için lokasyon bilgisi
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str | None] = mapped_column(String(50), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    # PING servisleri için lokasyon referansı
    ping_location_id: Mapped[int | None] = mapped_column(ForeignKey("ping_locations.id", ondelete="SET NULL"), index=True, nullable=True)

    tenant = relationship("Tenant", back_populates="services")
    monitors = relationship("Monitor", back_populates="service", cascade="all, delete-orphan")
    ping_location = relationship("PingLocation", back_populates="ping_services")


class PingLocation(Base):
    """PING servisleri için lokasyon tanımları"""
    __tablename__ = "ping_locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    country: Mapped[str] = mapped_column(String(50), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    isp: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ip_range: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Bu lokasyondan yapılan ping servisleri
    ping_services = relationship("ServiceDefinition", back_populates="ping_location")


class Monitor(Base):
    __tablename__ = "monitors"
    __table_args__ = (
        UniqueConstraint("tenant_id", "server_id", "service_id", name="uq_monitor_tenant_server_service"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    server_id: Mapped[int] = mapped_column(ForeignKey("servers.id", ondelete="CASCADE"), index=True, nullable=False)
    service_id: Mapped[int] = mapped_column(ForeignKey("service_definitions.id", ondelete="CASCADE"), index=True, nullable=False)

    interval_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    last_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    last_error: Mapped[str | None] = mapped_column(String(500), nullable=True)
    last_latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Alert sistemi için ek alanlar
    consecutive_failures: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    consecutive_successes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_checks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_failures: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    uptime_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    tenant = relationship("Tenant", back_populates="monitors")
    server = relationship("Server", back_populates="monitors")
    service = relationship("ServiceDefinition", back_populates="monitors")
    alert_rules = relationship("AlertRule", back_populates="monitor", cascade="all, delete-orphan")


class AlertChannel(Base):
    __tablename__ = "alert_channels"
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_alert_channel_tenant_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    channel_type: Mapped[AlertChannelTypeEnum] = mapped_column(Enum(AlertChannelTypeEnum), nullable=False)
    config: Mapped[str] = mapped_column(Text, nullable=False)  # JSON config (email, webhook URL, etc.)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    tenant = relationship("Tenant", back_populates="alert_channels")
    alert_rules = relationship("AlertRule", back_populates="alert_channel", cascade="all, delete-orphan")


class AlertRule(Base):
    __tablename__ = "alert_rules"
    __table_args__ = (
        UniqueConstraint("monitor_id", "alert_type", name="uq_alert_rule_monitor_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    monitor_id: Mapped[int] = mapped_column(ForeignKey("monitors.id", ondelete="CASCADE"), index=True, nullable=False)
    alert_channel_id: Mapped[int] = mapped_column(ForeignKey("alert_channels.id", ondelete="CASCADE"), index=True, nullable=False)
    
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    alert_type: Mapped[AlertTypeEnum] = mapped_column(Enum(AlertTypeEnum), nullable=False)
    
    # Alert kriterleri
    consecutive_failures_threshold: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_threshold_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    uptime_threshold_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # Alert ayarları
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    cooldown_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=5)  # Aynı alert için bekleme süresi
    last_triggered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    tenant = relationship("Tenant", back_populates="alert_rules")
    monitor = relationship("Monitor", back_populates="alert_rules")
    alert_channel = relationship("AlertChannel", back_populates="alert_rules")
    alert_history = relationship("AlertHistory", back_populates="alert_rule", cascade="all, delete-orphan")


class AlertHistory(Base):
    __tablename__ = "alert_histories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    alert_rule_id: Mapped[int] = mapped_column(ForeignKey("alert_rules.id", ondelete="CASCADE"), index=True, nullable=False)
    
    alert_type: Mapped[AlertTypeEnum] = mapped_column(Enum(AlertTypeEnum), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON details
    
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    sent_successfully: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)

    alert_rule = relationship("AlertRule", back_populates="alert_history")


class SchedulerLease(Base):
    __tablename__ = "scheduler_leases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    @staticmethod
    def default_expiry() -> datetime:
        return datetime.utcnow() + timedelta(seconds=10)

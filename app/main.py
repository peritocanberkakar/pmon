from __future__ import annotations

import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routers import tenants, servers, services, monitors, alert_channels, alert_rules, alert_history, ping_locations
from .scheduler import MonitorScheduler
from .utils.geolocation import PingLocationManager

# Veritabanı tablolarını oluştur
Base.metadata.create_all(bind=engine)

# Varsayılan PING lokasyonlarını oluştur
def create_default_ping_locations():
    from .database import SessionLocal
    from . import crud, models
    
    db = SessionLocal()
    try:
        # Varsayılan lokasyonlar
        default_locations = [
            {"name": "TR-Istanbul", "country": "TR", "city": "Istanbul", "region": "Marmara", "isp": "TurkNet"},
            {"name": "TR-Ankara", "country": "TR", "city": "Ankara", "region": "Central Anatolia", "isp": "TurkNet"},
            {"name": "US-East-Virginia", "country": "US", "city": "Virginia", "region": "East Coast", "isp": "AWS"},
            {"name": "US-West-California", "country": "US", "city": "California", "region": "West Coast", "isp": "AWS"},
            {"name": "EU-West-Ireland", "country": "IE", "city": "Dublin", "region": "Western Europe", "isp": "AWS"},
            {"name": "EU-Central-Frankfurt", "country": "DE", "city": "Frankfurt", "region": "Central Europe", "isp": "AWS"},
            {"name": "Asia-Pacific-Tokyo", "country": "JP", "city": "Tokyo", "region": "Asia Pacific", "isp": "AWS"},
            {"name": "Asia-Pacific-Singapore", "country": "SG", "city": "Singapore", "region": "Asia Pacific", "isp": "AWS"},
        ]
        
        for location_data in default_locations:
            existing = crud.get_ping_location_by_name(db, location_data["name"])
            if not existing:
                crud.create_ping_location(
                    db=db,
                    name=location_data["name"],
                    country=location_data["country"],
                    city=location_data["city"],
                    region=location_data["region"],
                    isp=location_data["isp"]
                )
                print(f"PING lokasyonu oluşturuldu: {location_data['name']}")
    except Exception as e:
        print(f"Varsayılan PING lokasyonları oluşturulurken hata: {e}")
    finally:
        db.close()

# Uygulama başlatılırken varsayılan lokasyonları oluştur
create_default_ping_locations()

# Ücretsiz lokasyonları da ekle
def create_free_ping_locations():
    from .database import SessionLocal
    
    db = SessionLocal()
    try:
        created_locations = PingLocationManager.create_free_locations(db)
        if created_locations:
            print(f"{len(created_locations)} ücretsiz PING lokasyonu eklendi")
    except Exception as e:
        print(f"Ücretsiz PING lokasyonları eklenirken hata: {e}")
    finally:
        db.close()

create_free_ping_locations()

# FastAPI uygulamasını oluştur
app = FastAPI(
    title="PMON - Multi-tenant Port Monitor API",
    description="""
    ## 🚀 PMON - Çok Kiracılı Port İzleme Servisi
    
    FastAPI tabanlı, çok kiracılı (multitenant) TCP/UDP port izleme servisi. 
    Tamamen API tabanlıdır ve Swagger/OpenAPI dokümantasyonu otomatik olarak sunulur.
    
    ### 🎯 Ana Özellikler
    
    - **🔐 Multi-tenant Yapı**: Her tenant'a özgü API anahtarı ile veri izolasyonu
    - **🖥️ Sunucu Yönetimi**: Hostname/IP bazlı sunucu ekleme ve yönetimi
    - **🔧 Servis Tanımları**: TCP/UDP protokol ve port tanımları (tenant'a özel veya global)
    - **📊 İzleme Sistemi**: Sunucu + Servis eşlemesi, özelleştirilebilir kontrol aralıkları
    - **📈 Gelişmiş İstatistikler**: Consecutive failures/successes, uptime yüzdesi, latency ölçümü
    - **🚨 Alert Sistemi**: Çoklu kanal desteği (e-posta, SMS, push, webhook)
    - **⚙️ Alert Kuralları**: Status change, consecutive failures, latency threshold, uptime percentage
    - **⏰ Arka Plan Scheduler**: Periyodik kontrol, tek-leader lease ile çakışmasız çalıştırma
    - **🔍 Anlık Kontrol**: Belirli bir izlemenin manuel tetiklenmesi
    - **🌐 CORS Desteği**: Web/mobil istemciler için hazır
    
    ### 🔑 Kimlik Doğrulama
    
    Tüm API isteklerinde `X-API-Key` header'ında tenant API anahtarını göndermeniz gerekir:
    
    ```
    X-API-Key: your_tenant_api_key_here
    ```
    
    """,
    version="1.2.0",
    contact={
        "name": "PMON Development Team",
        "email": "dev@pmon.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {"name": "tenants", "description": "Tenant yönetimi işlemleri"},
        {"name": "servers", "description": "Sunucu yönetimi işlemleri"},
        {"name": "services", "description": "Servis tanımları yönetimi"},
        {"name": "monitors", "description": "İzleme yönetimi işlemleri"},
        {"name": "alert-channels", "description": "Alert kanal yönetimi"},
        {"name": "alert-rules", "description": "Alert kural yönetimi"},
        {"name": "alert-history", "description": "Alert geçmişi görüntüleme"},
        {"name": "ping-locations", "description": "PING lokasyon yönetimi"},
    ]
)

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Sistem sağlık durumu kontrolü"""
    return {"status": "healthy", "version": "1.2.0"}

# CORS middleware ekle
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Üretimde spesifik origin'ler belirtin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router'ları ekle
app.include_router(tenants.router, prefix="/api")
app.include_router(servers.router, prefix="/api")
app.include_router(services.router, prefix="/api")
app.include_router(monitors.router, prefix="/api")
app.include_router(alert_channels.router, prefix="/api")
app.include_router(alert_rules.router, prefix="/api")
app.include_router(alert_history.router, prefix="/api")
app.include_router(ping_locations.router, prefix="/api")

# Scheduler'ı başlat
scheduler = MonitorScheduler()

@app.on_event("startup")
async def startup_event():
    scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.stop()

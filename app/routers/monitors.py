from __future__ import annotations

import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import crud, models, schemas
from .utils import get_current_tenant
from ..utils.network import check_tcp, check_udp

router = APIRouter(prefix="/monitors", tags=["monitors"])


@router.post("", response_model=schemas.MonitorOut,
    summary="Monitor Oluştur",
    description="Yeni bir izleme (monitor) oluşturur. Belirtilen sunucu ve servis için periyodik kontrol başlatır.",
    responses={
        200: {"description": "Monitor başarıyla oluşturuldu"},
        401: {"description": "Geçersiz API anahtarı"},
        404: {"description": "Sunucu veya servis bulunamadı"},
        422: {"description": "Geçersiz veri formatı"}
    })
def create_monitor(payload: schemas.MonitorCreate, db: Session = Depends(get_db), tenant: models.Tenant = Depends(get_current_tenant)):
    """
    Yeni bir izleme (monitor) oluşturur.
    
    - **server_id**: İzlenecek sunucunun ID'si (mevcut tenant'a ait olmalı)
    - **service_id**: İzlenecek servisin ID'si (mevcut tenant'a ait veya global olmalı)
    - **interval_seconds**: İzleme aralığı (5-86400 saniye arası, varsayılan: 60)
    - **enabled**: İzlemenin aktif olup olmadığı (varsayılan: true)
    
    Monitor oluşturulduktan sonra, sistem otomatik olarak belirtilen aralıklarla 
    sunucunun belirtilen portunu kontrol etmeye başlar.
    """
    # Sunucu kontrolü
    server = crud.get_server(db, server_id=payload.server_id, tenant_id=tenant.id)
    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadı")
    
    # Servis kontrolü
    service = crud.get_service(db, service_id=payload.service_id, tenant_id=tenant.id)
    if not service:
        raise HTTPException(status_code=404, detail="Servis bulunamadı")
    
    return crud.create_monitor(db, tenant_id=tenant.id, server_id=payload.server_id, service_id=payload.service_id, interval_seconds=payload.interval_seconds, enabled=payload.enabled)


@router.get("", response_model=list[schemas.MonitorOut],
    summary="Monitor Listesi",
    description="Mevcut tenant'a ait tüm izlemeleri listeler.",
    responses={
        200: {"description": "Monitor listesi başarıyla döndürüldü"},
        401: {"description": "Geçersiz API anahtarı"}
    })
def list_monitors(db: Session = Depends(get_db), tenant: models.Tenant = Depends(get_current_tenant)):
    """
    Mevcut tenant'a ait tüm izlemeleri listeler.
    
    Her monitor için şu bilgiler döndürülür:
    - Temel bilgiler (ID, sunucu, servis, aralık, durum)
    - Son kontrol sonuçları (durum, hata, latency)
    - İstatistikler (ardışık başarı/başarısızlık, toplam kontroller, uptime)
    - Zaman bilgileri (son kontrol, bir sonraki kontrol)
    """
    return crud.list_monitors(db, tenant_id=tenant.id)


@router.get("/{monitor_id}", response_model=schemas.MonitorOut,
    summary="Monitor Detayı",
    description="Belirtilen monitor'ün detaylarını getirir.",
    responses={
        200: {"description": "Monitor detayları başarıyla döndürüldü"},
        401: {"description": "Geçersiz API anahtarı"},
        404: {"description": "Monitor bulunamadı"}
    })
def get_monitor(monitor_id: int, db: Session = Depends(get_db), tenant: models.Tenant = Depends(get_current_tenant)):
    """
    Belirtilen monitor'ün detaylarını getirir.
    
    - **monitor_id**: Monitor'ün benzersiz ID'si
    
    Sadece mevcut tenant'a ait monitor'lere erişim sağlanır.
    """
    monitor = crud.get_monitor(db, monitor_id=monitor_id, tenant_id=tenant.id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor bulunamadı")
    return monitor


@router.put("/{monitor_id}", response_model=schemas.MonitorOut,
    summary="Monitor Güncelle",
    description="Belirtilen monitor'ün ayarlarını günceller.",
    responses={
        200: {"description": "Monitor başarıyla güncellendi"},
        401: {"description": "Geçersiz API anahtarı"},
        404: {"description": "Monitor bulunamadı"},
        422: {"description": "Geçersiz veri formatı"}
    })
def update_monitor(monitor_id: int, payload: schemas.MonitorUpdate, db: Session = Depends(get_db), tenant: models.Tenant = Depends(get_current_tenant)):
    """
    Belirtilen monitor'ün ayarlarını günceller.
    
    - **monitor_id**: Güncellenecek monitor'ün ID'si
    - **interval_seconds**: Yeni izleme aralığı (opsiyonel, 5-86400 saniye)
    - **enabled**: İzleme durumu (opsiyonel)
    
    Sadece mevcut tenant'a ait monitor'ler güncellenebilir.
    """
    monitor = crud.get_monitor(db, monitor_id=monitor_id, tenant_id=tenant.id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor bulunamadı")
    return crud.update_monitor(db, monitor=monitor, interval_seconds=payload.interval_seconds, enabled=payload.enabled)


@router.delete("/{monitor_id}",
    summary="Monitor Sil",
    description="Belirtilen monitor'ü siler ve izlemeyi durdurur.",
    responses={
        200: {"description": "Monitor başarıyla silindi"},
        401: {"description": "Geçersiz API anahtarı"},
        404: {"description": "Monitor bulunamadı"}
    })
def delete_monitor(monitor_id: int, db: Session = Depends(get_db), tenant: models.Tenant = Depends(get_current_tenant)):
    """
    Belirtilen monitor'ü siler.
    
    - **monitor_id**: Silinecek monitor'ün ID'si
    
    **Dikkat**: Monitor silindiğinde, bu monitor'a ait tüm alert kuralları da silinir.
    Bu işlem geri alınamaz.
    """
    monitor = crud.get_monitor(db, monitor_id=monitor_id, tenant_id=tenant.id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor bulunamadı")
    crud.delete_monitor(db, monitor=monitor)
    return {"message": "Monitor silindi"}


@router.post("/{monitor_id}/check", response_model=schemas.CheckResult,
    summary="Anlık Kontrol",
    description="Belirtilen monitor için anlık port kontrolü yapar.",
    responses={
        200: {"description": "Kontrol sonucu başarıyla döndürüldü"},
        401: {"description": "Geçersiz API anahtarı"},
        404: {"description": "Monitor bulunamadı"}
    })
async def check_monitor(monitor_id: int, db: Session = Depends(get_db), tenant: models.Tenant = Depends(get_current_tenant)):
    """
    Belirtilen monitor için anlık port kontrolü yapar.
    
    - **monitor_id**: Kontrol edilecek monitor'ün ID'si
    
    Bu endpoint, scheduler'ın otomatik kontrolünü beklemeden anlık kontrol yapar.
    Sonuç olarak şunlar döndürülür:
    - **status**: "up" veya "down"
    - **latency_ms**: Yanıt süresi (milisaniye)
    - **error**: Hata mesajı (varsa)
    
    Kontrol sonucu veritabanına kaydedilir ve istatistikler güncellenir.
    """
    monitor = crud.get_monitor(db, monitor_id=monitor_id, tenant_id=tenant.id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor bulunamadı")
    
    # Anlık kontrol yap
    from ..utils.network import check_port
    from .. import models as db_models
    
    server = crud.get_server(db, server_id=monitor.server_id, tenant_id=tenant.id)
    service = crud.get_service(db, service_id=monitor.service_id, tenant_id=tenant.id)
    
    if not server or not service:
        raise HTTPException(status_code=404, detail="Sunucu veya servis bulunamadı")
    
    # PING servisleri için port kullanma
    if service.protocol == db_models.ProtocolEnum.ping:
        success, latency, error = await check_port(server.host, 0, service.protocol.value)
    else:
        success, latency, error = await check_port(server.host, service.port, service.protocol.value)
    
    # Sonuçları güncelle
    status = "up" if success else "down"
    crud.update_monitor_status(db, monitor, status, error, latency)
    crud.update_monitor_stats(db, monitor, success, latency)
    
    return schemas.CheckResult(status=status, latency_ms=latency, error=error)

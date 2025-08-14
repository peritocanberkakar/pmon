from __future__ import annotations

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import crud, models, schemas
from .utils import get_current_tenant

router = APIRouter(prefix="/alert-channels", tags=["alert-channels"])


@router.post("", response_model=schemas.AlertChannelOut,
    summary="Alert Kanalı Ekle",
    description="Yeni bir alert kanalı oluşturur. Bu kanal, alert kuralları tarafından kullanılır.",
    responses={
        200: {"description": "Alert kanalı başarıyla oluşturuldu"},
        401: {"description": "Geçersiz API anahtarı"},
        422: {"description": "Geçersiz veri formatı"}
    })
def create_alert_channel(payload: schemas.AlertChannelCreate, db: Session = Depends(get_db), tenant: models.Tenant = Depends(get_current_tenant)):
    """
    Yeni bir alert kanalı oluşturur.
    
    - **name**: Kanal için açıklayıcı isim (örn: "Admin Email Alerts", "Slack Notifications")
    - **channel_type**: Kanal tipi ("email", "sms", "push", "webhook")
    - **config**: Kanal konfigürasyonu (JSON formatında)
    - **enabled**: Kanalın aktif olup olmadığı (varsayılan: true)
    
    **Konfigürasyon Örnekleri:**
    
    **Email Kanalı:**
    ```json
    {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "username": "admin@example.com",
        "password": "app_password",
        "to": "admin@example.com"
    }
    ```
    
    **Webhook Kanalı:**
    ```json
    {
        "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
        "method": "POST",
        "headers": {"Content-Type": "application/json"}
    }
    ```
    """
    return crud.create_alert_channel(db, tenant_id=tenant.id, name=payload.name, channel_type=payload.channel_type, config=payload.config, enabled=payload.enabled)


@router.get("", response_model=list[schemas.AlertChannelOut],
    summary="Alert Kanalı Listesi",
    description="Mevcut tenant'a ait tüm alert kanallarını listeler.",
    responses={
        200: {"description": "Alert kanalı listesi başarıyla döndürüldü"},
        401: {"description": "Geçersiz API anahtarı"}
    })
def list_alert_channels(db: Session = Depends(get_db), tenant: models.Tenant = Depends(get_current_tenant)):
    """
    Mevcut tenant'a ait tüm alert kanallarını listeler.
    
    Her kanal için şu bilgiler döndürülür:
    - Temel bilgiler (ID, isim, tip, durum)
    - Konfigürasyon detayları
    - Oluşturulma tarihi
    
    **Not**: Konfigürasyon bilgileri (şifreler, API anahtarları vb.) 
    güvenlik nedeniyle maskeleme ile döndürülebilir.
    """
    return crud.list_alert_channels(db, tenant_id=tenant.id)


@router.get("/{channel_id}", response_model=schemas.AlertChannelOut,
    summary="Alert Kanalı Detayı",
    description="Belirtilen alert kanalının detaylarını getirir.",
    responses={
        200: {"description": "Alert kanalı detayları başarıyla döndürüldü"},
        401: {"description": "Geçersiz API anahtarı"},
        404: {"description": "Alert kanalı bulunamadı"}
    })
def get_alert_channel(channel_id: int, db: Session = Depends(get_db), tenant: models.Tenant = Depends(get_current_tenant)):
    """
    Belirtilen alert kanalının detaylarını getirir.
    
    - **channel_id**: Alert kanalının benzersiz ID'si
    
    Sadece mevcut tenant'a ait alert kanallarına erişim sağlanır.
    """
    channel = crud.get_alert_channel(db, channel_id=channel_id, tenant_id=tenant.id)
    if not channel:
        raise HTTPException(status_code=404, detail="Alert kanalı bulunamadı")
    return channel


@router.put("/{channel_id}", response_model=schemas.AlertChannelOut,
    summary="Alert Kanalı Güncelle",
    description="Belirtilen alert kanalının ayarlarını günceller.",
    responses={
        200: {"description": "Alert kanalı başarıyla güncellendi"},
        401: {"description": "Geçersiz API anahtarı"},
        404: {"description": "Alert kanalı bulunamadı"},
        422: {"description": "Geçersiz veri formatı"}
    })
def update_alert_channel(channel_id: int, payload: schemas.AlertChannelUpdate, db: Session = Depends(get_db), tenant: models.Tenant = Depends(get_current_tenant)):
    """
    Belirtilen alert kanalının ayarlarını günceller.
    
    - **channel_id**: Güncellenecek kanalın ID'si
    - **name**: Yeni kanal adı (opsiyonel)
    - **config**: Yeni konfigürasyon (opsiyonel)
    - **enabled**: Kanal durumu (opsiyonel)
    
    Sadece mevcut tenant'a ait alert kanalları güncellenebilir.
    
    **Not**: Konfigürasyon güncellendiğinde, mevcut konfigürasyon tamamen değiştirilir.
    Kısmi güncelleme yapılmaz.
    """
    channel = crud.get_alert_channel(db, channel_id=channel_id, tenant_id=tenant.id)
    if not channel:
        raise HTTPException(status_code=404, detail="Alert kanalı bulunamadı")
    return crud.update_alert_channel(db, channel=channel, name=payload.name, config=payload.config, enabled=payload.enabled)


@router.delete("/{channel_id}",
    summary="Alert Kanalı Sil",
    description="Belirtilen alert kanalını siler. Bu kanalı kullanan alert kuralları da silinir.",
    responses={
        200: {"description": "Alert kanalı başarıyla silindi"},
        401: {"description": "Geçersiz API anahtarı"},
        404: {"description": "Alert kanalı bulunamadı"}
    })
def delete_alert_channel(channel_id: int, db: Session = Depends(get_db), tenant: models.Tenant = Depends(get_current_tenant)):
    """
    Belirtilen alert kanalını siler.
    
    - **channel_id**: Silinecek kanalın ID'si
    
    **Dikkat**: Alert kanalı silindiğinde, bu kanalı kullanan tüm alert kuralları da silinir.
    Bu işlem geri alınamaz.
    
    Sadece mevcut tenant'a ait alert kanalları silinebilir.
    """
    channel = crud.get_alert_channel(db, channel_id=channel_id, tenant_id=tenant.id)
    if not channel:
        raise HTTPException(status_code=404, detail="Alert kanalı bulunamadı")
    crud.delete_alert_channel(db, channel=channel)
    return {"message": "Alert kanalı silindi"}

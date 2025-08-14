from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import crud, models, schemas
from .utils import get_current_tenant

router = APIRouter(prefix="/alert-rules", tags=["alert-rules"])


@router.post("", response_model=schemas.AlertRuleOut,
    summary="Alert Kuralı Ekle",
    description="Yeni bir alert kuralı oluşturur. Bu kural, belirtilen koşullar sağlandığında alert gönderir.",
    responses={
        200: {"description": "Alert kuralı başarıyla oluşturuldu"},
        401: {"description": "Geçersiz API anahtarı"},
        404: {"description": "Monitor veya alert kanalı bulunamadı"},
        422: {"description": "Geçersiz veri formatı"}
    })
def create_alert_rule(payload: schemas.AlertRuleCreate, db: Session = Depends(get_db), tenant: models.Tenant = Depends(get_current_tenant)):
    """
    Yeni bir alert kuralı oluşturur.
    
    - **monitor_id**: İzlenecek monitor'ün ID'si (mevcut tenant'a ait olmalı)
    - **alert_channel_id**: Alert gönderilecek kanalın ID'si (mevcut tenant'a ait olmalı)
    - **name**: Kural için açıklayıcı isim (örn: "Server Down Alert", "High Latency Alert")
    - **alert_type**: Alert tipi ("status_change", "consecutive_failures", "latency_threshold", "uptime_percentage")
    - **consecutive_failures_threshold**: Ardışık başarısızlık eşiği (alert_type: consecutive_failures için)
    - **latency_threshold_ms**: Latency eşiği milisaniye (alert_type: latency_threshold için)
    - **uptime_threshold_percentage**: Uptime yüzde eşiği (alert_type: uptime_percentage için)
    - **enabled**: Kuralın aktif olup olmadığı (varsayılan: true)
    - **cooldown_minutes**: Aynı alert için bekleme süresi (1-1440 dakika, varsayılan: 5)
    
    **Alert Tipleri:**
    
    - **status_change**: Monitor durumu değiştiğinde (up→down veya down→up)
    - **consecutive_failures**: Belirtilen sayıda ardışık başarısızlık olduğunda
    - **latency_threshold**: Yanıt süresi belirtilen eşiği aştığında
    - **uptime_percentage**: Uptime yüzdesi belirtilen eşiğin altına düştüğünde
    """
    # Monitor kontrolü
    monitor = crud.get_monitor(db, monitor_id=payload.monitor_id, tenant_id=tenant.id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor bulunamadı")
    
    # Alert kanalı kontrolü
    channel = crud.get_alert_channel(db, channel_id=payload.alert_channel_id, tenant_id=tenant.id)
    if not channel:
        raise HTTPException(status_code=404, detail="Alert kanalı bulunamadı")
    
    return crud.create_alert_rule(
        db, 
        tenant_id=tenant.id, 
        monitor_id=payload.monitor_id, 
        alert_channel_id=payload.alert_channel_id,
        name=payload.name,
        alert_type=payload.alert_type,
        consecutive_failures_threshold=payload.consecutive_failures_threshold,
        latency_threshold_ms=payload.latency_threshold_ms,
        uptime_threshold_percentage=payload.uptime_threshold_percentage,
        enabled=payload.enabled,
        cooldown_minutes=payload.cooldown_minutes
    )


@router.get("", response_model=list[schemas.AlertRuleOut],
    summary="Alert Kuralı Listesi",
    description="Mevcut tenant'a ait tüm alert kurallarını listeler.",
    responses={
        200: {"description": "Alert kuralı listesi başarıyla döndürüldü"},
        401: {"description": "Geçersiz API anahtarı"}
    })
def list_alert_rules(db: Session = Depends(get_db), tenant: models.Tenant = Depends(get_current_tenant)):
    """
    Mevcut tenant'a ait tüm alert kurallarını listeler.
    
    Her kural için şu bilgiler döndürülür:
    - Temel bilgiler (ID, isim, tip, durum)
    - İlişkili monitor ve alert kanalı ID'leri
    - Eşik değerleri (alert tipine göre)
    - Bekleme süresi ve son tetiklenme zamanı
    - Oluşturulma tarihi
    """
    return crud.list_alert_rules(db, tenant_id=tenant.id)


@router.get("/{rule_id}", response_model=schemas.AlertRuleOut,
    summary="Alert Kuralı Detayı",
    description="Belirtilen alert kuralının detaylarını getirir.",
    responses={
        200: {"description": "Alert kuralı detayları başarıyla döndürüldü"},
        401: {"description": "Geçersiz API anahtarı"},
        404: {"description": "Alert kuralı bulunamadı"}
    })
def get_alert_rule(rule_id: int, db: Session = Depends(get_db), tenant: models.Tenant = Depends(get_current_tenant)):
    """
    Belirtilen alert kuralının detaylarını getirir.
    
    - **rule_id**: Alert kuralının benzersiz ID'si
    
    Sadece mevcut tenant'a ait alert kurallarına erişim sağlanır.
    """
    rule = crud.get_alert_rule(db, rule_id=rule_id, tenant_id=tenant.id)
    if not rule:
        raise HTTPException(status_code=404, detail="Alert kuralı bulunamadı")
    return rule


@router.put("/{rule_id}", response_model=schemas.AlertRuleOut,
    summary="Alert Kuralı Güncelle",
    description="Belirtilen alert kuralının ayarlarını günceller.",
    responses={
        200: {"description": "Alert kuralı başarıyla güncellendi"},
        401: {"description": "Geçersiz API anahtarı"},
        404: {"description": "Alert kuralı veya yeni alert kanalı bulunamadı"},
        422: {"description": "Geçersiz veri formatı"}
    })
def update_alert_rule(rule_id: int, payload: schemas.AlertRuleUpdate, db: Session = Depends(get_db), tenant: models.Tenant = Depends(get_current_tenant)):
    """
    Belirtilen alert kuralının ayarlarını günceller.
    
    - **rule_id**: Güncellenecek kuralın ID'si
    - **name**: Yeni kural adı (opsiyonel)
    - **alert_channel_id**: Yeni alert kanalı ID'si (opsiyonel, mevcut tenant'a ait olmalı)
    - **consecutive_failures_threshold**: Yeni ardışık başarısızlık eşiği (opsiyonel)
    - **latency_threshold_ms**: Yeni latency eşiği (opsiyonel)
    - **uptime_threshold_percentage**: Yeni uptime eşiği (opsiyonel)
    - **enabled**: Kural durumu (opsiyonel)
    - **cooldown_minutes**: Yeni bekleme süresi (opsiyonel, 1-1440 dakika)
    
    Sadece mevcut tenant'a ait alert kuralları güncellenebilir.
    
    **Not**: Yeni alert_channel_id belirtilirse, bu kanalın mevcut tenant'a ait olduğu kontrol edilir.
    """
    rule = crud.get_alert_rule(db, rule_id=rule_id, tenant_id=tenant.id)
    if not rule:
        raise HTTPException(status_code=404, detail="Alert kuralı bulunamadı")
    
    # Yeni alert kanalı kontrolü (eğer belirtilmişse)
    if payload.alert_channel_id is not None:
        channel = crud.get_alert_channel(db, channel_id=payload.alert_channel_id, tenant_id=tenant.id)
        if not channel:
            raise HTTPException(status_code=404, detail="Alert kanalı bulunamadı")
    
    return crud.update_alert_rule(
        db, 
        rule=rule,
        name=payload.name,
        alert_channel_id=payload.alert_channel_id,
        consecutive_failures_threshold=payload.consecutive_failures_threshold,
        latency_threshold_ms=payload.latency_threshold_ms,
        uptime_threshold_percentage=payload.uptime_threshold_percentage,
        enabled=payload.enabled,
        cooldown_minutes=payload.cooldown_minutes
    )


@router.delete("/{rule_id}",
    summary="Alert Kuralı Sil",
    description="Belirtilen alert kuralını siler.",
    responses={
        200: {"description": "Alert kuralı başarıyla silindi"},
        401: {"description": "Geçersiz API anahtarı"},
        404: {"description": "Alert kuralı bulunamadı"}
    })
def delete_alert_rule(rule_id: int, db: Session = Depends(get_db), tenant: models.Tenant = Depends(get_current_tenant)):
    """
    Belirtilen alert kuralını siler.
    
    - **rule_id**: Silinecek kuralın ID'si
    
    **Dikkat**: Alert kuralı silindiğinde, bu kurala ait tüm alert geçmişi de silinir.
    Bu işlem geri alınamaz.
    
    Sadece mevcut tenant'a ait alert kuralları silinebilir.
    """
    rule = crud.get_alert_rule(db, rule_id=rule_id, tenant_id=tenant.id)
    if not rule:
        raise HTTPException(status_code=404, detail="Alert kuralı bulunamadı")
    crud.delete_alert_rule(db, rule=rule)
    return {"message": "Alert kuralı silindi"}

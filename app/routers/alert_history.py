from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from .. import crud, schemas, models
from .utils import get_current_tenant

router = APIRouter(prefix="/alert-history", tags=["alert-history"])


@router.get("", response_model=list[schemas.AlertHistoryOut],
    summary="Alert Geçmişi",
    description="Mevcut tenant'a ait gönderilen alert'lerin geçmişini listeler.",
    responses={
        200: {"description": "Alert geçmişi başarıyla döndürüldü"},
        401: {"description": "Geçersiz API anahtarı"},
        422: {"description": "Geçersiz parametre değeri"}
    })
def list_alert_history(
    limit: int = Query(
        default=100, 
        ge=1, 
        le=1000,
        description="Döndürülecek maksimum kayıt sayısı (1-1000 arası, varsayılan: 100)"
    ),
    db: Session = Depends(get_db),
    tenant: models.Tenant = Depends(get_current_tenant)
):
    """
    Mevcut tenant'a ait gönderilen alert'lerin geçmişini listeler.
    
    - **limit**: Döndürülecek maksimum kayıt sayısı (1-1000 arası, varsayılan: 100)
    
    Sonuçlar en yeni alert'ten en eskiye doğru sıralanır.
    
    Her alert kaydı için şu bilgiler döndürülür:
    - **id**: Alert geçmişi kaydının benzersiz ID'si
    - **alert_rule_id**: İlgili alert kuralının ID'si
    - **alert_type**: Alert tipi (status_change, consecutive_failures, vb.)
    - **message**: Gönderilen alert mesajı
    - **details**: Alert detayları (JSON formatında)
    - **sent_at**: Alert gönderilme zamanı
    - **sent_successfully**: Alert'in başarıyla gönderilip gönderilmediği
    - **error_message**: Gönderim hatası (varsa)
    
    **Not**: Bu endpoint sadece alert geçmişini görüntüler. 
    Alert gönderme işlemi sistem tarafından otomatik olarak yapılır.
    """
    return crud.list_alert_history(db, tenant_id=tenant.id, limit=limit)

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import crud, models, schemas
from .utils import get_current_tenant

router = APIRouter(prefix="/services", tags=["services"])


@router.post("", response_model=schemas.ServiceOut,
    summary="Servis Ekle",
    description="Yeni bir servis tanımı ekler. Servis, belirtilen tenant'a ait olur veya global olabilir.",
    responses={
        200: {"description": "Servis başarıyla oluşturuldu"},
        401: {"description": "Geçersiz API anahtarı"},
        422: {"description": "Geçersiz veri formatı"}
    })
def create_service(payload: schemas.ServiceCreate, db: Session = Depends(get_db), tenant: models.Tenant = Depends(get_current_tenant)):
    """
    Yeni bir servis tanımı ekler.
    
    - **name**: Servis için açıklayıcı isim (örn: "HTTP Web Service", "SIP Service", "PING Service")
    - **protocol**: Protokol tipi ("tcp", "udp" veya "ping")
    - **port**: Port numarası (1-65535 arası, PING için kullanılmaz)
    - **is_global**: True ise tüm tenant'lar kullanabilir, False ise sadece oluşturan tenant kullanabilir
    - **location**: PING servisleri için lokasyon adı (opsiyonel)
    - **country**: PING servisleri için ülke kodu (opsiyonel)
    - **city**: PING servisleri için şehir adı (opsiyonel)
    
    Servis oluşturulduktan sonra, bu servisi sunuculara atayarak izleme başlatabilirsiniz.
    """
    # PING servisleri için lokasyon kontrolü
    ping_location_id = None
    if payload.protocol == models.ProtocolEnum.ping and payload.location:
        ping_location = crud.get_ping_location_by_name(db, payload.location)
        if not ping_location:
            raise HTTPException(status_code=400, detail=f"'{payload.location}' isimli ping lokasyonu bulunamadı")
        ping_location_id = ping_location.id
    
    return crud.create_service(
        db, 
        tenant_id=tenant.id, 
        name=payload.name, 
        protocol=payload.protocol, 
        port=payload.port, 
        is_global=payload.is_global,
        location=payload.location,
        country=payload.country,
        city=payload.city,
        ping_location_id=ping_location_id
    )


@router.get("", response_model=list[schemas.ServiceOut],
    summary="Servis Listesi",
    description="Mevcut tenant'a ait servisleri ve global servisleri listeler.",
    responses={
        200: {"description": "Servis listesi başarıyla döndürüldü"},
        401: {"description": "Geçersiz API anahtarı"}
    })
def list_services(db: Session = Depends(get_db), tenant: models.Tenant = Depends(get_current_tenant)):
    """
    Mevcut tenant'a ait servisleri ve global servisleri listeler.
    
    Listede şunlar bulunur:
    - Mevcut tenant'a ait özel servisler
    - Global olarak tanımlanmış servisler (tüm tenant'lar tarafından kullanılabilir)
    
    Her servis için ID, isim, protokol, port ve global durumu döndürülür.
    """
    return crud.list_services(db, tenant_id=tenant.id)


@router.get("/{service_id}", response_model=schemas.ServiceOut,
    summary="Servis Detayı",
    description="Belirtilen servisin detaylarını getirir.",
    responses={
        200: {"description": "Servis detayları başarıyla döndürüldü"},
        401: {"description": "Geçersiz API anahtarı"},
        404: {"description": "Servis bulunamadı"}
    })
def get_service(service_id: int, db: Session = Depends(get_db), tenant: models.Tenant = Depends(get_current_tenant)):
    """
    Belirtilen servisin detaylarını getirir.
    
    - **service_id**: Servisin benzersiz ID'si
    
    Sadece mevcut tenant'a ait servislere veya global servislere erişim sağlanır.
    """
    service = crud.get_service(db, service_id=service_id, tenant_id=tenant.id)
    if not service:
        raise HTTPException(status_code=404, detail="Servis bulunamadı")
    return service


@router.put("/{service_id}", response_model=schemas.ServiceOut,
    summary="Servis Güncelle",
    description="Belirtilen servisin bilgilerini günceller.",
    responses={
        200: {"description": "Servis başarıyla güncellendi"},
        401: {"description": "Geçersiz API anahtarı"},
        404: {"description": "Servis bulunamadı"},
        422: {"description": "Geçersiz veri formatı"}
    })
def update_service(service_id: int, payload: schemas.ServiceUpdate, db: Session = Depends(get_db), tenant: models.Tenant = Depends(get_current_tenant)):
    """
    Belirtilen servisin bilgilerini günceller.
    
    - **service_id**: Güncellenecek servisin ID'si
    - **name**: Yeni servis adı (opsiyonel)
    - **protocol**: Yeni protokol tipi (opsiyonel)
    - **port**: Yeni port numarası (opsiyonel)
    - **is_global**: Global durumu (opsiyonel)
    
    Sadece mevcut tenant'a ait servisler güncellenebilir.
    Global servisler sadece oluşturan tenant tarafından güncellenebilir.
    """
    service = crud.get_service(db, service_id=service_id, tenant_id=tenant.id)
    if not service:
        raise HTTPException(status_code=404, detail="Servis bulunamadı")
    return crud.update_service(db, service=service, name=payload.name, protocol=payload.protocol, port=payload.port, is_global=payload.is_global)


@router.delete("/{service_id}",
    summary="Servis Sil",
    description="Belirtilen servisi siler. Servise ait tüm izlemeler de silinir.",
    responses={
        200: {"description": "Servis başarıyla silindi"},
        401: {"description": "Geçersiz API anahtarı"},
        404: {"description": "Servis bulunamadı"}
    })
def delete_service(service_id: int, db: Session = Depends(get_db), tenant: models.Tenant = Depends(get_current_tenant)):
    """
    Belirtilen servisi siler.
    
    - **service_id**: Silinecek servisin ID'si
    
    **Dikkat**: Servis silindiğinde, bu servise ait tüm izlemeler de silinir.
    Bu işlem geri alınamaz.
    
    Sadece mevcut tenant'a ait servisler silinebilir.
    Global servisler sadece oluşturan tenant tarafından silinebilir.
    """
    service = crud.get_service(db, service_id=service_id, tenant_id=tenant.id)
    if not service:
        raise HTTPException(status_code=404, detail="Servis bulunamadı")
    crud.delete_service(db, service=service)
    return {"message": "Servis silindi"}

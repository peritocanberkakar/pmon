from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import crud, models, schemas
from .utils import get_current_tenant

router = APIRouter(prefix="/servers", tags=["servers"])


@router.post("", response_model=schemas.ServerOut,
    summary="Sunucu Ekle",
    description="Yeni bir sunucu ekler. Sunucu, belirtilen tenant'a ait olur.",
    responses={
        200: {"description": "Sunucu başarıyla oluşturuldu"},
        401: {"description": "Geçersiz API anahtarı"},
        422: {"description": "Geçersiz veri formatı"}
    })
def create_server(payload: schemas.ServerCreate, db: Session = Depends(get_db), tenant: models.Tenant = Depends(get_current_tenant)):
    """
    Yeni bir sunucu ekler.
    
    - **name**: Sunucu için açıklayıcı isim
    - **host**: Sunucu IP adresi veya hostname (örn: 192.168.1.100, server.example.com)
    
    Sunucu oluşturulduktan sonra, bu sunucuya servisler atayabilir ve izleme başlatabilirsiniz.
    """
    return crud.create_server(db, tenant_id=tenant.id, name=payload.name, host=payload.host)


@router.get("", response_model=list[schemas.ServerOut],
    summary="Sunucu Listesi",
    description="Mevcut tenant'a ait tüm sunucuları listeler.",
    responses={
        200: {"description": "Sunucu listesi başarıyla döndürüldü"},
        401: {"description": "Geçersiz API anahtarı"}
    })
def list_servers(db: Session = Depends(get_db), tenant: models.Tenant = Depends(get_current_tenant)):
    """
    Mevcut tenant'a ait tüm sunucuları listeler.
    
    Her sunucu için ID, isim, host bilgisi ve oluşturulma tarihi döndürülür.
    """
    return crud.list_servers(db, tenant_id=tenant.id)


@router.get("/{server_id}", response_model=schemas.ServerOut,
    summary="Sunucu Detayı",
    description="Belirtilen sunucunun detaylarını getirir.",
    responses={
        200: {"description": "Sunucu detayları başarıyla döndürüldü"},
        401: {"description": "Geçersiz API anahtarı"},
        404: {"description": "Sunucu bulunamadı"}
    })
def get_server(server_id: int, db: Session = Depends(get_db), tenant: models.Tenant = Depends(get_current_tenant)):
    """
    Belirtilen sunucunun detaylarını getirir.
    
    - **server_id**: Sunucunun benzersiz ID'si
    
    Sadece mevcut tenant'a ait sunuculara erişim sağlanır.
    """
    server = crud.get_server(db, server_id=server_id, tenant_id=tenant.id)
    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadı")
    return server


@router.put("/{server_id}", response_model=schemas.ServerOut,
    summary="Sunucu Güncelle",
    description="Belirtilen sunucunun bilgilerini günceller.",
    responses={
        200: {"description": "Sunucu başarıyla güncellendi"},
        401: {"description": "Geçersiz API anahtarı"},
        404: {"description": "Sunucu bulunamadı"},
        422: {"description": "Geçersiz veri formatı"}
    })
def update_server(server_id: int, payload: schemas.ServerUpdate, db: Session = Depends(get_db), tenant: models.Tenant = Depends(get_current_tenant)):
    """
    Belirtilen sunucunun bilgilerini günceller.
    
    - **server_id**: Güncellenecek sunucunun ID'si
    - **name**: Yeni sunucu adı (opsiyonel)
    - **host**: Yeni host bilgisi (opsiyonel)
    
    Sadece mevcut tenant'a ait sunucular güncellenebilir.
    """
    server = crud.get_server(db, server_id=server_id, tenant_id=tenant.id)
    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadı")
    return crud.update_server(db, server=server, name=payload.name, host=payload.host)


@router.delete("/{server_id}",
    summary="Sunucu Sil",
    description="Belirtilen sunucuyu siler. Sunucuya ait tüm izlemeler de silinir.",
    responses={
        200: {"description": "Sunucu başarıyla silindi"},
        401: {"description": "Geçersiz API anahtarı"},
        404: {"description": "Sunucu bulunamadı"}
    })
def delete_server(server_id: int, db: Session = Depends(get_db), tenant: models.Tenant = Depends(get_current_tenant)):
    """
    Belirtilen sunucuyu siler.
    
    - **server_id**: Silinecek sunucunun ID'si
    
    **Dikkat**: Sunucu silindiğinde, bu sunucuya ait tüm izlemeler de silinir.
    Bu işlem geri alınamaz.
    """
    server = crud.get_server(db, server_id=server_id, tenant_id=tenant.id)
    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadı")
    crud.delete_server(db, server=server)
    return {"message": "Sunucu silindi"}

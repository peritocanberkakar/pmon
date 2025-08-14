from __future__ import annotations

import os
import secrets
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from .. import crud, schemas

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.post("", response_model=schemas.TenantOut, 
    summary="Tenant Oluştur",
    description="Yeni bir tenant (kiracı) oluşturur. Her tenant'a benzersiz bir API anahtarı atanır.",
    responses={
        200: {"description": "Tenant başarıyla oluşturuldu"},
        403: {"description": "Tenant oluşturma devre dışı"},
        422: {"description": "Geçersiz veri formatı"}
    })
def create_tenant(payload: schemas.TenantCreate, db: Session = Depends(get_db)):
    """
    Yeni bir tenant oluşturur.
    
    - **name**: Tenant adı (3-200 karakter, benzersiz olmalı)
    - **api_key**: Otomatik olarak oluşturulur ve döndürülür
    - **created_at**: Otomatik olarak oluşturulma zamanı eklenir
    
    Tenant oluşturulduktan sonra dönen API key'i tüm diğer API isteklerinde 
    `X-API-Key` header'ında kullanmanız gerekir.
    """
    if os.getenv("PMON_BOOTSTRAP_TENANT_CREATION", "true").lower() != "true":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant oluşturma devre dışı")
    api_key = secrets.token_hex(24)
    return crud.create_tenant(db, name=payload.name, api_key=api_key)


@router.get("", response_model=list[schemas.TenantOut],
    summary="Tenant Listesi",
    description="Sistemdeki tüm tenant'ları listeler.",
    responses={
        200: {"description": "Tenant listesi başarıyla döndürüldü"}
    })
def list_tenants(db: Session = Depends(get_db)):
    """
    Sistemdeki tüm tenant'ları listeler.
    
    **Not**: Bu endpoint üretim ortamında korunmalıdır. 
    Sadece yönetici erişimi olmalıdır.
    """
    # Basit listeleme — üretimde bu ucu koruyun.
    return crud.list_tenants(db)

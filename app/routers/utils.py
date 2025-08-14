from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from .. import crud, models


async def get_current_tenant(x_api_key: str | None = Header(default=None, alias="X-API-Key"), db: Session = Depends(get_db)) -> models.Tenant:
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-API-Key gerekli")
    tenant = crud.get_tenant_by_api_key(db, x_api_key)
    if not tenant:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz API anahtarı")
    return tenant

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import crud, schemas
from ..utils.geolocation import PingLocationManager, GeolocationService
from .utils import get_current_tenant


router = APIRouter(prefix="/ping-locations", tags=["ping-locations"])


@router.post("", response_model=schemas.PingLocationOut,
    summary="Ping Lokasyonu Oluştur",
    description="Yeni bir ping lokasyonu oluşturur. Bu lokasyonlar farklı ülkelerden ping yapmak için kullanılır.",
    responses={
        200: {"description": "Ping lokasyonu başarıyla oluşturuldu"},
        400: {"description": "Geçersiz veri"},
        422: {"description": "Geçersiz veri formatı"}
    })
def create_ping_location(payload: schemas.PingLocationCreate, db: Session = Depends(get_db)):
    """
    Yeni bir ping lokasyonu oluşturur.

    - **name**: Lokasyon için benzersiz isim (örn: 'US-East-Virginia')
    - **country**: Ülke kodu (ISO 3166-1 alpha-2, örn: 'US', 'TR', 'DE')
    - **city**: Şehir adı
    - **region**: Bölge adı (opsiyonel)
    - **isp**: İnternet servis sağlayıcısı (opsiyonel)
    - **ip_range**: IP aralığı CIDR notasyonu (opsiyonel)

    Bu lokasyonlar daha sonra PING servisleri oluştururken kullanılabilir.
    """
    # Aynı isimde lokasyon var mı kontrol et
    existing = crud.get_ping_location_by_name(db, payload.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"'{payload.name}' isimli lokasyon zaten mevcut"
        )
    
    location = crud.create_ping_location(
        db=db,
        name=payload.name,
        country=payload.country,
        city=payload.city,
        region=payload.region,
        isp=payload.isp,
        ip_range=payload.ip_range
    )
    return location


@router.get("", response_model=List[schemas.PingLocationOut],
    summary="Ping Lokasyonları Listesi",
    description="Mevcut tüm ping lokasyonlarını listeler.",
    responses={
        200: {"description": "Ping lokasyonları başarıyla listelendi"}
    })
def list_ping_locations(active_only: bool = True, db: Session = Depends(get_db)):
    """
    Mevcut ping lokasyonlarını listeler.

    - **active_only**: Sadece aktif lokasyonları listele (varsayılan: true)

    Bu endpoint tüm tenant'lar tarafından kullanılabilir.
    """
    locations = crud.list_ping_locations(db, active_only=active_only)
    return locations


@router.get("/{location_id}", response_model=schemas.PingLocationOut,
    summary="Ping Lokasyonu Detayı",
    description="Belirtilen ID'ye sahip ping lokasyonunun detaylarını getirir.",
    responses={
        200: {"description": "Ping lokasyonu detayları başarıyla getirildi"},
        404: {"description": "Ping lokasyonu bulunamadı"}
    })
def get_ping_location(location_id: int, db: Session = Depends(get_db)):
    """
    Belirtilen ID'ye sahip ping lokasyonunun detaylarını getirir.

    - **location_id**: Lokasyonun benzersiz ID'si
    """
    location = crud.get_ping_location(db, location_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ping lokasyonu bulunamadı"
        )
    return location


@router.put("/{location_id}", response_model=schemas.PingLocationOut,
    summary="Ping Lokasyonu Güncelle",
    description="Belirtilen ID'ye sahip ping lokasyonunu günceller.",
    responses={
        200: {"description": "Ping lokasyonu başarıyla güncellendi"},
        404: {"description": "Ping lokasyonu bulunamadı"},
        400: {"description": "Geçersiz veri"},
        422: {"description": "Geçersiz veri formatı"}
    })
def update_ping_location(location_id: int, payload: schemas.PingLocationUpdate, db: Session = Depends(get_db)):
    """
    Belirtilen ID'ye sahip ping lokasyonunu günceller.

    - **location_id**: Güncellenecek lokasyonun ID'si
    - **payload**: Güncellenecek alanlar (sadece değiştirilecek alanlar gönderilir)
    """
    location = crud.get_ping_location(db, location_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ping lokasyonu bulunamadı"
        )
    
    # İsim değişiyorsa benzersizlik kontrolü
    if payload.name and payload.name != location.name:
        existing = crud.get_ping_location_by_name(db, payload.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"'{payload.name}' isimli lokasyon zaten mevcut"
            )
    
    # Sadece None olmayan değerleri güncelle
    update_data = {k: v for k, v in payload.dict().items() if v is not None}
    location = crud.update_ping_location(db, location, **update_data)
    return location


@router.delete("/{location_id}",
    summary="Ping Lokasyonu Sil",
    description="Belirtilen ID'ye sahip ping lokasyonunu siler.",
    responses={
        204: {"description": "Ping lokasyonu başarıyla silindi"},
        404: {"description": "Ping lokasyonu bulunamadı"}
    })
def delete_ping_location(location_id: int, db: Session = Depends(get_db)):
    """
    Belirtilen ID'ye sahip ping lokasyonunu siler.

    - **location_id**: Silinecek lokasyonun ID'si

    **Uyarı**: Bu lokasyonu kullanan PING servisleri etkilenebilir.
    """
    location = crud.get_ping_location(db, location_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ping lokasyonu bulunamadı"
        )
    
    crud.delete_ping_location(db, location)
    return {"message": "Ping lokasyonu başarıyla silindi"}


@router.post("/from-ip", response_model=schemas.PingLocationOut,
    summary="IP'den Otomatik Lokasyon Oluştur",
    description="IP adresinden otomatik olarak ping lokasyonu oluşturur. Ücretsiz geolocation API'leri kullanır.",
    responses={
        200: {"description": "Lokasyon başarıyla oluşturuldu"},
        400: {"description": "IP adresi geçersiz veya lokasyon bulunamadı"},
        422: {"description": "Geçersiz veri formatı"}
    })
async def create_location_from_ip(ip: str, name: str = None, db: Session = Depends(get_db)):
    """
    IP adresinden otomatik lokasyon oluşturur.

    - **ip**: Lokasyon bilgisi alınacak IP adresi
    - **name**: Lokasyon adı (opsiyonel, otomatik oluşturulur)

    Bu endpoint ücretsiz IP geolocation servislerini kullanarak otomatik lokasyon tespiti yapar.
    """
    location = await PingLocationManager.create_location_from_ip(db, ip, name)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"IP {ip} için lokasyon bilgisi alınamadı"
        )
    return location


@router.post("/free-locations", response_model=List[schemas.PingLocationOut],
    summary="Ücretsiz Lokasyonları Ekle",
    description="Ücretsiz public DNS ve cloud provider lokasyonlarını ekler.",
    responses={
        200: {"description": "Ücretsiz lokasyonlar başarıyla eklendi"},
        400: {"description": "Lokasyon ekleme hatası"}
    })
def add_free_locations(db: Session = Depends(get_db)):
    """
    Ücretsiz lokasyonları veritabanına ekler.

    Bu endpoint şunları ekler:
    - **Public DNS Resolver'lar**: Google DNS, Cloudflare, OpenDNS, Quad9, AdGuard
    - **Cloud Provider'lar**: AWS, Google Cloud, Azure (ücretsiz tier'ları)

    Bu lokasyonlar tüm tenant'lar tarafından kullanılabilir.
    """
    try:
        created_locations = PingLocationManager.create_free_locations(db)
        return created_locations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ücretsiz lokasyonlar eklenirken hata: {str(e)}"
        )


@router.get("/free-locations/list", 
    summary="Ücretsiz Lokasyon Listesi",
    description="Kullanılabilir ücretsiz lokasyonların listesini gösterir.",
    responses={
        200: {"description": "Ücretsiz lokasyon listesi başarıyla getirildi"}
    })
def list_free_locations():
    """
    Kullanılabilir ücretsiz lokasyonların listesini gösterir.

    Bu endpoint henüz veritabanına eklenmemiş ücretsiz lokasyonları listeler.
    """
    dns_locations = PingLocationManager.get_public_dns_locations()
    cloud_locations = PingLocationManager.get_cloud_locations()
    
    return {
        "dns_resolvers": dns_locations,
        "cloud_providers": cloud_locations,
        "total_count": len(dns_locations) + len(cloud_locations)
    }

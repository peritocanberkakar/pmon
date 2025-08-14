"""
IP Geolocation utilities for automatic ping location detection
"""
import asyncio
import httpx
from typing import Optional, Dict, Any
from .. import models, crud
from sqlalchemy.orm import Session


class GeolocationService:
    """IP geolocation için ücretsiz servisler"""
    
    # Ücretsiz IP geolocation API'leri
    FREE_APIS = [
        "http://ip-api.com/json/{ip}",
        "https://ipapi.co/{ip}/json/",
        "https://api.ipgeolocation.io/ipgeo?apiKey=free&ip={ip}",
        "https://freegeoip.app/json/{ip}"
    ]
    
    @staticmethod
    async def get_location_from_ip(ip: str) -> Optional[Dict[str, Any]]:
        """
        IP adresinden lokasyon bilgisi alır
        
        Args:
            ip: IP adresi
            
        Returns:
            Lokasyon bilgileri dict'i veya None
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            for api_url in GeolocationService.FREE_APIS:
                try:
                    url = api_url.format(ip=ip)
                    response = await client.get(url)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Farklı API'lerin farklı response formatları
                        location_data = GeolocationService._parse_location_data(data)
                        if location_data:
                            return location_data
                            
                except Exception as e:
                    print(f"API {api_url} hatası: {e}")
                    continue
                    
        return None
    
    @staticmethod
    def _parse_location_data(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Farklı API'lerin response'larını standart formata çevirir
        """
        try:
            # ip-api.com formatı
            if "countryCode" in data and "city" in data:
                return {
                    "country": data.get("countryCode", ""),
                    "city": data.get("city", ""),
                    "region": data.get("regionName", ""),
                    "isp": data.get("isp", ""),
                    "ip_range": f"{data.get('query', '')}/32"
                }
            
            # ipapi.co formatı
            elif "country_code" in data and "city" in data:
                return {
                    "country": data.get("country_code", ""),
                    "city": data.get("city", ""),
                    "region": data.get("region", ""),
                    "isp": data.get("org", ""),
                    "ip_range": f"{data.get('ip', '')}/32"
                }
            
            # ipgeolocation.io formatı
            elif "country_code2" in data and "city" in data:
                return {
                    "country": data.get("country_code2", ""),
                    "city": data.get("city", ""),
                    "region": data.get("state_prov", ""),
                    "isp": data.get("isp", ""),
                    "ip_range": f"{data.get('ip', '')}/32"
                }
            
            # freegeoip.app formatı
            elif "country_code" in data and "city" in data:
                return {
                    "country": data.get("country_code", ""),
                    "city": data.get("city", ""),
                    "region": data.get("region_code", ""),
                    "isp": data.get("organization", ""),
                    "ip_range": f"{data.get('ip', '')}/32"
                }
                
        except Exception as e:
            print(f"Lokasyon verisi parse hatası: {e}")
            
        return None


class PingLocationManager:
    """Ping lokasyonları için yönetim sınıfı"""
    
    @staticmethod
    async def create_location_from_ip(db: Session, ip: str, name: Optional[str] = None) -> Optional[models.PingLocation]:
        """
        IP adresinden otomatik lokasyon oluşturur
        
        Args:
            db: Database session
            ip: IP adresi
            name: Lokasyon adı (opsiyonel)
            
        Returns:
            Oluşturulan PingLocation veya None
        """
        # Önce IP'den lokasyon bilgisi al
        location_data = await GeolocationService.get_location_from_ip(ip)
        
        if not location_data:
            return None
            
        # Lokasyon adını oluştur
        if not name:
            name = f"{location_data['country']}-{location_data['city']}"
            
        # Mevcut lokasyon var mı kontrol et
        existing = crud.get_ping_location_by_name(db, name)
        if existing:
            return existing
            
        # Yeni lokasyon oluştur
        try:
            location = crud.create_ping_location(
                db=db,
                name=name,
                country=location_data["country"],
                city=location_data["city"],
                region=location_data.get("region"),
                isp=location_data.get("isp"),
                ip_range=location_data.get("ip_range")
            )
            
            print(f"IP {ip} için otomatik lokasyon oluşturuldu: {name}")
            return location
            
        except Exception as e:
            print(f"Lokasyon oluşturma hatası: {e}")
            return None
    
    @staticmethod
    def get_public_dns_locations() -> list[Dict[str, str]]:
        """
        Ücretsiz public DNS resolver'ların listesi
        """
        return [
            {"name": "Google-DNS", "country": "US", "city": "Global", "region": "Worldwide", "isp": "Google", "ip_range": "8.8.8.8/32"},
            {"name": "Cloudflare-DNS", "country": "US", "city": "Global", "region": "Worldwide", "isp": "Cloudflare", "ip_range": "1.1.1.1/32"},
            {"name": "OpenDNS", "country": "US", "city": "Global", "region": "Worldwide", "isp": "Cisco", "ip_range": "208.67.222.222/32"},
            {"name": "Quad9-DNS", "country": "CH", "city": "Zurich", "region": "Europe", "isp": "Quad9", "ip_range": "9.9.9.9/32"},
            {"name": "AdGuard-DNS", "country": "CY", "city": "Limassol", "region": "Europe", "isp": "AdGuard", "ip_range": "94.140.14.14/32"},
        ]
    
    @staticmethod
    def get_cloud_locations() -> list[Dict[str, str]]:
        """
        Ücretsiz cloud provider lokasyonları
        """
        return [
            # AWS Free Tier
            {"name": "AWS-US-East", "country": "US", "city": "Virginia", "region": "East Coast", "isp": "AWS", "ip_range": "52.0.0.0/8"},
            {"name": "AWS-US-West", "country": "US", "city": "California", "region": "West Coast", "isp": "AWS", "ip_range": "54.0.0.0/8"},
            {"name": "AWS-EU-West", "country": "IE", "city": "Dublin", "region": "Western Europe", "isp": "AWS", "ip_range": "52.30.0.0/16"},
            {"name": "AWS-EU-Central", "country": "DE", "city": "Frankfurt", "region": "Central Europe", "isp": "AWS", "ip_range": "52.28.0.0/16"},
            {"name": "AWS-Asia-Pacific", "country": "JP", "city": "Tokyo", "region": "Asia Pacific", "isp": "AWS", "ip_range": "52.192.0.0/16"},
            
            # Google Cloud Free Tier
            {"name": "GCP-US-East", "country": "US", "city": "South Carolina", "region": "East Coast", "isp": "Google Cloud", "ip_range": "35.0.0.0/8"},
            {"name": "GCP-US-West", "country": "US", "city": "Oregon", "region": "West Coast", "isp": "Google Cloud", "ip_range": "34.0.0.0/8"},
            {"name": "GCP-EU-West", "country": "BE", "city": "Brussels", "region": "Western Europe", "isp": "Google Cloud", "ip_range": "35.195.0.0/16"},
            
            # Azure Free Tier
            {"name": "Azure-US-East", "country": "US", "city": "Virginia", "region": "East Coast", "isp": "Microsoft Azure", "ip_range": "20.0.0.0/8"},
            {"name": "Azure-EU-West", "country": "NL", "city": "Amsterdam", "region": "Western Europe", "isp": "Microsoft Azure", "ip_range": "20.36.0.0/16"},
        ]
    
    @staticmethod
    def create_free_locations(db: Session) -> list[models.PingLocation]:
        """
        Ücretsiz lokasyonları veritabanına ekler
        """
        created_locations = []
        
        # Public DNS lokasyonları
        for location_data in PingLocationManager.get_public_dns_locations():
            existing = crud.get_ping_location_by_name(db, location_data["name"])
            if not existing:
                try:
                    location = crud.create_ping_location(
                        db=db,
                        name=location_data["name"],
                        country=location_data["country"],
                        city=location_data["city"],
                        region=location_data["region"],
                        isp=location_data["isp"],
                        ip_range=location_data["ip_range"]
                    )
                    created_locations.append(location)
                    print(f"Ücretsiz DNS lokasyonu eklendi: {location_data['name']}")
                except Exception as e:
                    print(f"DNS lokasyonu ekleme hatası: {e}")
        
        # Cloud lokasyonları
        for location_data in PingLocationManager.get_cloud_locations():
            existing = crud.get_ping_location_by_name(db, location_data["name"])
            if not existing:
                try:
                    location = crud.create_ping_location(
                        db=db,
                        name=location_data["name"],
                        country=location_data["country"],
                        city=location_data["city"],
                        region=location_data["region"],
                        isp=location_data["isp"],
                        ip_range=location_data["ip_range"]
                    )
                    created_locations.append(location)
                    print(f"Ücretsiz Cloud lokasyonu eklendi: {location_data['name']}")
                except Exception as e:
                    print(f"Cloud lokasyonu ekleme hatası: {e}")
        
        return created_locations

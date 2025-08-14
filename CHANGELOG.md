# Changelog

Bu dosya PMON projesinin tüm değişikliklerini kronolojik sırayla takip eder.

## [1.2.0] - 2024-12-19

### 🎉 Ücretsiz Lokasyon Servisleri

#### Eklenenler
- **GeolocationService**: IP geolocation için ücretsiz API'ler (ip-api.com, ipapi.co, ipgeolocation.io, freegeoip.app)
- **PingLocationManager**: Ücretsiz lokasyon yönetimi ve otomatik lokasyon oluşturma
- **Public DNS Resolver'lar**: Google DNS, Cloudflare, OpenDNS, Quad9, AdGuard lokasyonları
- **Cloud Provider Lokasyonları**: AWS, Google Cloud, Azure ücretsiz tier lokasyonları
- **IP'den Otomatik Lokasyon**: IP adresinden otomatik lokasyon tespiti ve oluşturma
- **Yeni API Endpoint'leri**: 
  - `POST /api/ping-locations/from-ip` - IP'den otomatik lokasyon oluşturma
  - `POST /api/ping-locations/free-locations` - Ücretsiz lokasyonları ekleme
  - `GET /api/ping-locations/free-locations/list` - Ücretsiz lokasyon listesi

#### Değiştirilenler
- **Bootstrap**: Uygulama başlatılırken otomatik ücretsiz lokasyon ekleme
- **Versiyon**: 1.1.0'dan 1.2.0'a güncellendi

#### Teknik Detaylar
- **Yeni Modül**: `app/utils/geolocation.py` - IP geolocation ve lokasyon yönetimi
- **API Entegrasyonu**: Çoklu ücretsiz geolocation API desteği
- **Hata Yönetimi**: API hatalarında fallback mekanizması
- **Dokümantasyon**: Yeni endpoint'ler için detaylı API dokümantasyonu

#### Test Senaryosu
- ✅ Ücretsiz lokasyonları ekleme
- ✅ IP'den otomatik lokasyon oluşturma (8.8.8.8)
- ✅ Ücretsiz lokasyon listesi görüntüleme

---

## [1.1.0] - 2024-12-19

### 🎉 PING Servisi ve Çoklu Lokasyon Desteği

#### Eklenenler
- **PING Protokolü**: TCP/UDP yanında PING protokolü desteği eklendi
- **PingLocation Modeli**: Ping lokasyonları için yeni veritabanı modeli
- **Ping Lokasyon CRUD**: Lokasyon yönetimi için tam CRUD işlemleri
- **Ping Lokasyon Router**: `/api/ping-locations` endpoint'leri
- **Varsayılan Lokasyonlar**: TR, US, EU, Asia-Pacific bölgeleri için hazır lokasyonlar
- **Platform Desteği**: Windows ve Linux/Mac için ping komutu optimizasyonu
- **Latency Ölçümü**: Ping çıktısından otomatik latency hesaplama

#### Değiştirilenler
- **ProtocolEnum**: PING protokolü eklendi
- **ServiceDefinition Modeli**: Lokasyon bilgileri ve ping_location_id eklendi
- **ServiceCreate/Update/Out Schemas**: PING servisleri için lokasyon alanları eklendi
- **Network Utils**: check_ping ve check_port fonksiyonları eklendi
- **Scheduler**: PING protokolü desteği eklendi
- **Monitors Router**: PING servisleri için async check_monitor fonksiyonu

#### Teknik Detaylar
- **Veritabanı**: PingLocation tablosu ve ServiceDefinition'a yeni alanlar eklendi
- **API**: 5 yeni endpoint eklendi (ping-locations)
- **Dokümantasyon**: PING servisleri için detaylı API dokümantasyonu
- **Bootstrap**: Uygulama başlatılırken varsayılan lokasyonlar oluşturuluyor

#### Test Senaryosu
- ✅ Ping lokasyonu oluşturma
- ✅ PING servisi tanımlama (perito.com.tr)
- ✅ Monitor oluşturma
- ✅ Anlık ping kontrolü

---

## [1.0.0] - 2024-12-19

### 🎉 İlk Sürüm - Production Ready

#### Eklenenler
- **Multi-tenant yapı**: Her tenant için benzersiz API anahtarı ile veri izolasyonu
- **Sunucu yönetimi**: Hostname/IP bazlı sunucu CRUD işlemleri
- **Servis tanımları**: TCP/UDP protokol ve port tanımları
- **İzleme sistemi**: Sunucu + Servis eşlemesi ile periyodik kontrol
- **Alert sistemi**: E-posta, SMS, push, webhook kanalları
- **Alert kuralları**: Status change, consecutive failures, latency threshold, uptime percentage
- **Gelişmiş istatistikler**: Consecutive failures/successes, uptime yüzdesi, latency
- **Arka plan scheduler**: Periyodik kontrol ve leader election
- **API dokümantasyonu**: Detaylı Swagger/OpenAPI dokümantasyonu
- **Docker desteği**: Containerized deployment
- **CORS desteği**: Web/mobil istemciler için hazır

#### Teknik Özellikler
- FastAPI framework ile modern API
- SQLAlchemy ORM ile güçlü veritabanı yönetimi
- SQLite varsayılan, PostgreSQL hazır
- Pydantic ile güçlü veri doğrulama
- Asenkron işlemler ve background tasks
- API Key authentication
- Tenant bazlı veri izolasyonu

#### API Endpoints
- **Tenant Yönetimi**: 2 endpoint
- **Sunucu Yönetimi**: 5 endpoint
- **Servis Yönetimi**: 5 endpoint
- **İzleme Yönetimi**: 6 endpoint
- **Alert Kanalları**: 4 endpoint
- **Alert Kuralları**: 4 endpoint
- **Alert Geçmişi**: 1 endpoint

#### Test Senaryosu
- ✅ Tenant oluşturma
- ✅ Sunucu ekleme (217.116.197.152)
- ✅ Servis tanımlama (UDP 5060)
- ✅ Monitor oluşturma
- ✅ Anlık port kontrolü

#### Dosya Yapısı
```
app/
├── main.py              # FastAPI uygulaması
├── database.py          # Veritabanı konfigürasyonu
├── models.py            # SQLAlchemy modelleri
├── schemas.py           # Pydantic şemaları
├── crud.py              # CRUD işlemleri
├── scheduler.py         # Arka plan scheduler
├── utils/
│   ├── network.py       # Port kontrol fonksiyonları
│   └── alert_sender.py  # Alert gönderme ve değerlendirme
└── routers/
    ├── tenants.py       # Tenant yönetimi
    ├── servers.py       # Sunucu yönetimi
    ├── services.py      # Servis yönetimi
    ├── monitors.py      # İzleme yönetimi
    ├── alert_channels.py # Alert kanal yönetimi
    ├── alert_rules.py   # Alert kural yönetimi
    └── alert_history.py # Alert geçmişi
```

#### Konfigürasyon
- Environment variables ile esnek konfigürasyon
- Docker ve docker-compose desteği
- Minimum bağımlılık prensibi
- DevOps friendly yapı

---

## Gelecek Versiyonlar

### [1.1.0] - Planlanan
- Webhook entegrasyonları (Slack, Discord, Teams)
- Grafik dashboard ve trend analizi
- Bildirim şablonları
- Bakım modu

### [1.2.0] - Planlanan
- SSL sertifika izleme
- HTTP/HTTPS izleme
- DNS izleme
- Ping izleme

### [2.0.0] - Planlanan
- Web arayüzü
- Mobil uygulama
- Gelişmiş raporlama
- API rate limiting

---

## Versiyonlama Kuralları

Bu proje [Semantic Versioning](https://semver.org/) kurallarını takip eder:

- **MAJOR.MINOR.PATCH** formatında
- **MAJOR**: Geriye uyumsuz API değişiklikleri
- **MINOR**: Geriye uyumlu yeni özellikler
- **PATCH**: Geriye uyumlu hata düzeltmeleri

### Değişiklik Kategorileri

#### 🎉 Eklenenler
- Yeni özellikler
- Yeni API endpoint'leri
- Yeni konfigürasyon seçenekleri

#### 🔧 Değiştirilenler
- Mevcut özelliklerde iyileştirmeler
- Performans optimizasyonları
- API davranış değişiklikleri

#### 🐛 Düzeltilenler
- Bug fixes
- Güvenlik açıkları
- Veritabanı sorunları

#### 🗑️ Kaldırılanlar
- Artık kullanılmayan özellikler
- Deprecated API endpoint'leri
- Eski konfigürasyon seçenekleri

---

**Not**: Bu changelog dosyası her yeni versiyon ile güncellenir. Değişiklikler kronolojik sırayla (en yeni en üstte) listelenir.

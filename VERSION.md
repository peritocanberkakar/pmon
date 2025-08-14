# PMON - Versiyon Geçmişi

Bu dosya PMON (Port Monitor) projesinin versiyon geçmişini ve değişiklik notlarını içerir.

## Versiyon 1.2.0 - Ücretsiz Lokasyon Servisleri (2024-12-19)

### 🎉 Yeni Özellikler

#### 🌍 Ücretsiz Lokasyon Servisleri
- **IP Geolocation API'leri**: Ücretsiz IP geolocation servisleri ile otomatik lokasyon tespiti
- **Public DNS Resolver'lar**: Google DNS, Cloudflare, OpenDNS, Quad9, AdGuard
- **Cloud Provider Lokasyonları**: AWS, Google Cloud, Azure ücretsiz tier'ları
- **Otomatik Lokasyon Oluşturma**: IP adresinden otomatik lokasyon tespiti

#### 🔧 Teknik İyileştirmeler
- **GeolocationService**: Çoklu API desteği ile IP lokasyon tespiti
- **PingLocationManager**: Ücretsiz lokasyon yönetimi
- **API Endpoint'leri**: IP'den lokasyon oluşturma ve ücretsiz lokasyon ekleme
- **Bootstrap**: Uygulama başlatılırken otomatik ücretsiz lokasyon ekleme

### 🚀 API Endpoints

#### Yeni Ping Lokasyon Endpoint'leri
- `POST /api/ping-locations/from-ip` - IP'den otomatik lokasyon oluşturma
- `POST /api/ping-locations/free-locations` - Ücretsiz lokasyonları ekleme
- `GET /api/ping-locations/free-locations/list` - Ücretsiz lokasyon listesi

### 🧪 Test Senaryoları

#### Ücretsiz Lokasyon Test Senaryosu
1. **Ücretsiz Lokasyonları Ekleme**: Public DNS ve cloud provider lokasyonları eklendi
2. **IP'den Lokasyon Oluşturma**: 8.8.8.8 IP'sinden otomatik lokasyon oluşturuldu
3. **Lokasyon Listesi**: Tüm ücretsiz lokasyonlar listelendi

### 📋 Gelecek Versiyonlar

#### Versiyon 1.3.0 (Planlanan)
- **SSL Sertifika İzleme**: SSL sertifika süre kontrolü
- **HTTP/HTTPS İzleme**: Web servisleri için HTTP durum kontrolü
- **DNS İzleme**: DNS çözümleme kontrolü
- **Gelişmiş PING**: Traceroute ve path analizi

#### Versiyon 2.0.0 (Planlanan)
- **Web Arayüzü**: Tam özellikli web dashboard
- **Mobil Uygulama**: iOS/Android mobil uygulaması
- **Gelişmiş Raporlama**: PDF/Excel rapor export
- **API Rate Limiting**: Gelişmiş API güvenlik

---

## Versiyon 1.1.0 - PING Servisi ve Çoklu Lokasyon Desteği (2024-12-19)

### 🎉 Yeni Özellikler

#### 🌍 PING Servisi
- **PING Protokolü**: TCP/UDP yanında PING protokolü desteği
- **Çoklu Lokasyon**: Farklı ülkelerden ping yapabilme özelliği
- **Lokasyon Yönetimi**: Ping lokasyonlarının CRUD işlemleri
- **Varsayılan Lokasyonlar**: TR, US, EU, Asia-Pacific bölgeleri için hazır lokasyonlar

#### 📍 Ping Lokasyon Sistemi
- **Lokasyon Tanımları**: Ülke, şehir, bölge, ISP bilgileri
- **Global Erişim**: Tüm tenant'lar tarafından kullanılabilir lokasyonlar
- **Aktif/Pasif Durumu**: Lokasyonları geçici olarak devre dışı bırakma
- **IP Aralığı**: CIDR notasyonu ile IP aralığı tanımlama

#### 🔧 Teknik İyileştirmeler
- **Platform Desteği**: Windows ve Linux/Mac için ping komutu optimizasyonu
- **Latency Ölçümü**: Ping çıktısından otomatik latency hesaplama
- **Hata Yönetimi**: Ping timeout ve bağlantı hatalarının detaylı raporlanması
- **Asenkron İşlemler**: Ping kontrollerinin asenkron yapılması

### 🚀 API Endpoints

#### Ping Lokasyon Yönetimi
- `POST /api/ping-locations` - Ping lokasyonu oluşturma
- `GET /api/ping-locations` - Ping lokasyonları listesi
- `GET /api/ping-locations/{location_id}` - Ping lokasyonu detayı
- `PUT /api/ping-locations/{location_id}` - Ping lokasyonu güncelleme
- `DELETE /api/ping-locations/{location_id}` - Ping lokasyonu silme

#### Servis Yönetimi (Güncellenmiş)
- PING protokolü desteği eklendi
- Lokasyon bilgileri eklendi
- Ping lokasyonu referansı eklendi

### 🧪 Test Senaryoları

#### PING Servisi Test Senaryosu
1. **Ping Lokasyonu Oluşturma**: Yeni bir ping lokasyonu oluşturuldu
2. **PING Servisi Tanımlama**: perito.com.tr için PING servisi tanımlandı
3. **Monitor Oluşturma**: PING servisi ile monitor oluşturuldu
4. **Anlık Kontrol**: Manuel ping kontrolü başarıyla gerçekleştirildi

### 📋 Gelecek Versiyonlar

#### Versiyon 1.2.0 (Planlanan)
- **SSL Sertifika İzleme**: SSL sertifika süre kontrolü
- **HTTP/HTTPS İzleme**: Web servisleri için HTTP durum kontrolü
- **DNS İzleme**: DNS çözümleme kontrolü
- **Gelişmiş PING**: Traceroute ve path analizi

#### Versiyon 2.0.0 (Planlanan)
- **Web Arayüzü**: Tam özellikli web dashboard
- **Mobil Uygulama**: iOS/Android mobil uygulaması
- **Gelişmiş Raporlama**: PDF/Excel rapor export
- **API Rate Limiting**: Gelişmiş API güvenlik

---

## Versiyon 1.0.0 - İlk Sürüm (2024-12-19)

### 🎉 Yeni Özellikler

#### 🔐 Multi-tenant Yapı
- **Tenant Yönetimi**: Her tenant için benzersiz API anahtarı ile veri izolasyonu
- **API Key Authentication**: `X-API-Key` header ile güvenli erişim
- **Veri İzolasyonu**: Her tenant'ın kendi sunucuları, servisleri ve izlemeleri

#### 🖥️ Sunucu Yönetimi
- **Sunucu Ekleme**: Hostname/IP bazlı sunucu tanımlama
- **Sunucu Güncelleme**: Mevcut sunucu bilgilerini düzenleme
- **Sunucu Silme**: Artık kullanılmayan sunucuları kaldırma
- **Sunucu Listeleme**: Tenant'a ait tüm sunucuları görüntüleme

#### 🔧 Servis Tanımları
- **Protokol Desteği**: TCP ve UDP protokol desteği
- **Port Tanımları**: Port numarası ve servis adı ile tanımlama
- **Global Servisler**: Tüm tenant'lar tarafından kullanılabilir servisler
- **Tenant Özel Servisler**: Sadece belirli tenant'a ait servisler

#### 📊 İzleme Sistemi
- **Monitor Oluşturma**: Sunucu + Servis eşlemesi ile izleme başlatma
- **Periyodik Kontrol**: Özelleştirilebilir kontrol aralıkları (dakika cinsinden)
- **Anlık Kontrol**: Manuel port kontrolü ile anında durum sorgulama
- **Durum Takibi**: Online/Offline durumu ve son kontrol zamanı

#### 🚨 Alert Sistemi
- **Alert Kanalları**: E-posta, SMS, Push, Webhook desteği
- **Alert Kuralları**: Status change, consecutive failures, latency threshold, uptime percentage
- **Alert Geçmişi**: Gönderilen alert'lerin detaylı log'u
- **Cooldown Mekanizması**: Alert spam'ini önlemek için bekleme süresi

#### 📈 Gelişmiş İstatistikler
- **Consecutive Failures/Successes**: Ardışık başarı/başarısızlık sayıları
- **Uptime Yüzdesi**: Otomatik hesaplanan uptime oranı
- **Latency Ölçümü**: Yanıt süresi takibi
- **Toplam İstatistikler**: Toplam kontrol ve başarısızlık sayıları

#### ⚙️ Arka Plan Scheduler
- **Periyodik Kontrol**: Otomatik port kontrolü
- **Leader Election**: Lease mekanizması ile tek scheduler çalıştırma
- **Çoklu Instance Desteği**: Birden fazla PMON instance'ı çalıştırma
- **Hata Toleransı**: Scheduler kesintilerinde otomatik devam

#### 🌐 API ve Dokümantasyon
- **FastAPI Framework**: Modern, hızlı ve otomatik dokümantasyon
- **Swagger/OpenAPI**: Otomatik API dokümantasyonu
- **Detaylı Açıklamalar**: Her endpoint ve alan için açıklayıcı dokümantasyon
- **CORS Desteği**: Web/mobil istemciler için hazır

### 🔧 Teknik Özellikler

#### Veritabanı
- **SQLAlchemy ORM**: Güçlü veritabanı yönetimi
- **SQLite Varsayılan**: Kolay kurulum için SQLite desteği
- **PostgreSQL Hazır**: Üretim ortamı için PostgreSQL desteği
- **Migration Sistemi**: Otomatik tablo oluşturma

#### Güvenlik
- **API Key Authentication**: Güvenli tenant erişimi
- **Veri İzolasyonu**: Tenant bazlı veri ayrımı
- **Input Validation**: Pydantic ile güçlü veri doğrulama

#### Performans
- **Asenkron İşlemler**: FastAPI ile yüksek performans
- **Background Tasks**: Arka plan scheduler ile kesintisiz izleme
- **Connection Pooling**: Veritabanı bağlantı optimizasyonu

### 📦 Kurulum ve Deployment

#### Docker Desteği
- **Dockerfile**: Containerized deployment
- **Docker Compose**: Kolay çoklu servis deployment
- **Environment Variables**: Konfigürasyon yönetimi

#### Minimum Bağımlılık
- **Hafif Dependencies**: Sadece gerekli paketler
- **Kolay Kurulum**: `pip install -r requirements.txt`
- **DevOps Friendly**: Minimal setup gereksinimleri

### 🚀 API Endpoints

#### Tenant Yönetimi
- `POST /api/tenants` - Yeni tenant oluşturma
- `GET /api/tenants` - Tenant listesi

#### Sunucu Yönetimi
- `POST /api/servers` - Sunucu ekleme
- `GET /api/servers` - Sunucu listesi
- `GET /api/servers/{server_id}` - Sunucu detayı
- `PUT /api/servers/{server_id}` - Sunucu güncelleme
- `DELETE /api/servers/{server_id}` - Sunucu silme

#### Servis Yönetimi
- `POST /api/services` - Servis ekleme
- `GET /api/services` - Servis listesi
- `GET /api/services/{service_id}` - Servis detayı
- `PUT /api/services/{service_id}` - Servis güncelleme
- `DELETE /api/services/{service_id}` - Servis silme

#### İzleme Yönetimi
- `POST /api/monitors` - Monitor oluşturma
- `GET /api/monitors` - Monitor listesi
- `GET /api/monitors/{monitor_id}` - Monitor detayı
- `PUT /api/monitors/{monitor_id}` - Monitor güncelleme
- `DELETE /api/monitors/{monitor_id}` - Monitor silme
- `POST /api/monitors/{monitor_id}/check` - Anlık kontrol

#### Alert Yönetimi
- `POST /api/alert-channels` - Alert kanalı ekleme
- `GET /api/alert-channels` - Alert kanalı listesi
- `PUT /api/alert-channels/{channel_id}` - Alert kanalı güncelleme
- `DELETE /api/alert-channels/{channel_id}` - Alert kanalı silme
- `POST /api/alert-rules` - Alert kuralı oluşturma
- `GET /api/alert-rules` - Alert kuralı listesi
- `PUT /api/alert-rules/{rule_id}` - Alert kuralı güncelleme
- `DELETE /api/alert-rules/{rule_id}` - Alert kuralı silme
- `GET /api/alert-history` - Alert geçmişi

### 🧪 Test Senaryoları

#### Temel Test Senaryosu
1. **Tenant Oluşturma**: Yeni bir test tenant'ı oluşturuldu
2. **Sunucu Ekleme**: `217.116.197.152` IP'li sunucu eklendi
3. **Servis Tanımlama**: UDP 5060 portu için servis tanımlandı
4. **Monitor Oluşturma**: Sunucu ve servis eşlemesi ile izleme başlatıldı
5. **Anlık Kontrol**: Manuel port kontrolü başarıyla gerçekleştirildi

### 📋 Gelecek Versiyonlar

#### Versiyon 1.1.0 (Planlanan)
- **Webhook Entegrasyonları**: Slack, Discord, Teams entegrasyonları
- **Grafik Dashboard**: İstatistik grafikleri ve trend analizi
- **Bildirim Şablonları**: Özelleştirilebilir alert mesajları
- **Bakım Modu**: Planlı bakım süreleri için geçici izleme durdurma

#### Versiyon 1.2.0 (Planlanan)
- **SSL Sertifika İzleme**: SSL sertifika süre kontrolü
- **HTTP/HTTPS İzleme**: Web servisleri için HTTP durum kontrolü
- **DNS İzleme**: DNS çözümleme kontrolü
- **Ping İzleme**: ICMP ping kontrolü

#### Versiyon 2.0.0 (Planlanan)
- **Web Arayüzü**: Tam özellikli web dashboard
- **Mobil Uygulama**: iOS/Android mobil uygulaması
- **Gelişmiş Raporlama**: PDF/Excel rapor export
- **API Rate Limiting**: Gelişmiş API güvenlik

---

## Versiyonlama Kuralları

### Semantic Versioning (SemVer)
Bu proje [Semantic Versioning](https://semver.org/) kurallarını takip eder:

- **MAJOR.MINOR.PATCH** formatında (örn: 1.0.0)
- **MAJOR**: Geriye uyumsuz API değişiklikleri
- **MINOR**: Geriye uyumlu yeni özellikler
- **PATCH**: Geriye uyumlu hata düzeltmeleri

### Değişiklik Kategorileri

#### 🎉 Yeni Özellikler
- Yeni API endpoint'leri
- Yeni veritabanı tabloları
- Yeni konfigürasyon seçenekleri
- Yeni alert kanalları

#### 🔧 İyileştirmeler
- Performans optimizasyonları
- Kod refactoring
- Dokümantasyon güncellemeleri
- UI/UX iyileştirmeleri

#### 🐛 Hata Düzeltmeleri
- Bug fixes
- Güvenlik açıkları
- Veritabanı sorunları
- API davranış düzeltmeleri

#### 🔒 Güvenlik
- Güvenlik açıkları
- Authentication iyileştirmeleri
- Authorization güncellemeleri

### Katkıda Bulunma

Yeni özellikler veya değişiklikler için:

1. **Feature Branch** oluşturun
2. **Test Coverage** ekleyin
3. **Dokümantasyon** güncelleyin
4. **VERSION.md** dosyasını güncelleyin
5. **Pull Request** oluşturun

---

**Son Güncelleme**: 2024-12-19  
**Versiyon**: 1.0.0  
**Durum**: Production Ready

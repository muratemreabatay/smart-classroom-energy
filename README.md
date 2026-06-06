# Enerji Verimliliği için Akıllı Sınıf Otomasyon ve Analiz Sistemi

Üniversite amfilerinin enerji tüketimini, oda doluluk oranına göre aydınlatma,
iklimlendirme ve cihaz güçlerini otomatik kontrol ederek optimize eden; aynı
zamanda tüketim verilerini analiz edip tasarruf raporu sunan bir sistem.

Sistem üç amfiyi (101, 102, 103) ayrı sekmelerde gösterir. **Amfi 101** gerçek
Arduino sensöründen canlı veri alır; diğer ikisi simülasyon olarak çalışır.

---

## Proje Yapısı

```
smart-classroom-energy-main/
├── main.py                          # Masaüstü arayüz (GUI) + sensör okuma
├── README.md                        # Bu dosya
└── Smart-Classroom/
    ├── mdb308.py                    # Sensör verisini Google Sheets'e kaydeder
    └── arduino_sensor/
        └── arduino_sensor.ino       # Arduino kodu (DHT22 + MQ135 + BH1750)
```

---

## 1. Gereksinimler

**Yazılım**
- Python 3.9+
- Python kütüphaneleri:
  ```bash
  pip install customtkinter pyserial
  ```
  > `pyserial` kurulu değilse uygulama yine açılır, sadece sensör çalışmaz
  > (tüm amfiler simülasyon olur).

**Donanım (Amfi 101 canlı veri için)**
- ESP32 / Arduino kart
- DHT22 (sıcaklık + nem)
- MQ135 (hava kalitesi)
- GY-302 / BH1750 (ışık, lux)

---

## 2. Arduino'yu Hazırla

1. Arduino IDE'de şu kütüphaneleri kur: **DHT sensor library**, **BH1750**.
2. `Smart-Classroom/arduino_sensor/arduino_sensor.ino` dosyasını karta yükle.
3. Kart, sensör verisini her dakika seri porttan şu formatta gönderir:
   ```
   sicaklik,nem,hava,isik
   ```

---

## 3. Arayüzü (GUI) Çalıştır

```bash
python3 main.py
```

Arduino bilgisayara takılıysa Amfi 101'de **🟢 Canlı Sensör** yazısı görünür ve
gerçek sıcaklık / nem / hava kalitesi / ışık değerleri ekrana gelir.

### Seri Port Ayarı

`main.py` dosyasının üstündeki port satırını işletim sistemine göre düzenle:

```python
SERIAL_PORT = "COM7"   # Windows
```

| İşletim Sistemi | Örnek Port |
|---|---|
| Windows | `COM7` |
| macOS | `/dev/cu.usbserial-XXXX` |
| Linux | `/dev/ttyUSB0` |

> Portu bulmak için: Windows'ta **Aygıt Yöneticisi → Bağlantı Noktaları**;
> Mac/Linux'ta terminalde `ls /dev/cu.*` veya `ls /dev/ttyUSB*`.

---

## 4. (Opsiyonel) Verileri Google Sheets'e Kaydet

`Smart-Classroom/mdb308.py` sensör verisini Google Sheets'e arşivler.

1. Google Cloud'dan bir service account oluştur, `credentials.json` dosyasını
   `Smart-Classroom/` klasörüne koy.
2. Google Drive'da **SensorVerileri** adında bir sheet oluştur ve service
   account e-postasıyla paylaş.
3. Kütüphaneleri kur ve çalıştır:
   ```bash
   pip install pyserial gspread oauth2client
   python3 Smart-Classroom/mdb308.py
   ```

> **Önemli:** Bir seri portu aynı anda tek program açabilir. `main.py` (GUI) ve
> `mdb308.py` (Sheets kaydı) **aynı bilgisayarda aynı portu** kullanamaz. Aynı
> anda sadece birini çalıştır.

---

## Sensör Durum Göstergeleri (Amfi 101)

| Gösterge | Anlamı |
|---|---|
| 🟢 Canlı Sensör | Arduino'dan veri geliyor |
| 🟡 Sensör bekleniyor | Bağlantı kuruldu, ilk veri bekleniyor |
| 🔴 Sensör bağlı değil | Port açılamadı (Arduino takılı değil / yanlış port) |
| ⚪ Simülasyon | Bu amfi sensörsüz (102 ve 103 her zaman böyledir) |

---

## Sık Karşılaşılan Sorunlar

- **`could not open port COM7`** → Yanlış port veya Arduino takılı değil.
  Doğru portu yaz; Arduino'yu kontrol et.
- **`Access is denied` / `port is busy`** → Arduino IDE'nin Seri Monitör'ü ya da
  `mdb308.py` portu tutuyor olabilir. Onları kapat.
- **GUI açılıyor ama 101 hep simülasyon** → `pyserial` kurulu değil veya port
  yanlış. `pip install pyserial` ve port ayarını kontrol et.

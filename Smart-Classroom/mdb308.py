import serial
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import time

# ---------------- GOOGLE SHEETS AYARI ----------------

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", scope
)

client = gspread.authorize(creds)

# Google Sheets dosya adı
sheet = client.open("SensorVerileri").sheet1

# Program her başladığında sayfayı temizle
sheet.clear()

# Başlıkları yeniden ekle
sheet.append_row(["Zaman", "Sicaklik", "Nem", "Hava", "Isik"])

# ---------------- ARDUINO SERİ PORT ----------------

ser = serial.Serial("COM7", 115200, timeout=2)
time.sleep(2)

print("Veri okunuyor ve Google Sheets'e kaydediliyor...")

while True:
    try:
        line = ser.readline().decode("utf-8", errors="ignore").strip()

        if not line:
            continue

        print("Gelen veri:", line)

        parts = line.split(",")

        if len(parts) != 4:
            print("Atlandı:", line)
            continue

        s, n, h, l = map(float, parts)

        zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        sheet.append_row([zaman, s, n, h, l])

        print(f"Kaydedildi -> {zaman} | {s}°C {n}% {h} {l} lux")

        time.sleep(1)

    except Exception as e:
        print("Hata:", e)
        time.sleep(2)
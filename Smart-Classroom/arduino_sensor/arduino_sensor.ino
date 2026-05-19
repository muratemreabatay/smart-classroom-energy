#include <Wire.h>
#include <BH1750.h>
#include "DHT.h"

// ----------- MQ135 -----------
int mq135Pin = 34;

// ----------- GY302 (BH1750) -----------
BH1750 lightMeter;

// ----------- DHT22 -----------
#define DHTPIN 16
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);

void setup() {

  Serial.begin(115200);

  // I2C başlat
  Wire.begin(21, 22);

  // BH1750 başlat
  lightMeter.begin();

  // DHT22 başlat
  dht.begin();

  // Sensör stabilizasyon
  delay(2000);
}

void loop() {

  // MQ135 hava kalitesi
  int havaKalitesi = analogRead(mq135Pin);

  // Işık seviyesi
  float lux = lightMeter.readLightLevel();

  // DHT22 sıcaklık ve nem
  float sicaklik = dht.readTemperature();
  float nem = dht.readHumidity();

  // DHT hata kontrolü
  if (isnan(sicaklik) || isnan(nem)) {
    Serial.println("DHT okunamadi!");
    delay(1000);
    return;
  }

  // Verileri CSV formatında gönder
  Serial.print(sicaklik);
  Serial.print(",");

  Serial.print(nem);
  Serial.print(",");

  Serial.print(havaKalitesi);
  Serial.print(",");

  Serial.println(lux);

  // 1 dakika bekle
  delay(60000);
}
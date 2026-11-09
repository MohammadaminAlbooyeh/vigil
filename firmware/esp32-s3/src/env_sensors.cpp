#include <Arduino.h>
#include <DHT.h>
#include "config.h"

DHT dht(DHT_PIN, DHT_TYPE);

void env_init() {
    dht.begin();
    Serial.println("[ENV] DHT22 initialized");
}

float env_read_temp() {
    float t = dht.readTemperature();
    return isnan(t) ? -1.0 : t;
}

float env_read_hum() {
    float h = dht.readHumidity();
    return isnan(h) ? -1.0 : h;
}

int env_read_aq() {
    return analogRead(34);
}
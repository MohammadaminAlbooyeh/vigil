#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <Wire.h>

#include "config.h"

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
DHT dht(DHT_PIN, DHT_TYPE);

unsigned long lastPublish = 0;
const unsigned long PUBLISH_INTERVAL = 5000;

void setup_wifi() {
    Serial.println("[WIFI] Connecting...");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println();
    Serial.print("[WIFI] Connected. IP: ");
    Serial.println(WiFi.localIP());
}

void setup_mqtt() {
    mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
}

void reconnect_mqtt() {
    while (!mqttClient.connected()) {
        Serial.print("[MQTT] Connecting...");
        if (mqttClient.connect(DEVICE_ID, MQTT_USER, MQTT_PASS)) {
            Serial.println("connected");
        } else {
            Serial.print("failed, rc=");
            Serial.print(mqttClient.state());
            Serial.println(" retrying in 5s");
            delay(5000);
        }
    }
}

void setup() {
    Serial.begin(115200);
    Serial.println("\n=== Sentinel-X ESP32-S3 Sensor Node ===");

    pinMode(PIR_PIN, INPUT);
    dht.begin();
    Wire.begin(ENV_I2C_SDA, ENV_I2C_SCL);

    setup_wifi();
    setup_mqtt();

    Serial.println("[SENSOR] PIR, DHT22, and I2C initialized");
}

void loop() {
    if (!mqttClient.connected()) {
        reconnect_mqtt();
    }
    mqttClient.loop();

    bool motion = digitalRead(PIR_PIN) == HIGH;
    if (motion) {
        mqttClient.publish(TOPIC_EVENTS, "motion_detected");
        Serial.println("[PIR] Motion detected");
    }

    if (millis() - lastPublish > PUBLISH_INTERVAL) {
        lastPublish = millis();
        float temp = dht.readTemperature();
        float hum = dht.readHumidity();

        if (!isnan(temp) && !isnan(hum)) {
            String payload = String("{\"device\":\"") + DEVICE_ID +
                             "\",\"temp\":" + temp +
                             ",\"hum\":" + hum + "}";
            mqttClient.publish(TOPIC_EVENTS, payload.c_str());
            Serial.printf("[ENV] Temp=%.1f Hum=%.1f\n", temp, hum);
        }
    }

    delay(100);
}
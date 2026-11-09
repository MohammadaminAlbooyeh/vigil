#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ESP32Servo.h>
#include "config.h"

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
ESP32Servo servo;

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
            mqttClient.subscribe(TOPIC_COMMANDS);
        } else {
            Serial.print("failed, rc=");
            Serial.print(mqttClient.state());
            Serial.println(" retrying in 5s");
            delay(5000);
        }
    }
}

void callback(char* topic, byte* payload, unsigned int length) {
    String message;
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    Serial.print("Command received: ");
    Serial.println(message);

    if (message == "siren_on") {
        digitalWrite(RELAY_SIREN, HIGH);
    } else if (message == "siren_off") {
        digitalWrite(RELAY_SIREN, LOW);
    } else if (message == "buzzer_on") {
        digitalWrite(RELAY_BUZZER, HIGH);
    } else if (message == "buzzer_off") {
        digitalWrite(RELAY_BUZZER, LOW);
    } else if (message == "door_lock") {
        digitalWrite(RELAY_DOOR, HIGH);
    } else if (message == "door_unlock") {
        digitalWrite(RELAY_DOOR, LOW);
    } else if (message == "light_on") {
        digitalWrite(RELAY_LIGHT, HIGH);
    } else if (message == "light_off") {
        digitalWrite(RELAY_LIGHT, LOW);
    } else if (message == "pan_left") {
        servo.write(180);
    } else if (message == "pan_right") {
        servo.write(0);
    } else if (message == "pan_center") {
        servo.write(90);
    }
}

void setup() {
    Serial.begin(115200);
    Serial.println("\n=== Sentinel-X ESP32 Actuator ===");

    pinMode(RELAY_DOOR, OUTPUT);
    pinMode(RELAY_LIGHT, OUTPUT);
    pinMode(RELAY_BUZZER, OUTPUT);
    pinMode(RELAY_SIREN, OUTPUT);

    servo.attach(SERVO_PIN, 500, 2500);
    servo.write(90);

    setup_wifi();
    setup_mqtt();
    mqttClient.setCallback(callback);
}

void loop() {
    if (!mqttClient.connected()) {
        reconnect_mqtt();
    }
    mqttClient.loop();
    delay(100);
}
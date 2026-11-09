#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ESP32Servo.h>
#include <esp_camera.h>

#include "config.h"

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
ESP32Servo servo;

bool motionDetected = false;
unsigned long lastMotionTime = 0;
const unsigned long MOTION_COOLDOWN = 5000;

void setup_wifi() {
    Serial.println("[WIFI] Connecting...");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println();
    Serial.print("[WIFI] Connected to ");
    Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
    Serial.print("Message arrived [");
    Serial.print(topic);
    Serial.print("] ");
    for (int i = 0; i < length; i++) {
        Serial.print((char)payload[i]);
    }
    Serial.println();
}

void setup_mqtt() {
    mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
    mqttClient.setCallback(callback);
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

void setup_camera() {
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_IO;
    config.pin_d1 = Y3_IO;
    config.pin_d2 = Y4_IO;
    config.pin_d3 = Y5_IO;
    config.pin_d4 = Y6_IO;
    config.pin_d5 = Y7_IO;
    config.pin_d6 = Y8_IO;
    config.pin_xclk = XCLK_IO;
    config.pin_pclk = PCLK_IO;
    config.pin_vsync = VSYNC_IO;
    config.pin_href = HREF_IO;
    config.pin_siod = SIOD_IO;
    config.pin_sioc = SIOC_IO;
    config.pin_pwdn = PWDN_IO;
    config.pin_reset = RESET_IO;
    config.xclk_freq_hz = 20000;
    config.pixel_format = PIXFORMAT_JPEG;
    config.frame_size = FRAMESIZE_VGA;
    config.jpeg_quality = 12;
    config.fb_count = 2;
    config.fb_location = FB_RAM;
    config.grab_mode = CAMERA_GRAB_LATEST;

    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Camera init failed: 0x%x\n", err);
        return;
    }
    Serial.println("[CAMERA] Initialized");
}

void setup() {
    Serial.begin(115200);
    Serial.println("\n=== Sentinel-X ESP32-CAM ===");

    servo.attach(SERVO_PIN, SERVO_MIN_US, SERVO_MAX_US);
    servo.write(90);
    Serial.println("[SERVO] Attached");

    setup_camera();
    setup_wifi();
    setup_mqtt();

    pinMode(MOTION_PIN, INPUT);
}

void loop() {
    if (!mqttClient.connected()) {
        reconnect_mqtt();
    }
    mqttClient.loop();

    int motionState = digitalRead(MOTION_PIN);
    if (motionState == HIGH && !motionDetected) {
        motionDetected = true;
        lastMotionTime = millis();
        Serial.println("[MOTION] Detected!");
        servo.write(90);
        mqttClient.publish(TOPIC_EVENTS, "motion_detected");
    }

    if (motionDetected && (millis() - lastMotionTime > MOTION_COOLDOWN)) {
        motionDetected = false;
        Serial.println("[MOTION] Cooldown expired");
    }

    delay(100);
}
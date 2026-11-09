#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include "config.h"

WiFiClient wifiClient;

class MQTTClient {
public:
    PubSubClient client;
    MQTTClient() : client(wifiClient) {}

    void begin() {
        client.setServer(MQTT_SERVER, MQTT_PORT);
    }

    bool connect() {
        return client.connect(DEVICE_ID, MQTT_USER, MQTT_PASS);
    }

    bool publish(const char* topic, const char* message) {
        return client.publish(topic, message);
    }

    bool subscribe(const char* topic) {
        return client.subscribe(topic);
    }

    void loop() {
        client.loop();
    }

    bool connected() {
        return client.connected();
    }
};
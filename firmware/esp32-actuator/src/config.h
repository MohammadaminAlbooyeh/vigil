#ifndef CONFIG_H
#define CONFIG_H

#define WIFI_SSID "your-ssid"
#define WIFI_PASSWORD "your-password"

#define MQTT_SERVER "192.168.1.100"
#define MQTT_PORT 1883
#define MQTT_USER "sentinel"
#define MQTT_PASS "sentinel123"

#define DEVICE_ID "esp32-actuator-01"
#define DEVICE_TYPE "actuator"

#define TOPIC_EVENTS "sentinel/events/actuator"
#define TOPIC_COMMANDS "sentinel/commands/actuator"

#define RELAY_DOOR 12
#define RELAY_LIGHT 13
#define RELAY_BUZZER 14
#define RELAY_SIREN 15

#define SERVO_PIN 2
#define SERVO_NEUTRAL_US 1500

#endif
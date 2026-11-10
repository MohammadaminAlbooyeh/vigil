#ifndef CONFIG_H
#define CONFIG_H

#define WIFI_SSID "your-ssid"
#define WIFI_PASSWORD "your-password"

#define MQTT_SERVER "192.168.1.100"
#define MQTT_PORT 1883
#define MQTT_USER "sentinel"
#define MQTT_PASS "sentinel123"

#define DEVICE_ID "esp32-s3-01"
#define DEVICE_TYPE "sensor"

#define TOPIC_EVENTS "sentinel/events/sensor"
#define TOPIC_COMMANDS "sentinel/commands/sensor"

#define PIR_PIN 4
#define PIR_DELAY_MS 2000
#define PIR_WARMUP_MS 10000
#define PIR_COOLDOWN_MS 5000

#define RADAR_RX 16
#define RADAR_TX 17
#define RADAR_BAUD 256000

#define ENV_I2C_SDA 21
#define ENV_I2C_SCL 22
#define DHT_PIN 5
#define DHT_TYPE DHT22

#endif
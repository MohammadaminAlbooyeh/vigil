#ifndef CONFIG_H
#define CONFIG_H

#define WIFI_SSID "your-ssid"
#define WIFI_PASSWORD "your-password"

#define MQTT_SERVER "192.168.1.100"
#define MQTT_PORT 1883
#define MQTT_USER "sentinel"
#define MQTT_PASS "sentinel123"

#define DEVICE_ID "esp32-cam-01"
#define DEVICE_TYPE "camera"

#define TOPIC_EVENTS "sentinel/events/camera"
#define TOPIC_COMMANDS "sentinel/commands/camera"

#define PWDN_IO 32
#define RESET_IO -1
#define XCLK_IO 0
#define SIOD_IO 5
#define SIOC_IO 4
#define Y2_IO 19
#define Y3_IO 18
#define Y4_IO 17
#define Y5_IO 16
#define Y6_IO 15
#define Y7_IO 14
#define Y8_IO 12
#define VSYNC_IO 5
#define HREF_IO 2
#define PCLK_IO 1

#define SERVO_PIN 13
#define SERVO_MIN_US 500
#define SERVO_MAX_US 2500
#define SERVO_NEUTRAL_US 1500

#define MOTION_PIN 14
#define MOTION_THRESHOLD 3
#define MOTION_COOLDOWN_MS 5000

#endif
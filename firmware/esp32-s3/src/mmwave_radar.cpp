#include <Arduino.h>
#include "config.h"

void radar_init() {
    Serial2.begin(RADAR_BAUD, SERIAL_8N1, RADAR_RX, RADAR_TX);
    Serial.println("[RADAR] Initialized");
}

bool radar_detect() {
    if (Serial2.available() >= 128) {
        uint8_t buf[128];
        Serial2.readBytes(buf, 128);
        return true;
    }
    return false;
}
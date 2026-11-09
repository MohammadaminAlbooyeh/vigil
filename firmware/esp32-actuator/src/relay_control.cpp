#include <Arduino.h>
#include "config.h"

void relay_init() {
    pinMode(RELAY_DOOR, OUTPUT);
    pinMode(RELAY_LIGHT, OUTPUT);
    pinMode(RELAY_BUZZER, OUTPUT);
    pinMode(RELAY_SIREN, OUTPUT);

    digitalWrite(RELAY_DOOR, LOW);
    digitalWrite(RELAY_LIGHT, LOW);
    digitalWrite(RELAY_BUZZER, LOW);
    digitalWrite(RELAY_SIREN, LOW);
}

void relay_set(uint8_t pin, bool state) {
    digitalWrite(pin, state ? HIGH : LOW);
}

void relay_buzzer_blink(int times, int delay_ms) {
    for (int i = 0; i < times; i++) {
        digitalWrite(RELAY_BUZZER, HIGH);
        delay(delay_ms);
        digitalWrite(RELAY_BUZZER, LOW);
        delay(delay_ms);
    }
}

void relay_siren_activate(int duration_ms) {
    digitalWrite(RELAY_SIREN, HIGH);
    delay(duration_ms);
    digitalWrite(RELAY_SIREN, LOW);
}
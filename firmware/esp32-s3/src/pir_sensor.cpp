#include <Arduino.h>
#include "config.h"

// PIR sensor with warmup + cooldown for ESP32-S3.

static bool pir_state = false;
static unsigned long last_event_time = 0;
static bool warmed_up = false;
static unsigned long warmup_start = 0;

void pir_init() {
    pinMode(PIR_PIN, INPUT);
    pir_state = false;
    last_event_time = 0;
    warmed_up = false;
    warmup_start = millis();
    // PIR sensors need a warmup period before reporting reliably
    delay(PIR_WARMUP_MS);
    warmed_up = true;
}

bool pir_check() {
    if (!warmed_up) {
        return false;
    }

    unsigned long now = millis();
    bool raw = digitalRead(PIR_PIN) == HIGH;

    if (raw && !pir_state) {
        pir_state = true;
        last_event_time = now;
        return true;  // rising edge: new motion event
    }

    if (!raw && pir_state && (now - last_event_time > PIR_COOLDOWN_MS)) {
        pir_state = false;
    }

    return pir_state;
}

bool pir_event() {
    // Returns true once per motion event (rising edge)
    return pir_state;
}

void pir_reset() {
    pir_state = false;
    last_event_time = 0;
}

unsigned long pir_last_event_time() {
    return last_event_time;
}

#include <Arduino.h>
#include "config.h"

// Motion detector with debounce + cooldown for ESP32-CAM.

static bool motion_state = false;
static unsigned long last_motion_time = 0;
static unsigned long last_read_time = 0;
static int stable_count = 0;

void motion_init() {
    pinMode(MOTION_PIN, INPUT);
    motion_state = false;
    last_motion_time = 0;
    last_read_time = 0;
    stable_count = 0;
}

bool motion_check() {
    unsigned long now = millis();
    // Debounce: only sample every 50ms
    if (now - last_read_time < 50) {
        return motion_state;
    }
    last_read_time = now;

    int reading = digitalRead(MOTION_PIN);
    if (reading == HIGH) {
        stable_count++;
    } else {
        stable_count = 0;
    }

    // Require MOTION_THRESHOLD consecutive HIGH readings to assert motion
    if (!motion_state && stable_count >= MOTION_THRESHOLD) {
        motion_state = true;
        last_motion_time = now;
        return true;
    }

    // Cooldown: hold motion_state true until cooldown expires
    if (motion_state && (now - last_motion_time > MOTION_COOLDOWN_MS)) {
        motion_state = false;
        stable_count = 0;
    }

    return motion_state;
}

void motion_reset() {
    motion_state = false;
    last_motion_time = 0;
    stable_count = 0;
}

unsigned long motion_last_time() {
    return last_motion_time;
}

bool motion_active() {
    return motion_state;
}

#include <Arduino.h>
#include "config.h"

void motion_init() {
    pinMode(MOTION_PIN, INPUT);
}

bool motion_check() {
    return digitalRead(MOTION_PIN) == HIGH;
}

void motion_reset() {
}
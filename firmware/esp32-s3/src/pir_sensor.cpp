#include <Arduino.h>
#include "config.h"

void pir_init() {
    pinMode(PIR_PIN, INPUT);
}

bool pir_check() {
    return digitalRead(PIR_PIN) == HIGH;
}
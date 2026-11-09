#include <Arduino.h>
#include <ESP32Servo.h>
#include "config.h"

ESP32Servo servo;

void servo_init() {
    servo.attach(SERVO_PIN, SERVO_MIN_US, SERVO_MAX_US);
    servo.write(90);
}

void servo_set_angle(int angle) {
    servo.write(angle);
}

void servo_pan_left() {
    servo.write(180);
}

void servo_pan_right() {
    servo.write(0);
}

void servo_pan_center() {
    servo.write(90);
}
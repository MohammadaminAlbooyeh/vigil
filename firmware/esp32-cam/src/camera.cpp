#include <Arduino.h>
#include "config.h"
#include <esp_camera.h>

void camera_init() {
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_IO;
    config.pin_d1 = Y3_IO;
    config.pin_d2 = Y4_IO;
    config.pin_d3 = Y5_IO;
    config.pin_d4 = Y6_IO;
    config.pin_d5 = Y7_IO;
    config.pin_d6 = Y8_IO;
    config.pin_xclk = XCLK_IO;
    config.pin_pclk = PCLK_IO;
    config.pin_vsync = VSYNC_IO;
    config.pin_href = HREF_IO;
    config.pin_siod = SIOD_IO;
    config.pin_sioc = SIOC_IO;
    config.pin_pwdn = PWDN_IO;
    config.pin_reset = RESET_IO;
    config.xclk_freq_hz = 20000;
    config.pixel_format = PIXFORMAT_JPEG;
    config.frame_size = FRAMESIZE_VGA;
    config.jpeg_quality = 12;
    config.fb_count = 2;
    config.fb_location = FB_RAM;
    config.grab_mode = CAMERA_GRAB_LATEST;

    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Camera init failed: 0x%x\n", err);
        return;
    }
    Serial.println("[CAMERA] Initialized");
}

camera_fb_t* camera_capture() {
    camera_fb_t* fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("[CAMERA] Capture failed");
        return nullptr;
    }
    return fb;
}

void camera_release(camera_fb_t* fb) {
    if (fb) esp_camera_fb_return(fb);
}
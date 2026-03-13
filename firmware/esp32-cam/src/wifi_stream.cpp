#include "wifi_stream.h"
#include <Arduino.h>
// TODO: Include esp_camera.h when building for ESP32-S3-CAM

void WifiStream::init() {
    // TODO: Initialize OV2640 camera with PSRAM frame buffer
    // camera_config_t config;
    // config.frame_size = FRAMESIZE_SVGA;  // 800x600
    // config.pixel_format = PIXFORMAT_JPEG;
    // config.jpeg_quality = 12;
    // config.fb_count = 2;  // Double buffer with PSRAM
    // esp_camera_init(&config);
    Serial.println("Camera initialized (stub)");
}

void WifiStream::handle_stream(WebServer& server) {
    // TODO: Serve multipart MJPEG stream
    // Content-Type: multipart/x-mixed-replace; boundary=frame
    // Each part: Content-Type: image/jpeg + JPEG data
    server.send(200, "text/plain", "MJPEG stream (stub)");
}

void WifiStream::handle_capture(WebServer& server) {
    // TODO: Capture single frame and return as JPEG
    server.send(200, "text/plain", "Single capture (stub)");
}

void WifiStream::set_fps(int fps) {
    target_fps_ = fps;
}

int WifiStream::get_current_fps() const {
    return target_fps_;
}

uint8_t* WifiStream::get_last_frame() {
    // TODO: Return pointer to last captured frame buffer
    return nullptr;
}

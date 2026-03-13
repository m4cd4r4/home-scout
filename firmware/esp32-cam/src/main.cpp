/**
 * Home Scout - ESP32-S3-CAM Fixed Room Camera
 *
 * Each ESP32-S3-CAM module is mounted in a room and serves MJPEG
 * frames over the local ScoutNet WiFi. Scout pulls frames on demand.
 *
 * Endpoints:
 *   GET /stream  - MJPEG stream (continuous)
 *   GET /capture - Single JPEG frame
 *   GET /status  - JSON health status
 *
 * Motion detection runs on-device to bump FPS when activity detected.
 */

#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include "wifi_stream.h"
#include "motion_detect.h"

// ScoutNet WiFi credentials - configured during setup
const char* WIFI_SSID = "ScoutNet";
const char* WIFI_PASSWORD = "scout_local_only";

// Room identifier - set per camera during deployment
const char* ROOM_NAME = "living_room";
const char* CAMERA_ID = "esp32_living_room";

WebServer server(80);
WifiStream streamer;
MotionDetect motion;

void handle_status() {
    String json = "{";
    json += "\"camera_id\":\"" + String(CAMERA_ID) + "\",";
    json += "\"room\":\"" + String(ROOM_NAME) + "\",";
    json += "\"fps\":" + String(streamer.get_current_fps()) + ",";
    json += "\"motion\":" + String(motion.is_active() ? "true" : "false") + ",";
    json += "\"uptime_seconds\":" + String(millis() / 1000) + ",";
    json += "\"free_heap\":" + String(ESP.getFreeHeap());
    json += "}";
    server.send(200, "application/json", json);
}

void setup() {
    Serial.begin(115200);
    Serial.printf("Home Scout ESP32-CAM - Room: %s\n", ROOM_NAME);

    // Connect to ScoutNet
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.printf("\nConnected. IP: %s\n", WiFi.localIP().toString().c_str());

    // Initialize camera
    streamer.init();

    // Initialize motion detection
    motion.init();

    // HTTP endpoints
    server.on("/stream", [](){ streamer.handle_stream(server); });
    server.on("/capture", [](){ streamer.handle_capture(server); });
    server.on("/status", handle_status);
    server.begin();

    Serial.println("Ready. Serving on port 80.");
}

void loop() {
    server.handleClient();

    // Adjust FPS based on motion
    if (motion.check_frame(streamer.get_last_frame())) {
        streamer.set_fps(SCOUT_STREAM_FPS);
    } else {
        streamer.set_fps(SCOUT_IDLE_FPS);
    }
}

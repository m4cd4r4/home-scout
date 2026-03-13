#pragma once

#include <WebServer.h>

/**
 * MJPEG streaming over HTTP for ESP32-CAM.
 * Serves frames at configurable FPS on /stream endpoint.
 */
class WifiStream {
public:
    void init();
    void handle_stream(WebServer& server);
    void handle_capture(WebServer& server);
    void set_fps(int fps);
    int get_current_fps() const;
    uint8_t* get_last_frame();

private:
    int target_fps_ = 1;
    unsigned long last_frame_time_ = 0;
};

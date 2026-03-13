#pragma once

#include <stdint.h>

/**
 * Simple pixel-difference motion detection.
 * Compares consecutive frames and triggers when enough pixels change.
 * Runs on the ESP32 to reduce network traffic - only bumps FPS on motion.
 */
class MotionDetect {
public:
    void init();
    bool check_frame(uint8_t* frame);
    bool is_active() const;

private:
    uint8_t* prev_frame_ = nullptr;
    bool active_ = false;
    unsigned long last_motion_time_ = 0;
    float threshold_ = 0.05;  // 5% of pixels must change
};

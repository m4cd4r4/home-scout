#include "motion_detect.h"
#include <Arduino.h>
#include <stdlib.h>

void MotionDetect::init() {
    prev_frame_ = nullptr;
    active_ = false;
    last_motion_time_ = 0;
}

bool MotionDetect::check_frame(uint8_t* frame) {
    if (frame == nullptr) return false;

    // TODO: Compare current frame with previous frame
    // Count pixels that differ by more than a threshold
    // If enough pixels changed, motion is detected

    // For now, stub that always returns false (no motion)
    unsigned long now = millis();

    if (active_ && (now - last_motion_time_ > SCOUT_MOTION_BUMP_SECONDS * 1000)) {
        active_ = false;
    }

    return active_;
}

bool MotionDetect::is_active() const {
    return active_;
}

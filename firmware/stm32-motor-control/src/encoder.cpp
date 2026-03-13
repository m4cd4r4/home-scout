#include "encoder.h"
#include <Arduino.h>

// Wheel circumference in meters
static const float WHEEL_CIRCUMFERENCE_M =
    (SCOUT_WHEEL_DIAMETER_MM / 1000.0) * 3.14159265;

void Encoder::init(int encoder_id) {
    encoder_id_ = encoder_id;
    count_ = 0;
    last_count_ = 0;
    last_time_us_ = micros();

    // TODO: Configure STM32H5 hardware timer for quadrature decoding
    // The STM32H5 has dedicated encoder interface mode on TIM1-TIM4
    // This avoids interrupt overhead and gives exact pulse counts
}

long Encoder::get_count() const {
    return count_;
}

void Encoder::reset() {
    count_ = 0;
    last_count_ = 0;
}

float Encoder::get_velocity() {
    unsigned long now = micros();
    unsigned long dt = now - last_time_us_;

    if (dt == 0) return velocity_;

    long delta = count_ - last_count_;
    last_count_ = count_;
    last_time_us_ = now;

    // Convert encoder ticks to meters per second
    float revolutions = (float)delta / SCOUT_ENCODER_CPR;
    float distance = revolutions * WHEEL_CIRCUMFERENCE_M;
    velocity_ = distance / (dt / 1000000.0);

    return velocity_;
}

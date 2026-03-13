#pragma once

/**
 * Quadrature encoder reader using STM32H5 hardware timers.
 * Pololu 37D motors have 64 CPR encoders, 50:1 gearbox = 3200 CPR at output.
 */
class Encoder {
public:
    void init(int encoder_id);
    long get_count() const;
    void reset();
    float get_velocity();  // m/s based on wheel diameter

private:
    int encoder_id_ = -1;
    volatile long count_ = 0;
    long last_count_ = 0;
    unsigned long last_time_us_ = 0;
    float velocity_ = 0.0;
};

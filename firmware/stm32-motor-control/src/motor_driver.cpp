#include "motor_driver.h"
#include <Arduino.h>

// Pin mappings - update for VENTUNO Q STM32H5 GPIO
// These are placeholder pins
static const int PWM_PINS[] = {3, 5, 6, 9};
static const int DIR_PINS[] = {2, 4, 7, 8};

void MotorDriver::init(int motor_id) {
    motor_id_ = motor_id;
    pin_pwm_ = PWM_PINS[motor_id];
    pin_dir_ = DIR_PINS[motor_id];

    pinMode(pin_pwm_, OUTPUT);
    pinMode(pin_dir_, OUTPUT);
    stop();
}

void MotorDriver::set_pwm(float duty) {
    // Clamp to speed limit
    float max_duty = SCOUT_MAX_SPEED_MPS / 0.5;  // 0.5 m/s is max mechanical
    if (duty > max_duty) duty = max_duty;
    if (duty < -max_duty) duty = -max_duty;

    if (duty >= 0) {
        digitalWrite(pin_dir_, HIGH);
        analogWrite(pin_pwm_, (int)(duty * 255));
    } else {
        digitalWrite(pin_dir_, LOW);
        analogWrite(pin_pwm_, (int)(-duty * 255));
    }
}

void MotorDriver::stop() {
    analogWrite(pin_pwm_, 0);
}

bool MotorDriver::is_stalled() const {
    return stalled_;
}

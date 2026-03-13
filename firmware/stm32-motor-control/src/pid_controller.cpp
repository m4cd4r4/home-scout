#include "pid_controller.h"

void PIDController::init(float kp, float ki, float kd) {
    kp_ = kp;
    ki_ = ki;
    kd_ = kd;
    reset();
}

float PIDController::compute(float setpoint, float measurement) {
    float error = setpoint - measurement;

    // Proportional
    float p = kp_ * error;

    // Integral with anti-windup
    integral_ += error;
    if (integral_ > output_max_ / ki_) integral_ = output_max_ / ki_;
    if (integral_ < output_min_ / ki_) integral_ = output_min_ / ki_;
    float i = ki_ * integral_;

    // Derivative
    float d = kd_ * (error - prev_error_);
    prev_error_ = error;

    // Sum and clamp
    float output = p + i + d;
    if (output > output_max_) output = output_max_;
    if (output < output_min_) output = output_min_;

    return output;
}

void PIDController::reset() {
    integral_ = 0.0;
    prev_error_ = 0.0;
}

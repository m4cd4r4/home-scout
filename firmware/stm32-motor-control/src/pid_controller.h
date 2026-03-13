#pragma once

/**
 * Simple PID controller for motor velocity control.
 * Runs at 100 Hz in the main loop.
 */
class PIDController {
public:
    void init(float kp, float ki, float kd);
    float compute(float setpoint, float measurement);
    void reset();

private:
    float kp_ = 0.0;
    float ki_ = 0.0;
    float kd_ = 0.0;
    float integral_ = 0.0;
    float prev_error_ = 0.0;
    float output_min_ = -1.0;
    float output_max_ = 1.0;
};

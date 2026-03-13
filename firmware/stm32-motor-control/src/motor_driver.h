#pragma once

/**
 * Motor driver interface for Cytron MDD10A.
 * Each driver has 2 channels (PWM + DIR per channel).
 * Two MDD10A boards drive 4 motors total.
 */
class MotorDriver {
public:
    void init(int motor_id);
    void set_pwm(float duty);  // -1.0 to 1.0
    void stop();
    bool is_stalled() const;

private:
    int pin_pwm_ = -1;
    int pin_dir_ = -1;
    int motor_id_ = -1;
    bool stalled_ = false;
};

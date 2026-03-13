#pragma once

/**
 * Safety subsystem - operates independently of the Qualcomm side.
 *
 * Handles:
 *   - Hardware watchdog (100ms timeout)
 *   - Emergency stop button (GPIO interrupt)
 *   - Cliff detection (TCRT5000 IR sensors)
 *   - Battery voltage monitoring (INA219)
 *   - Motor relay control (master power kill)
 *   - Safe mode (lost heartbeat, sensor failure)
 */
class Safety {
public:
    void init();
    void update();
    void feed_watchdog();
    bool is_emergency_stop() const;
    void enter_safe_mode(const char* reason);
    float get_battery_voltage() const;
    const int* get_cliff_readings() const;

private:
    bool emergency_stop_ = false;
    bool safe_mode_ = false;
    float battery_voltage_ = 0.0;
    int cliff_readings_[2] = {0, 0};

    void check_cliff_sensors();
    void check_battery();
    void open_motor_relay();
};

#pragma once

#include "encoder.h"

/**
 * CAN-FD communication bridge between STM32H5 MCU and Qualcomm SoC.
 *
 * Protocol:
 *   Qualcomm -> STM32: velocity commands, heartbeat, config
 *   STM32 -> Qualcomm: odometry, battery, cliff status, safety alerts
 *
 * CAN-FD message IDs:
 *   0x100: Heartbeat (Qualcomm -> STM32)
 *   0x101: Velocity command (Qualcomm -> STM32)
 *   0x200: Odometry (STM32 -> Qualcomm)
 *   0x201: Battery status (STM32 -> Qualcomm)
 *   0x202: Cliff status (STM32 -> Qualcomm)
 *   0x2FF: Safety alert (STM32 -> Qualcomm)
 */
class CANBridge {
public:
    void init();
    void process_incoming();
    bool has_new_heartbeat();
    float get_target_velocity(int motor_id);
    void send_odometry(Encoder encoders[4]);
    void send_battery_status(float voltage);
    void send_cliff_status(const int* readings);
    void send_safety_alert(const char* message);

private:
    float target_velocities_[4] = {0, 0, 0, 0};
    bool heartbeat_received_ = false;
};

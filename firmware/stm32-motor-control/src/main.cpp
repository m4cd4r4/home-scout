/**
 * Home Scout - STM32H5 Motor Control Firmware
 *
 * This firmware runs on the VENTUNO Q's built-in STM32H5F5 MCU.
 * It handles real-time motor control, encoder reading, PID velocity
 * control, sensor polling, and safety interlocks.
 *
 * The Qualcomm side (Linux/ROS 2) communicates via CAN-FD.
 * This MCU is deliberately kept simple - no decision logic.
 * It executes velocity commands and returns sensor data.
 */

#include <Arduino.h>
#include "motor_driver.h"
#include "encoder.h"
#include "can_bridge.h"
#include "safety.h"
#include "pid_controller.h"

// Motor instances (4 motors, 2 drivers)
MotorDriver motors[4];
Encoder encoders[4];
PIDController pid[4];

// Communication
CANBridge can_bridge;

// Safety
Safety safety;

// Timing
unsigned long last_pid_update = 0;
unsigned long last_heartbeat_rx = 0;
const unsigned long PID_INTERVAL_MS = 10;  // 100 Hz PID loop

void setup() {
    Serial.begin(115200);
    Serial.println("Home Scout STM32H5 - Motor Control v0.1.0");

    // Initialize safety first (sets up e-stop, cliff sensors, watchdog)
    safety.init();

    // Initialize motor drivers
    // TODO: Set actual pin mappings for VENTUNO Q
    for (int i = 0; i < 4; i++) {
        motors[i].init(i);
        encoders[i].init(i);
        pid[i].init(1.0, 0.1, 0.05);  // Kp, Ki, Kd - tune on real hardware
    }

    // Initialize CAN-FD bridge to Qualcomm side
    can_bridge.init();

    Serial.println("Ready. Waiting for commands via CAN-FD.");
}

void loop() {
    unsigned long now = millis();

    // Check safety systems (highest priority)
    safety.update();
    if (safety.is_emergency_stop()) {
        for (int i = 0; i < 4; i++) {
            motors[i].stop();
        }
        return;  // Skip everything else during e-stop
    }

    // Check heartbeat from Qualcomm side
    if (can_bridge.has_new_heartbeat()) {
        last_heartbeat_rx = now;
    }
    if (now - last_heartbeat_rx > SCOUT_HEARTBEAT_TIMEOUT_MS) {
        // Lost communication with brain - enter safe mode
        safety.enter_safe_mode("Heartbeat lost");
        return;
    }

    // Process incoming CAN-FD commands
    can_bridge.process_incoming();

    // PID velocity control loop at 100 Hz
    if (now - last_pid_update >= PID_INTERVAL_MS) {
        last_pid_update = now;

        for (int i = 0; i < 4; i++) {
            float target_vel = can_bridge.get_target_velocity(i);
            float actual_vel = encoders[i].get_velocity();
            float output = pid[i].compute(target_vel, actual_vel);
            motors[i].set_pwm(output);
        }

        // Send encoder data back to Qualcomm side
        can_bridge.send_odometry(encoders);
    }

    // Send sensor data periodically
    can_bridge.send_battery_status(safety.get_battery_voltage());
    can_bridge.send_cliff_status(safety.get_cliff_readings());

    // Pet the watchdog
    safety.feed_watchdog();
}

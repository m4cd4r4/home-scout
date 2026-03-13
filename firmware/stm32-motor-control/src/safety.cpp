#include "safety.h"
#include <Arduino.h>

// Pin assignments - update for VENTUNO Q
static const int PIN_ESTOP = 10;
static const int PIN_CLIFF_LEFT = A0;
static const int PIN_CLIFF_RIGHT = A1;
static const int PIN_MOTOR_RELAY = 11;

// ISR for emergency stop button
static volatile bool estop_triggered = false;
void estop_isr() {
    estop_triggered = true;
}

void Safety::init() {
    // Emergency stop button - hardware interrupt, highest priority
    pinMode(PIN_ESTOP, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(PIN_ESTOP), estop_isr, FALLING);

    // Cliff sensors - analog input
    pinMode(PIN_CLIFF_LEFT, INPUT);
    pinMode(PIN_CLIFF_RIGHT, INPUT);

    // Motor relay - starts OFF (motors disabled until first heartbeat)
    pinMode(PIN_MOTOR_RELAY, OUTPUT);
    open_motor_relay();

    // TODO: Initialize hardware watchdog (IWDG)
    // STM32H5 has independent watchdog with 100ms timeout
    // If main loop hangs, MCU resets and all motors stop

    Serial.println("Safety systems initialized");
}

void Safety::update() {
    // Check e-stop (hardware interrupt already caught it, just read flag)
    if (estop_triggered) {
        emergency_stop_ = true;
        open_motor_relay();
        Serial.println("E-STOP ACTIVATED");
    }

    // Check cliff sensors
    check_cliff_sensors();

    // Check battery
    check_battery();
}

void Safety::feed_watchdog() {
    // TODO: Pet the IWDG watchdog
    // HAL_IWDG_Refresh(&hiwdg);
}

bool Safety::is_emergency_stop() const {
    return emergency_stop_ || safe_mode_;
}

void Safety::enter_safe_mode(const char* reason) {
    safe_mode_ = true;
    open_motor_relay();
    Serial.print("SAFE MODE: ");
    Serial.println(reason);
    // TODO: Flash red LEDs
    // TODO: Play pre-loaded "Scout needs help" audio clip
}

float Safety::get_battery_voltage() const {
    return battery_voltage_;
}

const int* Safety::get_cliff_readings() const {
    return cliff_readings_;
}

void Safety::check_cliff_sensors() {
    cliff_readings_[0] = analogRead(PIN_CLIFF_LEFT);
    cliff_readings_[1] = analogRead(PIN_CLIFF_RIGHT);

    // Low reading = no floor reflection = cliff detected
    if (cliff_readings_[0] < SCOUT_CLIFF_THRESHOLD ||
        cliff_readings_[1] < SCOUT_CLIFF_THRESHOLD) {
        enter_safe_mode("Cliff detected");
    }
}

void Safety::check_battery() {
    // TODO: Read INA219 via I2C for accurate voltage/current
    // For now, placeholder
    battery_voltage_ = 14.8;
}

void Safety::open_motor_relay() {
    digitalWrite(PIN_MOTOR_RELAY, LOW);  // Open relay = motors disconnected
}

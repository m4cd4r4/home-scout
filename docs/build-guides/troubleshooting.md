# Troubleshooting

## Phase 1: Voice

### Microphone not detected

```bash
# Check I2S devices
arecord -l

# If no devices listed, check wiring:
# - VDD to 3.3V (not 5V!)
# - SCK to I2S_BCLK
# - WS to I2S_WS
# - SD to I2S_DIN
```

### No audio output

```bash
# Check speaker device
aplay -l

# Test with a WAV file
aplay -D plughw:0,0 /usr/share/sounds/alsa/Front_Center.wav

# If silent, check MAX98357A wiring:
# - VIN to 5V
# - DIN to I2S_DOUT
# - BCLK and LRC match microphone
```

### Wake word not triggering

- Speak clearly within 1-2 meters of the microphone
- Say "Hey Scout" with a brief pause after "Hey"
- Check microphone gain: `alsamixer`
- Verify the wake word model loaded: `ros2 topic echo /scout/wake_detected`

### ASR transcription is inaccurate

- Reduce background noise
- Speak at normal pace, don't rush
- Check NPU utilization - if overloaded, ASR quality drops
- Try re-downloading the Whisper model: `./scripts/download-models.sh`

### TTS audio is garbled or choppy

- Check CPU usage: `htop` - Piper runs on CPU, not NPU
- Reduce TTS speaking rate in params
- Ensure the speaker is properly connected and not loose

## Phase 2: Vision

### Camera not detected

```bash
# List video devices
v4l2-ctl --list-devices

# Check CSI connection - ribbon cable must be firmly seated
# Check that you're using CSI-0 (not CSI-1)
```

### Object detection is slow

- Default rate is 2 Hz - this is normal for NPU inference
- Check NPU temperature: `cat /sys/class/thermal/thermal_zone*/temp`
- If NPU is throttling, improve chassis ventilation

### Objects not recognized

- SmolVLM works best with common household objects
- Ensure good lighting - no deep shadows
- Move objects closer to the camera
- Lower the confidence threshold: `ros2 param set /scout/detector confidence_threshold 0.25`

## Phase 3: Mobility

### Motors not spinning

1. Check battery voltage: should be 14.0-16.8V for 4S LiPo
2. Check the inline fuse - may be blown
3. Verify STM32H5 firmware is flashed: `pio run --target upload`
4. Check CAN-FD connection between Qualcomm and STM32H5
5. Try manual motor test: `ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.1}}" -1`

### Scout drifts to one side

- PID needs tuning. See [STM32 Firmware Reference](../reference/stm32-firmware.md)
- Check that all 4 wheel encoders are reporting similar values
- Verify wheels spin freely when lifted

### SLAM map is poor quality

- Move slowly during mapping (max 0.1 m/s)
- Ensure LIDAR has clear line of sight (check mounting height)
- Avoid mapping in very large open spaces - add features if needed
- Check IMU calibration: `ros2 topic echo /scout/imu/data`

### Cliff sensor false triggers

- Clean the sensor lens with a soft cloth
- Adjust threshold in firmware: `CLIFF_THRESHOLD_MM` in `safety.h`
- Dark carpets can trigger cliff sensors - adjust for your floor type

### E-stop doesn't work

This is a safety-critical issue. **Stop using Scout until resolved.**
- Check wiring from button to STM32H5 EXTI pin
- Verify in firmware that the interrupt is configured as falling edge
- Test with multimeter: button should pull the pin to GND when pressed

## Phase 4: Memory

### "I don't know where that is"

- Scout needs to have seen the object during a patrol first
- Check that detections are being recorded: `ros2 topic echo /scout/sightings`
- Verify the object alias exists in the database
- Check retention settings - old sightings may have expired

### Wrong room assignment

- Room polygons may not match your SLAM map
- Re-check polygon coordinates in `config/room-maps/`
- Run the room mapping setup again if your furniture has moved significantly

## Phase 5: Faces

### Face not recognized

- Re-enroll with better lighting
- Ensure the camera captures faces from multiple angles during enrollment
- Lower match threshold: `ros2 param set /scout/recognition match_threshold 0.5`
- Check that the encryption key file exists and is readable

### Frequent misidentification

- Raise match threshold: `ros2 param set /scout/recognition match_threshold 0.7`
- Re-enroll the confused individuals with more samples
- Ensure good, even lighting during both enrollment and recognition

## General

### High CPU/NPU temperature

- Check that chassis ventilation holes are not blocked
- Reduce vision inference rate
- Add a small heatsink to the VENTUNO Q if needed
- Check ambient temperature - avoid direct sunlight

### Out of disk space

```bash
df -h /home/scout/data

# Purge old sightings
sqlite3 /home/scout/data/scout_memory.db "DELETE FROM object_sightings WHERE timestamp < datetime('now', '-30 days');"

# Check model sizes
du -sh /home/scout/models/*
```

### ROS 2 node crashes

```bash
# Check node status
ros2 node list

# View crash logs
journalctl -u scout -n 100

# Restart individual node
ros2 run scout_voice wake_word_node
```

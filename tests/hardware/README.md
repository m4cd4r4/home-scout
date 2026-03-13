# Hardware Tests

Tests that run on the physical Scout robot or require real hardware peripherals. These are manual or semi-automated checks run during hardware bring-up and before deployment.

## Scope

- **Motor control** - Verify wheel encoders, PWM signals, and odometry accuracy over a measured distance.
- **Sensors** - Check LiDAR returns, depth camera frames, IMU readings, cliff sensors, and bumper contacts.
- **NPU inference** - Run the ONNX object detection model on the Qualcomm QCS6490 NPU and verify latency and output format.
- **Audio** - Wake word detection on the physical microphone array. TTS playback through the speaker.
- **Power** - Battery voltage monitoring, charge state reporting, safe shutdown on low battery.
- **Connectivity** - Wi-Fi connection to home network, mDNS discovery, API reachability.

## Running

Hardware tests require SSH access to the robot:

```bash
# SSH into Scout
ssh scout@scout.local

# Run hardware checks
cd ~/ros2_ws
pytest tests/hardware/ -v -s --timeout=60
```

The `-s` flag is important - these tests print real-time sensor values to the console for visual verification.

## Test Categories

### Automated Checks

These run without human intervention and return pass/fail:

| Test | What It Verifies |
|------|-----------------|
| `test_lidar_scan.py` | LiDAR publishes scans at expected rate, range values are sane |
| `test_camera_feed.py` | Camera node publishes frames, resolution matches config |
| `test_imu_readings.py` | IMU reports gravity vector within tolerance |
| `test_npu_inference.py` | Model loads on NPU, inference completes < 50ms |
| `test_battery_monitor.py` | Battery voltage reads within expected range |

### Manual Verification

These require a human to observe physical behavior:

| Test | What To Check |
|------|--------------|
| `test_drive_square.py` | Robot drives a 1m square - verify it returns close to start position |
| `test_cliff_stop.py` | Place robot near table edge - verify it stops before the edge |
| `test_wake_word_live.py` | Say "Hey Scout" from 1m, 2m, 3m - verify detection at each distance |
| `test_speaker_volume.py` | TTS plays a test phrase - verify audibility and clarity |

## Safety

- Always run hardware tests in a clear area with at least 2m of open space.
- Keep the emergency stop button accessible.
- `test_drive_*` tests have a 10-second watchdog timer - the robot stops automatically if the test hangs.
- Never run motor tests while the robot is elevated or on a table.

## File Naming

```
tests/hardware/
  test_lidar_scan.py
  test_camera_feed.py
  test_imu_readings.py
  test_npu_inference.py
  test_battery_monitor.py
  test_drive_square.py
  test_cliff_stop.py
  test_wake_word_live.py
  test_speaker_volume.py
```

## Dependencies

- Physical Scout robot with all sensors connected
- SSH access to the robot
- `pytest` with `pytest-timeout`
- ROS 2 Jazzy running on the robot

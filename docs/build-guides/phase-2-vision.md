# Phase 2: Scout Can See

After this phase, Scout can detect and identify household objects using a camera and on-device VLM inference. Combined with Phase 1, Scout can now answer "What do you see?" and start building object awareness.

## What You Need (Phase 2 additions)

| Part | Model | Cost |
|------|-------|------|
| Object camera | Arducam IMX477 HQ MIPI-CSI | ~$60 |
| CSI ribbon cable | 15-pin, 200mm | ~$3 |
| Camera mount | 3D printed (see hardware/mounts/camera-mount/) | ~$1 filament |

**Phase 2 total: ~$64** (cumulative: ~$426)

## Step 1: Connect the Camera

1. Power off the VENTUNO Q
2. Connect the Arducam IMX477 to the MIPI-CSI connector using the ribbon cable
3. Mount the camera on the chassis top plate (or just prop it up for testing)

!!! note
    The VENTUNO Q has two MIPI-CSI connectors. Use CSI-0 for the main object detection camera. CSI-1 is reserved for the navigation camera in Phase 3.

## Step 2: Verify Camera

```bash
# Check the camera is detected
v4l2-ctl --list-devices

# Capture a test frame
v4l2-ctl --device=/dev/video0 --stream-mmap --stream-count=1 --stream-to=test.raw
```

## Step 3: Download Vision Model

If you haven't already downloaded models:

```bash
./scripts/download-models.sh /home/scout/models
```

This includes SmolVLM-256M (~1.5GB) optimized for the Qualcomm NPU.

## Step 4: Launch Scout with Vision

```bash
source /opt/ros/jazzy/setup.bash
source ~/home-scout/ros2_ws/install/setup.bash
ros2 launch scout_bringup scout_full.launch.py enable_vision:=true enable_nav:=false
```

## Step 5: Test Object Detection

Place common objects in front of the camera and test:

```bash
# Watch detected objects in real time
ros2 topic echo /scout/detections

# Ask Scout what it sees
# "Hey Scout, what do you see?"
# "Hey Scout, what's on the table?"
```

## Step 6: Tune Detection

Edit detection parameters:

```bash
# Adjust confidence threshold (default: 0.4)
ros2 param set /scout/detector confidence_threshold 0.3

# Adjust detection rate (default: 2.0 Hz)
ros2 param set /scout/detector rate_hz 1.0
```

## Test It

- Place a cup, phone, and book in front of Scout
- "Hey Scout, what do you see?" - Should list detected objects
- Move objects around - tracker should maintain stable IDs
- Check NPU usage: `cat /sys/class/thermal/thermal_zone*/temp`

## What's Next

[Phase 3: Scout Can Move](phase-3-mobility.md) - add wheels, motors, and autonomous navigation.

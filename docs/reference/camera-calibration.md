# Camera Calibration

Accurate camera calibration is required for object localization (Phase 4) and face recognition (Phase 5). This guide covers calibrating the onboard MIPI-CSI camera and the ESP32-S3-CAM room cameras, correcting lens distortion, and publishing calibration data in the format ROS 2 expects.

## Why Calibrate?

All camera lenses introduce distortion. Wide-angle lenses (like the 120-degree IMX219) distort heavily near the edges. Without calibration:

- Object position estimates are inaccurate (especially at frame edges)
- SLAM visual odometry drifts
- Face recognition embedding quality degrades at non-center positions

Calibration computes two things:

1. **Intrinsic parameters** - focal length, optical center, distortion coefficients. These are properties of the camera + lens.
2. **Extrinsic parameters** - position and orientation of the camera relative to Scout's base frame. These are properties of where you mounted the camera.

---

## Prerequisites

- OpenCV 4.x installed (`sudo apt install -y python3-opencv`)
- A printed checkerboard calibration target (see below)
- The camera physically connected and working (see [VENTUNO Q Setup](ventuno-q-setup.md))

### Calibration Target

Print a checkerboard pattern on a rigid flat surface. Do not use a regular sheet of paper - it bends and ruins calibration accuracy.

**Recommended target:**

- 9x6 inner corners (10x7 squares)
- 25mm square size
- Printed on foam board, acrylic, or glued to a flat piece of MDF
- Black and white with sharp edges (laser print, not inkjet)

Download a ready-to-print checkerboard PDF:

```bash
# Generate a checkerboard image with OpenCV
python3 -c "
import numpy as np
import cv2
rows, cols, size = 7, 10, 80  # 80px per square for printing
img = np.zeros((rows * size, cols * size), dtype=np.uint8)
for r in range(rows):
    for c in range(cols):
        if (r + c) % 2 == 0:
            img[r*size:(r+1)*size, c*size:(c+1)*size] = 255
cv2.imwrite('checkerboard_10x7.png', img)
print('Saved checkerboard_10x7.png - print at 100% scale')
"
```

Measure the actual printed square size with calipers. The exact measurement matters more than hitting exactly 25mm.

---

## Calibrating the MIPI-CSI Camera (Onboard)

### Step 1: Capture calibration images

Capture 20-30 images of the checkerboard from different angles and positions. Cover the full field of view, including corners and edges.

```bash
# Start the camera node
ros2 run scout_vision camera_node --ros-args -p resolution:="640x480"

# In another terminal, run the calibration image capture tool
ros2 run scout_vision calibration_capture \
  --ros-args \
  -p output_dir:=/home/scout/calibration/mipi_csi \
  -p checkerboard_rows:=6 \
  -p checkerboard_cols:=9 \
  -p num_images:=25
```

The capture tool displays a live preview. It waits for the checkerboard to be detected, then captures a frame when you press SPACE. Move the checkerboard between captures to cover:

- Center of frame
- All four corners
- Close up (fills ~80% of frame)
- Far away (fills ~20% of frame)
- Tilted at various angles (up to ~45 degrees)

### Step 2: Run calibration

```bash
python3 scripts/calibrate_camera.py \
  --input /home/scout/calibration/mipi_csi \
  --output config/camera/mipi_csi.yaml \
  --rows 6 \
  --cols 9 \
  --square-size 0.025  # 25mm in meters
```

### Step 3: Verify calibration

```bash
python3 scripts/calibrate_camera.py \
  --verify \
  --calibration config/camera/mipi_csi.yaml \
  --input /home/scout/calibration/mipi_csi
```

This undistorts each calibration image and displays it. Straight lines in the real world should appear straight in the undistorted image. The script also reports the mean reprojection error.

**Target reprojection error:** below 0.5 pixels. If above 1.0 pixel, recapture with better coverage or a flatter calibration target.

---

## Calibrating ESP32-S3-CAM Room Cameras

Each ESP32-CAM has its own lens and needs independent calibration.

### Step 1: Capture images from the ESP32-CAM

The ESP32-CAMs serve MJPEG streams over ScoutNet. Capture frames from the stream:

```bash
# Replace 10.0.77.11 with your ESP32-CAM's IP
python3 scripts/capture_from_mjpeg.py \
  --url http://10.0.77.11/stream \
  --output /home/scout/calibration/esp32_cam_1 \
  --count 25
```

Hold the checkerboard in front of the room camera and press SPACE to capture each frame. Follow the same coverage guidelines as above.

### Step 2: Run calibration

```bash
python3 scripts/calibrate_camera.py \
  --input /home/scout/calibration/esp32_cam_1 \
  --output config/camera/esp32_cam_1.yaml \
  --rows 6 \
  --cols 9 \
  --square-size 0.025
```

Repeat for each ESP32-CAM (esp32_cam_2, esp32_cam_3, esp32_cam_4).

---

## Calibration with OpenCV Directly

If you prefer to run calibration outside of the Scout tooling, here is the OpenCV approach:

```python
import cv2
import numpy as np
import glob
import yaml

# Checkerboard dimensions (inner corners)
ROWS = 6
COLS = 9
SQUARE_SIZE = 0.025  # meters

# Prepare object points (3D points in real world space)
objp = np.zeros((ROWS * COLS, 3), np.float32)
objp[:, :2] = np.mgrid[0:COLS, 0:ROWS].T.reshape(-1, 2) * SQUARE_SIZE

obj_points = []  # 3D points
img_points = []  # 2D points in image plane

images = sorted(glob.glob("/home/scout/calibration/mipi_csi/*.png"))

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    found, corners = cv2.findChessboardCorners(gray, (COLS, ROWS), None)
    if found:
        # Refine corner positions to sub-pixel accuracy
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        obj_points.append(objp)
        img_points.append(corners)

# Calibrate
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
    obj_points, img_points, gray.shape[::-1], None, None
)

print(f"Reprojection error: {ret:.4f} pixels")
print(f"Camera matrix:\n{mtx}")
print(f"Distortion coefficients: {dist.ravel()}")

# Save in ROS 2 camera_info format
calibration = {
    "image_width": gray.shape[1],
    "image_height": gray.shape[0],
    "camera_name": "mipi_csi",
    "camera_matrix": {
        "rows": 3, "cols": 3,
        "data": mtx.flatten().tolist()
    },
    "distortion_model": "plumb_bob",
    "distortion_coefficients": {
        "rows": 1, "cols": 5,
        "data": dist.ravel().tolist()
    },
    "rectification_matrix": {
        "rows": 3, "cols": 3,
        "data": np.eye(3).flatten().tolist()
    },
    "projection_matrix": {
        "rows": 3, "cols": 4,
        "data": np.hstack([mtx, np.zeros((3, 1))]).flatten().tolist()
    }
}

with open("config/camera/mipi_csi.yaml", "w") as f:
    yaml.dump(calibration, f, default_flow_style=False)

print("Calibration saved to config/camera/mipi_csi.yaml")
```

---

## Calibration Data Format (ROS 2)

Scout uses the standard ROS 2 `sensor_msgs/CameraInfo` format. The calibration YAML file looks like this:

```yaml
image_width: 640
image_height: 480
camera_name: mipi_csi
camera_matrix:
  rows: 3
  cols: 3
  data: [525.4, 0.0, 320.1,
         0.0, 524.8, 241.3,
         0.0, 0.0, 1.0]
distortion_model: plumb_bob
distortion_coefficients:
  rows: 1
  cols: 5
  data: [-0.2834, 0.0712, -0.0008, 0.0012, 0.0]
rectification_matrix:
  rows: 3
  cols: 3
  data: [1.0, 0.0, 0.0,
         0.0, 1.0, 0.0,
         0.0, 0.0, 1.0]
projection_matrix:
  rows: 3
  cols: 4
  data: [525.4, 0.0, 320.1, 0.0,
         0.0, 524.8, 241.3, 0.0,
         0.0, 0.0, 1.0, 0.0]
```

### Field descriptions

| Field | Description |
|-------|-------------|
| `camera_matrix` | 3x3 intrinsic matrix. Contains focal lengths (fx, fy) and optical center (cx, cy). |
| `distortion_model` | `plumb_bob` for standard 5-parameter radial-tangential model. |
| `distortion_coefficients` | [k1, k2, p1, p2, k3] - radial (k) and tangential (p) distortion. |
| `rectification_matrix` | 3x3 identity for monocular cameras. Used for stereo rectification. |
| `projection_matrix` | 3x4 projection matrix. For monocular, this is the camera matrix with a zero column appended. |

### Loading calibration in a ROS 2 node

```python
from sensor_msgs.msg import CameraInfo
import yaml

def load_camera_info(yaml_path: str) -> CameraInfo:
    with open(yaml_path) as f:
        cal = yaml.safe_load(f)

    info = CameraInfo()
    info.width = cal["image_width"]
    info.height = cal["image_height"]
    info.distortion_model = cal["distortion_model"]
    info.d = cal["distortion_coefficients"]["data"]
    info.k = cal["camera_matrix"]["data"]
    info.r = cal["rectification_matrix"]["data"]
    info.p = cal["projection_matrix"]["data"]
    return info
```

The `camera_node` publishes `CameraInfo` messages alongside `Image` messages on the `/scout/camera/camera_info` topic.

---

## Lens Distortion Correction

### Understanding distortion types

**Radial distortion** (barrel/pincushion): straight lines appear curved, especially near frame edges. The 120-degree IMX219 has significant barrel distortion. Coefficients k1, k2, k3 model this.

**Tangential distortion**: caused by the lens not being perfectly parallel to the sensor. Coefficients p1, p2 model this. Usually small.

### Undistortion in the pipeline

Scout undistorts frames before running object detection and face recognition. This happens in the `camera_node`:

```python
import cv2
import numpy as np

# Load calibration
mtx = np.array(camera_info.k).reshape(3, 3)
dist = np.array(camera_info.d)

# Compute optimal new camera matrix (once, at startup)
new_mtx, roi = cv2.getOptimalNewCameraMatrix(
    mtx, dist, (width, height), alpha=0.0
)

# Precompute undistortion maps (once, at startup)
map1, map2 = cv2.initUndistortRectifyMap(
    mtx, dist, None, new_mtx, (width, height), cv2.CV_16SC2
)

# Undistort each frame (fast - uses precomputed maps)
undistorted = cv2.remap(frame, map1, map2, cv2.INTER_LINEAR)
```

Setting `alpha=0.0` crops the undistorted image to remove black borders. Set `alpha=1.0` to keep the full field of view (with black borders at edges).

---

## ESP32-CAM and MIPI-CSI Alignment

When Scout uses both the onboard MIPI-CSI camera and ESP32-CAM room cameras to track objects, it needs to know where each camera is in the map frame.

### MIPI-CSI extrinsics

The onboard camera moves with Scout. Its position relative to Scout's base frame is defined in the URDF:

```xml
<!-- ros2_ws/src/scout_description/urdf/scout.urdf.xacro -->
<link name="camera_link">
  <visual>
    <geometry><box size="0.025 0.025 0.025"/></geometry>
  </visual>
</link>

<joint name="camera_joint" type="fixed">
  <parent link="base_link"/>
  <child link="camera_link"/>
  <!-- Camera mounted 15cm above base, 10cm forward, looking forward -->
  <origin xyz="0.10 0.0 0.15" rpy="0 0 0"/>
</joint>
```

Measure the actual camera position on your build and update these values.

### ESP32-CAM extrinsics

Room cameras are fixed in the world. Their positions are defined in the room map configuration:

```yaml
# config/room-maps/living_room.yaml
cameras:
  - name: esp32_cam_1
    ip: 10.0.77.11
    calibration: config/camera/esp32_cam_1.yaml
    position:
      x: 3.2    # meters from map origin
      y: 1.5
      z: 2.1    # height (mounted on wall)
    orientation:
      roll: 0.0
      pitch: -0.35  # tilted down ~20 degrees
      yaw: 1.57     # facing into the room
```

These extrinsics are set manually when you mount the cameras. Use a tape measure for position. Estimate orientation visually - the object memory system tolerates moderate angular error because it merges sightings across multiple frames and cameras.

---

## Recalibration

Recalibrate when:

- You change the camera module or lens
- You change the camera resolution setting
- You physically move or remount a camera
- Reprojection error degrades (check with `scout-cli camera verify`)

For room cameras, recalibrating extrinsics (position/orientation) is usually more important than recalibrating intrinsics. The lens properties do not change unless you swap the camera module.

---

## Troubleshooting

### Checkerboard not detected in some images

- Make sure the entire checkerboard is visible in the frame
- Avoid glare and shadows on the checkerboard surface
- Use even lighting - avoid bright spots and dark corners
- Print on matte paper or board, not glossy

### High reprojection error (> 1.0 pixel)

- Check that your checkerboard is flat (tape it to a rigid board)
- Verify the square size measurement is accurate
- Capture more images with better angle diversity
- Remove any blurry images from the calibration set

### Undistorted images look wrong

- Double-check rows/cols count (count inner corners, not squares)
- Verify the calibration YAML was written correctly
- Try recalibrating with a fresh set of images

---

## Related Documentation

- [VENTUNO Q Setup](ventuno-q-setup.md) - camera hardware connection
- [Room Mapping](../design/room-mapping.md) - how room cameras integrate with the spatial map
- [Architecture](../ARCHITECTURE.md) - vision pipeline overview

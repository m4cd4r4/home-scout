# Contributing Software

Scout's software stack covers ROS 2 nodes (Python), STM32/ESP32 firmware (C++), simulation environments, tests, and developer tooling. This guide covers the package structure, code style, testing requirements, and the simulation-first development approach.

---

## Development Setup

### Docker (recommended)

One command gets you a full environment with ROS 2 Jazzy, PlatformIO, Python tools, and a pre-built workspace.

```bash
git clone https://github.com/m4cd4r4/home-scout.git
cd home-scout
docker compose -f docker/docker-compose.dev.yml up
```

Your local files sync into the container. Edit on your host, build and run inside the container.

### Manual setup

If you prefer a native install:

```bash
# Ubuntu 24.04 required (or WSL2 with Ubuntu 24.04)

# Install ROS 2 Jazzy
sudo apt install -y ros-jazzy-desktop python3-colcon-common-extensions python3-rosdep

# Clone and build
git clone https://github.com/m4cd4r4/home-scout.git
cd home-scout/ros2_ws
rosdep install --from-paths src --ignore-src -y
colcon build --symlink-install
source install/setup.bash

# Install Python tools
pip install ruff mypy pytest pytest-cov

# Install PlatformIO (for firmware)
pip install platformio
```

---

## ROS 2 Package Structure

All ROS 2 packages live in `ros2_ws/src/` and follow a consistent layout.

```
ros2_ws/src/
  scout_interfaces/          # Shared message, service, and action definitions
    msg/
      ObjectSighting.msg
      BatteryStatus.msg
    srv/
      WhereIs.srv
      EnrollFace.srv
      LoadPersonality.srv
    action/
      Patrol.action
    package.xml
    CMakeLists.txt

  scout_bringup/             # Launch files and top-level configuration
    launch/
      scout_voice_only.launch.py
      scout_full.launch.py
      simulation.launch.py
    config/
    package.xml
    setup.py

  scout_voice/               # Phase 1: voice pipeline
    scout_voice/
      __init__.py
      wake_word_node.py
      asr_node.py
      conversation_node.py
      tts_node.py
    test/
      test_wake_word.py
      test_asr.py
      test_conversation.py
    package.xml
    setup.py
    setup.cfg

  scout_vision/              # Phase 2: camera and detection
  scout_nav/                 # Phase 3: navigation and motor bridge
  scout_memory/              # Phase 4: object memory
  scout_faces/               # Phase 5: face recognition
  scout_description/         # URDF robot model
  scout_simulation/          # Gazebo worlds and simulation launch
```

### Package naming

- All packages: `scout_*` prefix
- Node names: descriptive, `snake_case` (e.g., `wake_word_detector`, `object_memory_node`)
- Topic names: namespaced under `/scout/` (e.g., `/scout/voice/wake_word`, `/scout/vision/detections`)
- Service names: namespaced under `/scout/` (e.g., `/scout/memory/where_is`)

### Adding a new package

```bash
cd ros2_ws/src
ros2 pkg create scout_your_feature \
  --build-type ament_python \
  --dependencies rclpy std_msgs scout_interfaces
```

Follow the existing package layout. Include a `test/` directory with at least one test file.

---

## Python Code Style

### Tooling

| Tool | Purpose | Config |
|------|---------|--------|
| `ruff` | Linter and formatter | `pyproject.toml` |
| `mypy` | Static type checker | `pyproject.toml` |
| `pytest` | Test runner | `setup.cfg` |
| `pytest-cov` | Coverage measurement | `setup.cfg` |

### Running the tools

```bash
# Format
ruff format .

# Lint
ruff check .

# Type check
mypy ros2_ws/src --strict

# All three (this is what CI runs)
ruff format --check . && ruff check . && mypy ros2_ws/src --strict
```

### Style rules

**Line length:** 88 characters (ruff default).

**Imports:** sorted by ruff. Standard library first, then third-party, then local.

**Type hints:** required on all function signatures. Use `mypy --strict`.

```python
def detect_objects(
    frame: np.ndarray,
    confidence_threshold: float = 0.5,
    max_detections: int = 20,
) -> list[Detection]:
    """Run object detection on a single frame.

    Args:
        frame: BGR image as a numpy array.
        confidence_threshold: Minimum confidence to keep a detection.
        max_detections: Maximum number of detections to return.

    Returns:
        List of detections sorted by confidence (highest first).
    """
    ...
```

**Docstrings:** Google style. Required on all public functions and classes.

**Naming:**
- Variables and functions: `snake_case`
- Classes: `PascalCase`
- Constants: `SCREAMING_SNAKE_CASE`
- Private methods: single underscore prefix (`_process_frame`)

**ROS 2 node pattern:**

```python
import rclpy
from rclpy.node import Node
from scout_interfaces.msg import ObjectSighting


class ObjectMemoryNode(Node):
    """Stores and queries object sighting history."""

    def __init__(self) -> None:
        super().__init__("object_memory_node")

        # Declare parameters with defaults
        self.declare_parameter("db_path", "/home/scout/data/scout.db")
        self.declare_parameter("decay_interval_s", 3600)

        # Subscriptions
        self.create_subscription(
            ObjectSighting,
            "/scout/vision/sightings",
            self._on_sighting,
            10,
        )

        # Services
        self.create_service(
            WhereIs,
            "/scout/memory/where_is",
            self._handle_where_is,
        )

        self.get_logger().info("Object memory node started")

    def _on_sighting(self, msg: ObjectSighting) -> None:
        ...

    def _handle_where_is(
        self, request: WhereIs.Request, response: WhereIs.Response
    ) -> WhereIs.Response:
        ...


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = ObjectMemoryNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
```

---

## C++ Code Style (Firmware)

Firmware for the STM32H5 and ESP32 uses C++.

### Tooling

| Tool | Purpose | Config |
|------|---------|--------|
| `clang-format` | Formatter | `.clang-format` |
| PlatformIO | Build system | `platformio.ini` |
| Unity | Test framework | `platformio.ini` (native env) |

### Running the tools

```bash
# Format
find firmware/ -name "*.cpp" -o -name "*.h" | xargs clang-format -i

# Build
cd firmware/stm32-motor-control && pio run
cd firmware/esp32-cam && pio run

# Test (native, no hardware needed)
cd firmware/stm32-motor-control && pio test -e native
```

### Style rules

- `snake_case` for functions and variables
- `PascalCase` for types and structs
- `SCREAMING_SNAKE_CASE` for constants and macros
- Braces on same line for functions and control flow
- Max line length: 100 characters

```cpp
struct MotorState {
    float target_rpm;
    float actual_rpm;
    float pwm_duty;
    uint32_t encoder_ticks;
};

void update_pid(MotorState* motor, float dt) {
    float error = motor->target_rpm - motor->actual_rpm;
    // ...
}
```

---

## Testing Requirements

### Coverage target

**80% minimum for new code.** This is measured per package. Existing packages may be below 80% - do not decrease their coverage.

### Test organization

Tests live alongside the code they test:

```
scout_voice/
  scout_voice/
    wake_word_node.py
  test/
    test_wake_word.py        # Unit tests for wake_word_node
    test_asr.py              # Unit tests for asr_node
    test_voice_integration.py  # Integration test for full voice pipeline
```

### Running tests

```bash
# All tests (from ros2_ws/)
colcon test
colcon test-result --verbose

# Single package
colcon test --packages-select scout_voice
colcon test-result --verbose

# With coverage
colcon test --packages-select scout_voice --pytest-args --cov=scout_voice --cov-report=term-missing
```

### Test types

**Unit tests** - test individual functions and classes in isolation. Mock ROS 2 infrastructure.

```python
# test/test_object_memory.py
from scout_memory.object_memory import ObjectMemory


def test_store_and_retrieve_sighting() -> None:
    memory = ObjectMemory(db_path=":memory:")
    memory.store_sighting(
        name="keys",
        room="kitchen",
        zone="counter_left",
        x=1.2,
        y=0.8,
        confidence=0.92,
    )

    result = memory.where_is("keys")
    assert result is not None
    assert result.room == "kitchen"
    assert result.zone == "counter_left"


def test_confidence_decay() -> None:
    memory = ObjectMemory(db_path=":memory:")
    memory.store_sighting(name="phone", room="bedroom", zone="desk", x=2.0, y=3.0, confidence=0.95)
    memory.apply_decay(hours=4)

    result = memory.where_is("phone")
    assert result is not None
    assert result.confidence < 0.95  # Should have decayed
```

**Integration tests** - test ROS 2 nodes together using launch_testing.

```python
# test/test_voice_integration.py
import launch_testing
import rclpy
from std_msgs.msg import String


def test_wake_word_triggers_asr(proc_output) -> None:
    """Publishing a wake word trigger should start ASR recording."""
    node = rclpy.create_node("test_node")
    pub = node.create_publisher(String, "/scout/voice/wake_word", 10)

    # Publish wake word trigger
    msg = String()
    msg.data = "hey scout"
    pub.publish(msg)

    # Verify ASR node started recording
    # (check for the appropriate topic or service response)
    ...
```

**Simulation tests** - test full behaviors in Gazebo simulation. These run in CI using the Docker simulation environment.

### What to test

- Business logic: object memory queries, confidence decay, room assignment, PID math
- ROS 2 node behavior: message handling, service responses, parameter changes
- Safety conditions: E-stop handling, heartbeat timeout, cliff sensor response
- Edge cases: empty database queries, malformed CAN frames, missing cameras

### What not to test

- ROS 2 framework internals (publishers, subscribers, timers)
- Third-party libraries (OpenCV, NumPy, SQLite)
- Hardware drivers (these are tested via simulation or manual hardware tests)

---

## Simulation-First Development

**All new features must work in simulation before testing on hardware.** This is a hard requirement.

### Why simulation first

1. Not every contributor has a VENTUNO Q board
2. Hardware testing is slow (flash, boot, test, reflash)
3. Simulation lets you test dangerous scenarios safely (cliffs, collisions, battery failures)
4. CI runs simulation tests automatically on every PR

### Running the simulation

```bash
# Full simulation with Gazebo
ros2 launch scout_bringup simulation.launch.py

# Simulation with specific world
ros2 launch scout_bringup simulation.launch.py world:=small_apartment

# Headless simulation (CI mode, no GUI)
ros2 launch scout_bringup simulation.launch.py gui:=false
```

### Simulation worlds

Pre-built Gazebo worlds are in `ros2_ws/src/scout_simulation/worlds/`:

| World | Description | Use for |
|-------|-------------|---------|
| `small_apartment.sdf` | 3-room apartment with furniture | General navigation, object detection |
| `open_floor.sdf` | Single large room, no obstacles | Motor tuning, SLAM mapping |
| `obstacle_course.sdf` | Dense obstacle field | Obstacle avoidance, safety testing |
| `multi_floor.sdf` | Two floors with stairs | Cliff sensor testing |

### Adding simulation support to your feature

If your feature involves a new sensor, actuator, or behavior, add a Gazebo plugin or mock node:

```python
# scout_simulation/mock_nodes/mock_battery.py
class MockBatteryNode(Node):
    """Simulates battery drain and charging for testing."""

    def __init__(self) -> None:
        super().__init__("mock_battery")
        self.charge = 1.0  # Start full
        self.drain_rate = 0.001  # Per second
        self.create_timer(1.0, self._drain)
        self.pub = self.create_publisher(BatteryStatus, "/scout/battery", 10)

    def _drain(self) -> None:
        self.charge = max(0.0, self.charge - self.drain_rate)
        msg = BatteryStatus()
        msg.voltage = 12.0 + (self.charge * 4.8)  # 12.0V - 16.8V
        msg.charge_percent = self.charge
        self.pub.publish(msg)
```

---

## CI Pipeline

Every PR runs the following checks automatically:

| Check | Tool | Pass condition |
|-------|------|---------------|
| Python lint | `ruff check .` | No errors |
| Python format | `ruff format --check .` | No formatting changes needed |
| Python types | `mypy --strict` | No type errors |
| Python tests | `colcon test` | All tests pass |
| Python coverage | `pytest-cov` | 80%+ on changed packages |
| C++ format | `clang-format --dry-run` | No formatting changes needed |
| Firmware build | `pio run` (STM32 + ESP32) | Build succeeds |
| Firmware tests | `pio test -e native` | All tests pass |
| YAML lint | `yamllint` | No errors |
| Privacy audit | `verify-privacy.sh` (simulated) | No external network calls in codebase |
| STL validation | `admesh --check` | All STL files watertight (hardware PRs only) |
| Simulation test | Gazebo + launch_testing | Simulation tests pass |

Fix all CI failures before requesting review. If a CI check fails on something unrelated to your change, note it in the PR description.

---

## Branch Naming

| Pattern | Use for | Example |
|---------|---------|---------|
| `phase-N/feature-name` | Phase-specific features | `phase-2/tracker-improvements` |
| `firmware/description` | Firmware changes | `firmware/pid-anti-windup` |
| `fix/description` | Bug fixes | `fix/memory-query-timeout` |
| `test/description` | Test additions | `test/voice-pipeline-integration` |
| `docs/description` | Documentation | `docs/calibration-guide` |
| `ci/description` | CI/CD changes | `ci/add-coverage-report` |

Always branch from latest `main`:

```bash
git checkout main && git pull origin main
git checkout -b phase-4/memory-decay-tuning
```

---

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): short description

Optional longer description.

Refs: #123
```

Types: `feat`, `fix`, `test`, `docs`, `ci`, `chore`, `firmware`, `hardware`

Scopes: `voice`, `vision`, `nav`, `memory`, `faces`, `stm32`, `esp32`, `sim`, `bringup`

---

## PR Checklist

Before opening your PR:

- [ ] Rebased onto latest `main`
- [ ] `ruff check .` passes
- [ ] `ruff format --check .` passes
- [ ] `mypy --strict` passes (for Python changes)
- [ ] `colcon test` passes
- [ ] Coverage is 80%+ on new code
- [ ] Firmware builds cleanly (if firmware changed)
- [ ] Feature works in simulation
- [ ] Documentation updated (if user-facing change)
- [ ] No new network calls, cloud dependencies, or telemetry (privacy preserved)
- [ ] No new autonomous movement without safety review (if nav-related)

---

## Good First Issues

Look for issues labeled `good first issue`. These are well-scoped tasks that do not require hardware.

Common starter tasks:

- Add unit tests to increase coverage on an existing package
- Fix a linting or type checking issue
- Add a new Gazebo world for simulation
- Improve error messages in CLI tools
- Add parameter validation to a ROS 2 node
- Write a mock node for simulation

---

## Privacy Constraint

Scout never connects to the internet. This constraint applies to all code contributions:

- No HTTP clients, no `requests`, no `urllib` calls to external services
- No DNS lookups
- No telemetry, analytics, or crash reporting
- No phone-home, update checks, or beacon endpoints
- Any PR that introduces external network access will fail CI and will not be merged

The only allowed network traffic is on ScoutNet (10.0.77.0/24) between Scout and ESP32-CAMs.

---

## Related Documentation

- [CONTRIBUTING.md](../../CONTRIBUTING.md) - general contribution guidelines, full PR process
- [Architecture](../ARCHITECTURE.md) - system design and subsystem details
- [Hardware Contributions](hardware-contributions.md) - contributing physical designs
- [STM32 Firmware Reference](../reference/stm32-firmware.md) - firmware development details

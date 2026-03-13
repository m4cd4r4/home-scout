# Simulation Tests

Tests that run the full Scout stack inside a Gazebo simulation environment. These validate navigation, obstacle avoidance, and sensor fusion against a virtual household.

## Scope

- **Navigation** - Scout can drive through a simulated house floor plan without collisions. SLAM builds a usable map. Patrol node visits all rooms.
- **Object detection in sim** - Synthetic objects placed in the Gazebo world are detected by the vision pipeline and recorded in memory with correct room assignments.
- **End-to-end query** - After a simulated patrol, a WhereIs query returns the correct room and zone for objects placed in the scene.
- **Safety** - Cliff sensors and bumper contacts trigger emergency stop. Scout does not fall off simulated ledges.

## Gazebo World

The simulation uses `scout_simulation/worlds/test_house.world` - a simple rectangular floor plan with:
- 3 rooms (kitchen, living room, bedroom) matching the polygon definitions in the spatial index
- Furniture models (table, couch, chairs) as static obstacles
- Small objects (phone, keys, book) placed on surfaces
- A simulated depth camera and LiDAR on the robot model

## Running

```bash
# Build simulation package
colcon build --packages-select scout_simulation

# Launch Gazebo with the test house
ros2 launch scout_simulation gazebo_house.launch.py headless:=true

# Run simulation tests (separate terminal)
pytest tests/simulation/ -v --timeout=120
```

## CI Considerations

- Simulation tests are slow (30-120 seconds each) - run nightly, not on every push.
- Use `headless:=true` to avoid needing a display server in CI.
- Gazebo requires significant memory (~2GB) - allocate accordingly in CI runners.
- Tag these tests with `@pytest.mark.simulation` for selective execution.

## File Naming

```
tests/simulation/
  test_navigation.py
  test_object_detection_sim.py
  test_end_to_end_query.py
  test_safety_stops.py
```

## Dependencies

- `gazebo_ros` (Gazebo Harmonic for ROS 2 Jazzy)
- `scout_simulation` package (world files, robot URDF)
- `pytest` with `pytest-timeout`
- No physical hardware

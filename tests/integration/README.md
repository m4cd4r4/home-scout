# Integration Tests

Tests that verify multiple Scout modules working together end-to-end, without requiring physical hardware or a live ROS 2 graph.

## Scope

Integration tests cover cross-module interactions:

- **Memory pipeline** - Object sighting flows from detection through spatial index assignment to SQLite persistence, then retrieval via the query engine with confidence decay applied.
- **Voice pipeline** - Wake word detection triggers ASR, which produces text routed to the conversation node, which queries object memory and returns a TTS response.
- **Face pipeline** - Camera frame passes through face detection, embedding generation, and database lookup to produce a greeting.
- **Navigation + Memory** - Patrol node visits rooms; object sightings are tagged with correct room/zone assignments based on the robot's pose and the spatial index.

## Approach

- Use `launch_testing` from ROS 2 to spin up subsets of the node graph in-process.
- Replace hardware drivers with mock publishers (e.g., mock camera node publishes pre-recorded frames).
- Use an in-memory SQLite database (`:memory:`) for the object memory store.
- Assert on topic messages and service responses rather than internal state.

## Running

```bash
# From the workspace root
colcon test --packages-select scout_memory scout_voice scout_faces
colcon test-result --verbose
```

## File Naming

```
tests/integration/
  test_memory_pipeline.py
  test_voice_pipeline.py
  test_face_pipeline.py
  test_patrol_memory.py
```

## Dependencies

- `pytest`
- `launch_testing` (ROS 2)
- `rclpy` (test node helpers)
- No hardware, no GPU, no network access

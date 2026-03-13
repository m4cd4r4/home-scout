# Room Mapping Design

Scout builds a map of your home using SLAM (Simultaneous Localization and Mapping). The raw SLAM output is an occupancy grid - a 2D grid of cells marked as free, occupied, or unknown. This document explains how Scout converts that grid into named rooms and zones, the polygon definition format, zone types, the initial room setup workflow, and the web UI for labeling.

---

## From Occupancy Grid to Rooms

SLAM produces a grayscale image where each pixel represents a 5cm x 5cm cell:

- **White (255)**: free space - Scout can drive here
- **Black (0)**: occupied - walls, furniture, obstacles
- **Gray (128)**: unknown - not yet explored

This grid is useful for navigation but meaningless for human queries like "Where are my keys?" People think in rooms and zones ("on the kitchen counter"), not grid coordinates (1.35, 2.87).

Scout bridges this gap with a polygon overlay system. You draw polygons on the occupancy grid to define rooms and zones. Each polygon gets a human-readable name.

```
Occupancy Grid                  Polygon Overlay
+------------------+            +------------------+
|  ######          |            |  [kitchen]       |
|  #    #  ####    |            |       [living    |
|  #    #  #  #    |            |        room]     |
|  ######  #  #    |            |                  |
|          ####    |            |  [bedroom]       |
|  ######          |            |                  |
|  #    #          |            |  [hallway]       |
|  ######          |            |                  |
+------------------+            +------------------+
```

---

## Polygon Definition Format

Room and zone polygons are defined in YAML files stored in `config/room-maps/`.

### Room map file structure

```yaml
# config/room-maps/my_house.yaml

map_file: "maps/my_house.pgm"       # SLAM-generated occupancy grid
resolution: 0.05                     # Meters per pixel
origin: [-2.5, -3.0, 0.0]           # Map origin [x, y, theta] in meters

rooms:
  - name: kitchen
    label: "Kitchen"                 # Human-readable display name
    polygon:                         # Vertices in map coordinates (meters)
      - [0.0, 0.0]
      - [0.0, 3.5]
      - [4.2, 3.5]
      - [4.2, 0.0]
    zones:
      - name: counter_left
        label: "Left counter"
        type: counter
        polygon:
          - [0.2, 0.0]
          - [0.2, 0.8]
          - [1.5, 0.8]
          - [1.5, 0.0]
      - name: counter_right
        label: "Right counter"
        type: counter
        polygon:
          - [2.5, 0.0]
          - [2.5, 0.8]
          - [4.0, 0.8]
          - [4.0, 0.0]
      - name: table
        label: "Kitchen table"
        type: desk
        polygon:
          - [1.0, 1.5]
          - [1.0, 3.0]
          - [3.0, 3.0]
          - [3.0, 1.5]

  - name: living_room
    label: "Living Room"
    polygon:
      - [4.2, 0.0]
      - [4.2, 5.0]
      - [8.0, 5.0]
      - [8.0, 0.0]
    zones:
      - name: couch
        label: "Couch"
        type: shelf        # Objects placed on furniture surfaces
        polygon:
          - [5.0, 0.5]
          - [5.0, 1.5]
          - [7.5, 1.5]
          - [7.5, 0.5]
      - name: coffee_table
        label: "Coffee table"
        type: desk
        polygon:
          - [5.5, 2.0]
          - [5.5, 3.0]
          - [7.0, 3.0]
          - [7.0, 2.0]
      - name: tv_stand
        label: "TV stand"
        type: shelf
        polygon:
          - [4.5, 4.0]
          - [4.5, 5.0]
          - [7.5, 5.0]
          - [7.5, 4.0]

  - name: hallway
    label: "Hallway"
    polygon:
      - [0.0, 3.5]
      - [0.0, 5.5]
      - [4.2, 5.5]
      - [4.2, 3.5]
    zones: []               # Hallway has no zones - objects here are just "in the hallway"

  - name: bedroom
    label: "Bedroom"
    polygon:
      - [0.0, 5.5]
      - [0.0, 9.0]
      - [4.2, 9.0]
      - [4.2, 5.5]
    zones:
      - name: bed
        label: "Bed"
        type: shelf
        polygon:
          - [0.5, 6.0]
          - [0.5, 8.5]
          - [2.5, 8.5]
          - [2.5, 6.0]
      - name: nightstand
        label: "Nightstand"
        type: shelf
        polygon:
          - [2.8, 7.5]
          - [2.8, 8.5]
          - [3.5, 8.5]
          - [3.5, 7.5]
      - name: desk
        label: "Desk"
        type: desk
        polygon:
          - [2.8, 5.8]
          - [2.8, 7.0]
          - [4.0, 7.0]
          - [4.0, 5.8]
```

### Polygon rules

- Polygons are lists of [x, y] vertices in map coordinates (meters)
- Vertices must be in order (clockwise or counter-clockwise)
- Polygons do not need to be convex
- Room polygons should not overlap (a point in two rooms creates ambiguity)
- Zone polygons must be contained within their parent room polygon
- A zone polygon can overlap other zone polygons in the same room (an object in the overlap area will be assigned to the smallest enclosing zone)

---

## Zone Types

Zone types tell Scout what kind of surface a zone represents. This affects how Scout reports object locations in natural language.

| Type | Description | Example phrase |
|------|-------------|---------------|
| `shelf` | Horizontal surface at elevation - shelves, TV stands, bed | "on the TV stand" |
| `desk` | Work surface - desks, tables | "on the kitchen table" |
| `counter` | Kitchen/bathroom counter surface | "on the left counter" |
| `floor` | Floor-level area | "on the floor in the hallway" |
| `drawer` | Not directly visible - inferred from context | "possibly in the desk drawer" |
| `wall` | Vertical surface - hooks, wall-mounted shelves | "on the wall hook" |
| `bin` | Container - baskets, trays, bins | "in the basket on the shelf" |

Zone types also affect confidence decay rates. Objects on a `desk` decay faster (people move things on desks) than objects on a `shelf` (semi-permanent placement).

---

## Initial Room Setup Workflow

When you first build Scout with Phase 3 (mobility), you need to map your home and define rooms. This is a one-time process that takes 15-30 minutes.

### Step 1: Run frontier exploration

Scout autonomously explores your home to build the SLAM map.

```bash
ros2 launch scout_nav mapping.launch.py
```

Scout drives through your home, using frontier exploration to find and map unexplored areas. Open doors to all rooms you want mapped. Close doors to rooms you want excluded.

**During exploration:**

- Stay out of Scout's path (your legs are obstacles)
- Scout will navigate around furniture - do not move furniture during mapping
- The web UI at `http://10.0.77.1:8080/map` shows the map building in real time
- Exploration finishes when no more frontiers exist (all reachable space is mapped)

```bash
# Or trigger exploration manually
ros2 service call /scout/nav/start_mapping std_srvs/srv/Trigger
```

### Step 2: Save the map

```bash
ros2 service call /scout/nav/save_map scout_interfaces/srv/SaveMap \
  "{filename: 'my_house'}"
```

This saves the occupancy grid to `maps/my_house.pgm` and metadata to `maps/my_house.yaml`.

### Step 3: Define rooms and zones

Open the room labeling web UI:

```
http://10.0.77.1:8080/room-editor
```

Or define rooms manually in YAML (see the format section above).

### Step 4: Verify room assignment

Drive Scout through each room and verify it reports the correct room:

```bash
# Check Scout's current room
ros2 topic echo /scout/localization/current_room

# Walk through rooms and verify the topic updates correctly
```

---

## Web UI for Polygon Labeling

The room editor web UI lets you draw room and zone polygons visually on top of the SLAM map.

### Accessing the editor

Connect to ScoutNet and open `http://10.0.77.1:8080/room-editor` in your browser.

### Editor features

- **Map display**: the SLAM occupancy grid as a zoomable, pannable image
- **Room drawing tool**: click vertices to draw a room polygon, double-click to close
- **Zone drawing tool**: select a room, then draw zone polygons within it
- **Name and type assignment**: click a polygon to set its name, label, and type
- **Drag to adjust**: click and drag polygon vertices to refine boundaries
- **Delete**: select a polygon and press Delete to remove it
- **Undo/redo**: Ctrl+Z / Ctrl+Y
- **Save**: saves the room map YAML to `config/room-maps/`
- **Preview**: shows room/zone names overlaid on the map

### Workflow in the editor

1. Load the SLAM map (auto-detected if only one map exists)
2. Draw room outlines first - cover all free space with room polygons
3. Name each room (click the polygon, type the name)
4. Draw zones within rooms for surfaces where objects tend to accumulate
5. Assign zone types from the dropdown
6. Save

### Coordinate system

The editor displays pixel coordinates but saves map coordinates (meters). The conversion uses the map's resolution and origin from the SLAM metadata file:

```
map_x = (pixel_x * resolution) + origin_x
map_y = (pixel_y * resolution) + origin_y
```

You do not need to do this conversion manually - the editor handles it.

---

## How Object Memory Uses Room Maps

When the `object_memory_node` receives an object sighting, it:

1. Gets Scout's current position from the `/odom` transform
2. Runs point-in-polygon tests against all room polygons
3. If a match is found, runs point-in-polygon tests against zones within that room
4. Stores the sighting with room name, zone name, and raw coordinates

```python
# Simplified point-in-polygon assignment
def assign_location(x: float, y: float, room_map: RoomMap) -> tuple[str, str]:
    for room in room_map.rooms:
        if point_in_polygon(x, y, room.polygon):
            for zone in room.zones:
                if point_in_polygon(x, y, zone.polygon):
                    return (room.name, zone.name)
            return (room.name, "")  # In room but not in a specific zone
    return ("unknown", "")  # Outside all defined rooms
```

### Natural language generation

The room and zone names feed into response templates:

- Room only: "I last saw your keys **in the kitchen** about 2 hours ago."
- Room + zone: "I last saw your keys **on the kitchen counter** about 2 hours ago."
- Unknown room: "I last saw your keys at coordinates (1.3, 2.8) about 2 hours ago." (this means you need to define more room polygons)

---

## ESP32-CAM Room Assignment

Each ESP32-CAM has a fixed room and zone assignment in its configuration:

```yaml
# config/room-maps/my_house.yaml (continued)
cameras:
  - name: esp32_cam_1
    ip: 10.0.77.11
    room: kitchen
    zone: counter_left
    calibration: config/camera/esp32_cam_1.yaml
    position:
      x: 0.5
      y: 0.4
      z: 2.1
    orientation:
      roll: 0.0
      pitch: -0.3
      yaw: 0.0
```

Objects detected by a room camera are automatically tagged with that camera's room and zone. No point-in-polygon test is needed - the room assignment is static.

---

## Updating the Room Map

### After rearranging furniture

If you move furniture, zones may need updating. Room boundaries usually stay the same.

```bash
# Re-open the editor
# Adjust zone polygons to match new furniture positions
# Save
```

### After adding a new room

If you open a previously closed door:

```bash
# Run mapping again in the new area
ros2 launch scout_nav mapping.launch.py mode:=extend

# Scout will explore the new area while preserving the existing map
# Then update room polygons in the editor
```

### After a full remap

If the map becomes inaccurate (SLAM drift, major renovations):

```bash
# Start fresh
ros2 launch scout_nav mapping.launch.py mode:=new

# Re-draw all room and zone polygons
```

---

## File Locations

| File | Location | Purpose |
|------|----------|---------|
| SLAM map (pgm) | `maps/my_house.pgm` | Occupancy grid image |
| SLAM metadata | `maps/my_house.yaml` | Resolution, origin, timestamps |
| Room map config | `config/room-maps/my_house.yaml` | Room/zone polygons and cameras |
| Geofence config | `config/geofence.yaml` | Keep-out zones (see [SAFETY.md](../../SAFETY.md)) |
| Speed zone config | `config/speed_zones.yaml` | Per-room speed limits |
| Patrol route config | `config/patrol-routes/default.yaml` | Room visit order and timing |

---

## Troubleshooting

### Scout reports "unknown" room

- Check that your room polygons cover all navigable space (no gaps between rooms)
- Verify the polygon coordinates are in map frame (meters), not pixel coordinates
- Run `scout-cli map rooms --verify` to highlight uncovered areas

### Objects assigned to wrong room

- Room polygons might overlap - check boundaries in the editor
- Scout's localization might have drifted - check SLAM accuracy with `ros2 topic echo /scout/localization/pose`
- If localization drifts consistently, consider remapping

### Zone polygons not matching furniture

- Measure furniture positions from a fixed reference point (wall corner)
- Use the editor's grid overlay for alignment
- Zone boundaries do not need to be pixel-perfect - 10-20cm margin is fine

### Map looks distorted or has artifacts

- SLAM artifacts usually come from moved objects during mapping (chairs, people)
- Remap with the space clear of moving obstacles
- Close doors to rooms you do not want mapped

---

## Related Documentation

- [Architecture](../ARCHITECTURE.md) - memory subsystem and SLAM integration
- [Personality Guide](personality-guide.md) - response templates that use room/zone names
- [Camera Calibration](../reference/camera-calibration.md) - ESP32-CAM extrinsics in room context
- [Safety](../../SAFETY.md) - geofencing and speed zones

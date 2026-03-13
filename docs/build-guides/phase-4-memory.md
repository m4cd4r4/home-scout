# Phase 4: Scout Remembers

After this phase, Scout remembers where it has seen household objects. Ask "Where are my keys?" and get an answer. This is a software-only phase - no new hardware needed.

## What You Need

Nothing new. Phase 4 is pure software running on the existing hardware from Phases 1-3.

**Phase 4 total: $0** (cumulative: ~$995)

## Step 1: Initialize the Object Database

The database is created automatically on first launch, but you can pre-populate room definitions:

```bash
# Edit room polygons (from your SLAM map)
nano ~/home-scout/config/room-maps/my_home.yaml
```

See [Room Mapping](../design/room-mapping.md) for how to define room polygons from your SLAM occupancy grid.

## Step 2: Launch with Memory Enabled

```bash
ros2 launch scout_bringup scout_full.launch.py
```

The `object_memory_node` starts automatically and begins recording sightings from the vision system.

## Step 3: Build Object Memory

Let Scout patrol normally. As it moves through rooms, the VLM detects objects and the memory system records:
- What was seen (object name)
- Where it was seen (room + zone from SLAM pose)
- When it was seen (timestamp)
- How confident the detection was

## Step 4: Add Custom Aliases

Scout understands natural language aliases. Add your own:

```sql
-- Connect to the database
sqlite3 /home/scout/data/scout_memory.db

-- Add aliases for your household items
INSERT INTO object_aliases (alias, canonical_name) VALUES ('my phone', 'phone');
INSERT INTO object_aliases (alias, canonical_name) VALUES ('the remote', 'tv remote');
INSERT INTO object_aliases (alias, canonical_name) VALUES ('dad''s glasses', 'glasses');
```

## Step 5: Configure Retention

Edit `ros2_ws/src/scout_bringup/config/scout_params.yaml`:

```yaml
scout_memory:
  default_ttl_hours: 720      # 30 days default
  decay_check_interval: 300   # Check every 5 minutes
```

## Test It

- Leave your keys on the kitchen counter
- Let Scout patrol and detect them
- Later: "Hey Scout, where are my keys?"
- Scout should respond: "I last saw your keys on the kitchen counter about 2 hours ago."

More tests:
- "Hey Scout, where's my phone?"
- "Hey Scout, have you seen the TV remote?"
- "Hey Scout, what's in the living room?"
- Move an object and ask again after the next patrol

## How Confidence Decay Works

Scout's confidence that an object is still in a location decays over time:
- **Portable items** (keys, phone, wallet): 4-hour half-life
- **Semi-fixed items** (books, bags): 24-hour half-life
- **Fixed items** (furniture, appliances): 1-week half-life

When confidence drops below 10%, Scout will say "I saw your keys on the kitchen counter yesterday, but I'm not very confident they're still there."

## What's Next

[Phase 5: Scout Knows Us](phase-5-faces.md) - add face recognition so Scout greets family members by name.

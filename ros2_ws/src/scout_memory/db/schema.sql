-- Home Scout object memory schema
-- SQLite with FTS5 for full-text search

CREATE TABLE IF NOT EXISTS object_sightings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    object_name TEXT NOT NULL,
    room TEXT NOT NULL DEFAULT 'unknown',
    zone TEXT,
    x REAL,
    y REAL,
    z REAL,
    confidence REAL NOT NULL DEFAULT 1.0,
    source TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sightings_object ON object_sightings(object_name);
CREATE INDEX IF NOT EXISTS idx_sightings_room ON object_sightings(room);
CREATE INDEX IF NOT EXISTS idx_sightings_created ON object_sightings(created_at DESC);

-- FTS5 virtual table for full-text search over sightings
CREATE VIRTUAL TABLE IF NOT EXISTS object_sightings_fts USING fts5(
    object_name,
    room,
    zone,
    source,
    content='object_sightings',
    content_rowid='id'
);

-- Triggers to keep FTS5 index in sync
CREATE TRIGGER IF NOT EXISTS sightings_ai AFTER INSERT ON object_sightings BEGIN
    INSERT INTO object_sightings_fts(rowid, object_name, room, zone, source)
    VALUES (new.id, new.object_name, new.room, new.zone, new.source);
END;

CREATE TRIGGER IF NOT EXISTS sightings_ad AFTER DELETE ON object_sightings BEGIN
    INSERT INTO object_sightings_fts(object_sightings_fts, rowid, object_name, room, zone, source)
    VALUES ('delete', old.id, old.object_name, old.room, old.zone, old.source);
END;

CREATE TRIGGER IF NOT EXISTS sightings_au AFTER UPDATE ON object_sightings BEGIN
    INSERT INTO object_sightings_fts(object_sightings_fts, rowid, object_name, room, zone, source)
    VALUES ('delete', old.id, old.object_name, old.room, old.zone, old.source);
    INSERT INTO object_sightings_fts(rowid, object_name, room, zone, source)
    VALUES (new.id, new.object_name, new.room, new.zone, new.source);
END;

-- Aliases map common names to canonical object names
CREATE TABLE IF NOT EXISTS object_aliases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alias TEXT NOT NULL UNIQUE,
    canonical_name TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_aliases_alias ON object_aliases(alias);

-- Pre-populate common aliases
INSERT OR IGNORE INTO object_aliases (alias, canonical_name) VALUES
    ('phone', 'phone'),
    ('my phone', 'phone'),
    ('mobile', 'phone'),
    ('cell phone', 'phone'),
    ('keys', 'keys'),
    ('my keys', 'keys'),
    ('car keys', 'keys'),
    ('house keys', 'keys'),
    ('wallet', 'wallet'),
    ('my wallet', 'wallet'),
    ('purse', 'wallet'),
    ('remote', 'remote_control'),
    ('tv remote', 'remote_control'),
    ('remote control', 'remote_control'),
    ('glasses', 'glasses'),
    ('my glasses', 'glasses'),
    ('spectacles', 'glasses'),
    ('sunglasses', 'sunglasses');

-- Room polygons (vertices as JSON arrays of [x, y] pairs)
CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    polygon_json TEXT NOT NULL
);

-- Zone polygons (sub-areas within rooms)
CREATE TABLE IF NOT EXISTS zones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER NOT NULL REFERENCES rooms(id),
    name TEXT NOT NULL,
    polygon_json TEXT NOT NULL,
    UNIQUE(room_id, name)
);

CREATE INDEX IF NOT EXISTS idx_zones_room ON zones(room_id);

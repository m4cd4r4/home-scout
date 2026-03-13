"""Shared pytest fixtures for Home Scout tests.

Provides in-memory SQLite databases, sample data, and room polygon
definitions used across unit and integration tests.
"""

import json
import sqlite3

import pytest


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    polygon_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS zones (
    id INTEGER PRIMARY KEY,
    room_id INTEGER NOT NULL REFERENCES rooms(id),
    name TEXT NOT NULL,
    polygon_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS object_sightings (
    id INTEGER PRIMARY KEY,
    object_name TEXT NOT NULL,
    confidence REAL NOT NULL,
    x REAL NOT NULL,
    y REAL NOT NULL,
    room TEXT,
    zone TEXT,
    description TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE VIRTUAL TABLE IF NOT EXISTS object_sightings_fts USING fts5(
    object_name,
    room,
    zone,
    description,
    content='object_sightings',
    content_rowid='id'
);

CREATE TABLE IF NOT EXISTS object_aliases (
    id INTEGER PRIMARY KEY,
    alias TEXT NOT NULL UNIQUE,
    canonical_name TEXT NOT NULL
);
"""

SAMPLE_ROOMS = [
    {
        "name": "kitchen",
        "polygon": [[0.0, 0.0], [4.0, 0.0], [4.0, 3.0], [0.0, 3.0]],
    },
    {
        "name": "living_room",
        "polygon": [[4.0, 0.0], [8.0, 0.0], [8.0, 5.0], [4.0, 5.0]],
    },
    {
        "name": "bedroom",
        "polygon": [[0.0, 3.0], [4.0, 3.0], [4.0, 6.0], [0.0, 6.0]],
    },
]

SAMPLE_ZONES = [
    {
        "room": "kitchen",
        "name": "countertop",
        "polygon": [[0.0, 0.0], [2.0, 0.0], [2.0, 1.0], [0.0, 1.0]],
    },
    {
        "room": "living_room",
        "name": "coffee_table",
        "polygon": [[5.0, 1.0], [7.0, 1.0], [7.0, 3.0], [5.0, 3.0]],
    },
]


@pytest.fixture()
def tmp_db():
    """In-memory SQLite database with schema and sample room/zone data."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_SQL)

    for room in SAMPLE_ROOMS:
        conn.execute(
            "INSERT INTO rooms (name, polygon_json) VALUES (?, ?)",
            (room["name"], json.dumps(room["polygon"])),
        )

    for zone in SAMPLE_ZONES:
        room_id = conn.execute(
            "SELECT id FROM rooms WHERE name = ?", (zone["room"],)
        ).fetchone()["id"]
        conn.execute(
            "INSERT INTO zones (room_id, name, polygon_json) VALUES (?, ?, ?)",
            (room_id, zone["name"], json.dumps(zone["polygon"])),
        )

    # Seed a few aliases
    aliases = [
        ("my phone", "phone"),
        ("tv remote", "remote_control"),
        ("telly remote", "remote_control"),
        ("sunnies", "glasses"),
    ]
    conn.executemany(
        "INSERT INTO object_aliases (alias, canonical_name) VALUES (?, ?)",
        aliases,
    )

    conn.commit()
    yield conn
    conn.close()


@pytest.fixture()
def sample_sighting():
    """A representative ObjectSighting-like dict."""
    return {
        "object_name": "keys",
        "confidence": 0.92,
        "x": 1.0,
        "y": 0.5,
        "room": "kitchen",
        "zone": "countertop",
        "description": "Silver keyring with 3 keys",
        "created_at": "2026-03-13T10:30:00",
    }


@pytest.fixture()
def sample_room_polygons():
    """Room polygon definitions as (name, vertices) tuples.

    Matches the data inserted by the tmp_db fixture so spatial index
    tests can set up their own SpatialIndex without hitting the DB.
    """
    rooms = [
        (r["name"], [tuple(p) for p in r["polygon"]]) for r in SAMPLE_ROOMS
    ]
    zones = [
        (z["name"], z["room"], [tuple(p) for p in z["polygon"]])
        for z in SAMPLE_ZONES
    ]
    return {"rooms": rooms, "zones": zones}

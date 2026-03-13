"""Unit tests for scout_memory.spatial_index module.

Tests point-in-polygon room assignment, zone matching, and edge cases.
"""

import json
import sqlite3

import pytest

from scout_memory.spatial_index import RoomMatch, SpatialIndex


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_spatial_index(tmp_db: sqlite3.Connection) -> SpatialIndex:
    """Build a SpatialIndex with polygon data loaded from the test DB."""
    idx = SpatialIndex.__new__(SpatialIndex)
    idx._conn = tmp_db
    idx._rooms = []
    idx._zones = []

    # Load rooms
    rows = tmp_db.execute("SELECT name, polygon_json FROM rooms").fetchall()
    for row in rows:
        verts = [tuple(p) for p in json.loads(row["polygon_json"])]
        idx._rooms.append((row["name"], verts))

    # Load zones
    rows = tmp_db.execute(
        "SELECT z.name, r.name AS room_name, z.polygon_json "
        "FROM zones z JOIN rooms r ON z.room_id = r.id"
    ).fetchall()
    for row in rows:
        verts = [tuple(p) for p in json.loads(row["polygon_json"])]
        idx._zones.append((row["name"], row["room_name"], verts))

    return idx


# ---------------------------------------------------------------------------
# Point-in-polygon static method
# ---------------------------------------------------------------------------

class TestPointInPolygon:
    """Tests for SpatialIndex._point_in_polygon (ray-casting algorithm)."""

    SQUARE = [(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)]

    def test_point_inside_square(self):
        assert SpatialIndex._point_in_polygon(2.0, 2.0, self.SQUARE) is True

    def test_point_outside_square(self):
        assert SpatialIndex._point_in_polygon(5.0, 5.0, self.SQUARE) is False

    def test_point_far_outside(self):
        assert SpatialIndex._point_in_polygon(-10.0, -10.0, self.SQUARE) is False

    def test_point_near_edge(self):
        """A point very close to (but inside) an edge should be inside."""
        assert SpatialIndex._point_in_polygon(0.01, 2.0, self.SQUARE) is True

    def test_point_just_outside_edge(self):
        """A point just beyond the boundary should be outside."""
        assert SpatialIndex._point_in_polygon(-0.01, 2.0, self.SQUARE) is False

    def test_triangle_inside(self):
        triangle = [(0.0, 0.0), (6.0, 0.0), (3.0, 5.0)]
        assert SpatialIndex._point_in_polygon(3.0, 2.0, triangle) is True

    def test_triangle_outside(self):
        triangle = [(0.0, 0.0), (6.0, 0.0), (3.0, 5.0)]
        assert SpatialIndex._point_in_polygon(0.0, 5.0, triangle) is False

    def test_empty_polygon(self):
        """An empty polygon should always return False."""
        assert SpatialIndex._point_in_polygon(0.0, 0.0, []) is False

    def test_degenerate_line(self):
        """A polygon with only 2 points (a line) should return False."""
        line = [(0.0, 0.0), (5.0, 5.0)]
        assert SpatialIndex._point_in_polygon(2.5, 2.5, line) is False

    def test_l_shaped_polygon(self):
        """L-shaped (concave) polygon."""
        l_shape = [
            (0.0, 0.0), (4.0, 0.0), (4.0, 2.0),
            (2.0, 2.0), (2.0, 4.0), (0.0, 4.0),
        ]
        # Inside the bottom portion
        assert SpatialIndex._point_in_polygon(3.0, 1.0, l_shape) is True
        # Inside the left arm
        assert SpatialIndex._point_in_polygon(1.0, 3.0, l_shape) is True
        # In the "notch" - outside
        assert SpatialIndex._point_in_polygon(3.0, 3.0, l_shape) is False


# ---------------------------------------------------------------------------
# Room assignment via assign()
# ---------------------------------------------------------------------------

class TestAssign:
    """Tests for SpatialIndex.assign() using rooms from conftest."""

    def test_point_in_kitchen(self, tmp_db):
        idx = _make_spatial_index(tmp_db)
        result = idx.assign(2.0, 1.5)
        assert result.room_name == "kitchen"

    def test_point_in_living_room(self, tmp_db):
        idx = _make_spatial_index(tmp_db)
        result = idx.assign(6.0, 2.5)
        assert result.room_name == "living_room"

    def test_point_in_bedroom(self, tmp_db):
        idx = _make_spatial_index(tmp_db)
        result = idx.assign(2.0, 4.5)
        assert result.room_name == "bedroom"

    def test_point_outside_all_rooms(self, tmp_db):
        idx = _make_spatial_index(tmp_db)
        result = idx.assign(20.0, 20.0)
        assert result.room_name == "unknown"
        assert result.zone_name is None

    def test_negative_coordinates(self, tmp_db):
        idx = _make_spatial_index(tmp_db)
        result = idx.assign(-5.0, -5.0)
        assert result.room_name == "unknown"


# ---------------------------------------------------------------------------
# Zone assignment
# ---------------------------------------------------------------------------

class TestZoneAssignment:
    """Tests that zones take precedence over rooms."""

    def test_point_in_countertop_zone(self, tmp_db):
        idx = _make_spatial_index(tmp_db)
        result = idx.assign(1.0, 0.5)
        assert result.room_name == "kitchen"
        assert result.zone_name == "countertop"

    def test_point_in_coffee_table_zone(self, tmp_db):
        idx = _make_spatial_index(tmp_db)
        result = idx.assign(6.0, 2.0)
        assert result.room_name == "living_room"
        assert result.zone_name == "coffee_table"

    def test_point_in_room_but_not_zone(self, tmp_db):
        """Point inside the kitchen but outside the countertop zone."""
        idx = _make_spatial_index(tmp_db)
        result = idx.assign(3.0, 2.0)
        assert result.room_name == "kitchen"
        assert result.zone_name is None


# ---------------------------------------------------------------------------
# RoomMatch dataclass
# ---------------------------------------------------------------------------

class TestRoomMatch:
    def test_room_match_fields(self):
        m = RoomMatch(room_name="kitchen", zone_name="countertop")
        assert m.room_name == "kitchen"
        assert m.zone_name == "countertop"

    def test_room_match_no_zone(self):
        m = RoomMatch(room_name="bedroom", zone_name=None)
        assert m.zone_name is None

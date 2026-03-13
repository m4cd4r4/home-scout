"""Spatial index for room and zone assignment.

Uses point-in-polygon tests to assign (x, y) coordinates from object
sightings to named rooms and zones. Polygons are stored in the rooms
and zones SQLite tables as JSON arrays of [x, y] vertices.
This is a library module, not a ROS node.
"""

import json
import sqlite3
from dataclasses import dataclass


@dataclass
class RoomMatch:
    """Result of a spatial lookup."""

    room_name: str
    zone_name: str | None


class SpatialIndex:
    """Point-in-polygon room/zone assignment."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn
        self._rooms: list[tuple[str, list[tuple[float, float]]]] = []
        self._zones: list[tuple[str, str, list[tuple[float, float]]]] = []
        self._load_polygons()

    def _load_polygons(self) -> None:
        """Load room and zone polygons from the database."""
        # TODO: SELECT id, name, polygon_json FROM rooms
        # TODO: Parse polygon_json into list of (x, y) tuples
        # TODO: SELECT z.id, z.name, z.polygon_json, r.name as room_name
        #       FROM zones z JOIN rooms r ON z.room_id = r.id
        pass

    def assign(self, x: float, y: float) -> RoomMatch:
        """Assign a point to a room and optional zone.

        Args:
            x: X coordinate in map frame.
            y: Y coordinate in map frame.

        Returns:
            RoomMatch with room and zone names. Falls back to "unknown"
            if the point is outside all defined polygons.
        """
        # Check zones first (more specific)
        for zone_name, room_name, polygon in self._zones:
            if self._point_in_polygon(x, y, polygon):
                return RoomMatch(room_name=room_name, zone_name=zone_name)

        # Fall back to room-level
        for room_name, polygon in self._rooms:
            if self._point_in_polygon(x, y, polygon):
                return RoomMatch(room_name=room_name, zone_name=None)

        return RoomMatch(room_name="unknown", zone_name=None)

    @staticmethod
    def _point_in_polygon(
        x: float, y: float, polygon: list[tuple[float, float]]
    ) -> bool:
        """Ray-casting algorithm for point-in-polygon test.

        Args:
            x: Test point X.
            y: Test point Y.
            polygon: List of (x, y) vertices defining the polygon.

        Returns:
            True if the point is inside the polygon.
        """
        n = len(polygon)
        inside = False
        j = n - 1
        for i in range(n):
            xi, yi = polygon[i]
            xj, yj = polygon[j]
            if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
                inside = not inside
            j = i
        return inside

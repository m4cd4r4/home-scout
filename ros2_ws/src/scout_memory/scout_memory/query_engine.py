"""Query engine for object memory.

Translates natural language queries into SQLite queries using FTS5
full-text search. Handles alias resolution and fuzzy matching.
This is a library module, not a ROS node.
"""

import sqlite3
from dataclasses import dataclass


@dataclass
class QueryResult:
    """A single query result from the object memory."""

    object_name: str
    room: str
    zone: str
    confidence: float
    last_seen: str
    description: str


class QueryEngine:
    """Translates natural language to SQLite FTS5 queries."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def find_object(self, query: str) -> QueryResult | None:
        """Find the most recent sighting of an object.

        Args:
            query: Natural language query like "my keys" or "the remote".

        Returns:
            Most recent sighting with confidence decay applied, or None.
        """
        canonical = self._resolve_alias(query)
        # TODO: Query object_sightings FTS5 table for canonical name
        # TODO: Order by created_at DESC, LIMIT 1
        # TODO: Apply confidence decay based on age
        # TODO: Return QueryResult or None
        return None

    def search(self, query: str, limit: int = 10) -> list[QueryResult]:
        """Full-text search across all sightings.

        Args:
            query: Search terms.
            limit: Max results to return.

        Returns:
            List of matching sightings ranked by relevance.
        """
        # TODO: Run FTS5 MATCH query against object_sightings_fts
        # TODO: Join with main table for full row data
        # TODO: Apply confidence decay
        return []

    def _resolve_alias(self, name: str) -> str:
        """Resolve an alias to its canonical object name.

        E.g., "my phone" -> "phone", "TV remote" -> "remote_control"
        """
        cleaned = name.lower().strip()
        # Strip common prefixes
        for prefix in ("my ", "the ", "our ", "a "):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):]

        # TODO: Look up in object_aliases table
        # SELECT canonical_name FROM object_aliases WHERE alias = ?
        return cleaned

    def _build_description(self, result: QueryResult) -> str:
        """Build a human-readable description of a sighting."""
        if result.zone:
            return (
                f"I last saw your {result.object_name} on the "
                f"{result.zone} in the {result.room}."
            )
        return (
            f"I last saw your {result.object_name} in the {result.room}."
        )

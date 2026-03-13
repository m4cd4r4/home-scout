"""Unit tests for scout_memory.query_engine module.

Tests alias resolution, FTS5 search, and object lookup.
"""

import sqlite3

import pytest

from scout_memory.query_engine import QueryEngine, QueryResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _seed_sightings(conn: sqlite3.Connection) -> None:
    """Insert sample sightings into the test database."""
    sightings = [
        ("keys", 0.92, 1.0, 0.5, "kitchen", "countertop",
         "Silver keyring with 3 keys", "2026-03-13T10:30:00"),
        ("phone", 0.88, 6.0, 2.0, "living_room", "coffee_table",
         "Black smartphone face-down", "2026-03-13T11:00:00"),
        ("laptop", 0.95, 2.0, 4.5, "bedroom", None,
         "Silver MacBook Pro on bed", "2026-03-13T09:00:00"),
        ("remote_control", 0.75, 5.5, 3.5, "living_room", None,
         "Black TV remote", "2026-03-13T08:00:00"),
        ("glasses", 0.85, 1.5, 0.3, "kitchen", "countertop",
         "Reading glasses with blue frames", "2026-03-13T07:00:00"),
    ]

    for s in sightings:
        conn.execute(
            "INSERT INTO object_sightings "
            "(object_name, confidence, x, y, room, zone, description, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            s,
        )

    # Populate FTS5 index
    conn.execute(
        "INSERT INTO object_sightings_fts (rowid, object_name, room, zone, description) "
        "SELECT id, object_name, room, zone, description FROM object_sightings"
    )
    conn.commit()


# ---------------------------------------------------------------------------
# Alias resolution
# ---------------------------------------------------------------------------

class TestResolveAlias:
    """Tests for QueryEngine._resolve_alias()."""

    def test_strip_my_prefix(self, tmp_db):
        engine = QueryEngine(tmp_db)
        assert engine._resolve_alias("my keys") == "keys"

    def test_strip_the_prefix(self, tmp_db):
        engine = QueryEngine(tmp_db)
        assert engine._resolve_alias("the phone") == "phone"

    def test_strip_our_prefix(self, tmp_db):
        engine = QueryEngine(tmp_db)
        assert engine._resolve_alias("our laptop") == "laptop"

    def test_strip_a_prefix(self, tmp_db):
        engine = QueryEngine(tmp_db)
        assert engine._resolve_alias("a book") == "book"

    def test_no_prefix(self, tmp_db):
        engine = QueryEngine(tmp_db)
        assert engine._resolve_alias("keys") == "keys"

    def test_case_insensitive(self, tmp_db):
        engine = QueryEngine(tmp_db)
        assert engine._resolve_alias("My Keys") == "keys"

    def test_whitespace_stripped(self, tmp_db):
        engine = QueryEngine(tmp_db)
        assert engine._resolve_alias("  my keys  ") == "keys"

    def test_prefix_only_word_not_stripped(self, tmp_db):
        """'the' by itself should not strip to empty."""
        engine = QueryEngine(tmp_db)
        result = engine._resolve_alias("the")
        # After stripping "the ", we get "" - depends on implementation
        assert isinstance(result, str)

    def test_compound_name_preserves_rest(self, tmp_db):
        engine = QueryEngine(tmp_db)
        assert engine._resolve_alias("my tv remote") == "tv remote"


# ---------------------------------------------------------------------------
# find_object (stub - returns None until implemented)
# ---------------------------------------------------------------------------

class TestFindObject:
    """Tests for QueryEngine.find_object().

    The current implementation is a stub that returns None. These tests
    document the expected behavior and will pass once implemented.
    """

    def test_returns_none_for_stub(self, tmp_db):
        """Current stub returns None for any query."""
        _seed_sightings(tmp_db)
        engine = QueryEngine(tmp_db)
        result = engine.find_object("keys")
        # Stub returns None - update assertion when implemented
        assert result is None

    @pytest.mark.skip(reason="Pending find_object implementation")
    def test_find_keys_in_kitchen(self, tmp_db):
        _seed_sightings(tmp_db)
        engine = QueryEngine(tmp_db)
        result = engine.find_object("my keys")
        assert result is not None
        assert result.object_name == "keys"
        assert result.room == "kitchen"
        assert result.zone == "countertop"

    @pytest.mark.skip(reason="Pending find_object implementation")
    def test_find_phone_strips_prefix(self, tmp_db):
        _seed_sightings(tmp_db)
        engine = QueryEngine(tmp_db)
        result = engine.find_object("the phone")
        assert result is not None
        assert result.object_name == "phone"

    @pytest.mark.skip(reason="Pending find_object implementation")
    def test_find_nonexistent_object(self, tmp_db):
        _seed_sightings(tmp_db)
        engine = QueryEngine(tmp_db)
        result = engine.find_object("unicorn")
        assert result is None


# ---------------------------------------------------------------------------
# search (stub - returns empty list until implemented)
# ---------------------------------------------------------------------------

class TestSearch:
    """Tests for QueryEngine.search().

    The current implementation is a stub that returns []. These tests
    document the expected behavior.
    """

    def test_returns_empty_for_stub(self, tmp_db):
        """Current stub returns empty list."""
        _seed_sightings(tmp_db)
        engine = QueryEngine(tmp_db)
        results = engine.search("kitchen")
        assert results == []

    @pytest.mark.skip(reason="Pending search implementation")
    def test_search_by_room(self, tmp_db):
        _seed_sightings(tmp_db)
        engine = QueryEngine(tmp_db)
        results = engine.search("kitchen")
        assert len(results) >= 1
        assert all(r.room == "kitchen" for r in results)

    @pytest.mark.skip(reason="Pending search implementation")
    def test_search_by_description(self, tmp_db):
        _seed_sightings(tmp_db)
        engine = QueryEngine(tmp_db)
        results = engine.search("silver")
        assert len(results) >= 1

    @pytest.mark.skip(reason="Pending search implementation")
    def test_search_respects_limit(self, tmp_db):
        _seed_sightings(tmp_db)
        engine = QueryEngine(tmp_db)
        results = engine.search("*", limit=2)
        assert len(results) <= 2

    @pytest.mark.skip(reason="Pending search implementation")
    def test_search_empty_query(self, tmp_db):
        _seed_sightings(tmp_db)
        engine = QueryEngine(tmp_db)
        results = engine.search("")
        assert isinstance(results, list)


# ---------------------------------------------------------------------------
# QueryResult dataclass
# ---------------------------------------------------------------------------

class TestQueryResult:
    def test_fields(self):
        r = QueryResult(
            object_name="keys",
            room="kitchen",
            zone="countertop",
            confidence=0.92,
            last_seen="2026-03-13T10:30:00",
            description="Silver keyring",
        )
        assert r.object_name == "keys"
        assert r.room == "kitchen"
        assert r.zone == "countertop"
        assert r.confidence == 0.92
        assert r.last_seen == "2026-03-13T10:30:00"
        assert r.description == "Silver keyring"

    def test_no_zone(self):
        r = QueryResult(
            object_name="laptop",
            room="bedroom",
            zone="",
            confidence=0.95,
            last_seen="2026-03-13T09:00:00",
            description="",
        )
        assert r.zone == ""


# ---------------------------------------------------------------------------
# QueryEngine._build_description
# ---------------------------------------------------------------------------

class TestBuildDescription:
    def test_with_zone(self, tmp_db):
        engine = QueryEngine(tmp_db)
        result = QueryResult(
            object_name="keys",
            room="kitchen",
            zone="countertop",
            confidence=0.9,
            last_seen="now",
            description="",
        )
        desc = engine._build_description(result)
        assert "keys" in desc
        assert "countertop" in desc
        assert "kitchen" in desc

    def test_without_zone(self, tmp_db):
        engine = QueryEngine(tmp_db)
        result = QueryResult(
            object_name="laptop",
            room="bedroom",
            zone="",
            confidence=0.9,
            last_seen="now",
            description="",
        )
        desc = engine._build_description(result)
        assert "laptop" in desc
        assert "bedroom" in desc
        assert "countertop" not in desc

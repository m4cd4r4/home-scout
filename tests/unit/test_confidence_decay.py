"""Unit tests for scout_memory.confidence_decay module.

Tests exponential decay calculation, category mapping, and half-life lookups.
"""

import math

import pytest

from scout_memory.confidence_decay import (
    CATEGORY_MAP,
    DEFAULT_DECAY_CONFIGS,
    DecayConfig,
    compute_decayed_confidence,
    get_half_life,
)


# ---------------------------------------------------------------------------
# compute_decayed_confidence
# ---------------------------------------------------------------------------

class TestComputeDecayedConfidence:
    """Tests for the exponential decay formula."""

    def test_no_time_elapsed(self):
        """Confidence unchanged when age is zero."""
        result = compute_decayed_confidence(0.9, age_hours=0.0, half_life_hours=4.0)
        assert result == pytest.approx(0.9)

    def test_one_half_life(self):
        """After one half-life, confidence should be halved."""
        result = compute_decayed_confidence(1.0, age_hours=4.0, half_life_hours=4.0)
        assert result == pytest.approx(0.5)

    def test_two_half_lives(self):
        """After two half-lives, confidence should be quartered."""
        result = compute_decayed_confidence(1.0, age_hours=8.0, half_life_hours=4.0)
        assert result == pytest.approx(0.25)

    def test_fractional_half_life(self):
        """Half a half-life should decay by sqrt(0.5)."""
        result = compute_decayed_confidence(1.0, age_hours=2.0, half_life_hours=4.0)
        expected = math.pow(0.5, 0.5)  # ~0.7071
        assert result == pytest.approx(expected)

    def test_negative_age_returns_original(self):
        """Negative age is a no-op (future sighting)."""
        result = compute_decayed_confidence(0.8, age_hours=-1.0, half_life_hours=4.0)
        assert result == pytest.approx(0.8)

    def test_zero_half_life_returns_original(self):
        """Zero half-life is a degenerate case - return original."""
        result = compute_decayed_confidence(0.8, age_hours=5.0, half_life_hours=0.0)
        assert result == pytest.approx(0.8)

    def test_negative_half_life_returns_original(self):
        result = compute_decayed_confidence(0.8, age_hours=5.0, half_life_hours=-1.0)
        assert result == pytest.approx(0.8)

    def test_result_clamped_to_zero(self):
        """After many half-lives the value should approach zero but not go negative."""
        result = compute_decayed_confidence(1.0, age_hours=10000.0, half_life_hours=1.0)
        assert result >= 0.0

    def test_result_clamped_to_one(self):
        """Confidence should never exceed 1.0 even with unusual inputs."""
        result = compute_decayed_confidence(1.0, age_hours=0.0, half_life_hours=100.0)
        assert result <= 1.0

    def test_low_initial_confidence(self):
        """Low starting confidence decays proportionally."""
        result = compute_decayed_confidence(0.1, age_hours=4.0, half_life_hours=4.0)
        assert result == pytest.approx(0.05)

    def test_very_long_half_life(self):
        """Fixed furniture barely decays over a day."""
        result = compute_decayed_confidence(0.95, age_hours=24.0, half_life_hours=168.0)
        expected = 0.95 * math.pow(0.5, 24.0 / 168.0)
        assert result == pytest.approx(expected)


# ---------------------------------------------------------------------------
# CATEGORY_MAP
# ---------------------------------------------------------------------------

class TestCategoryMap:
    """Tests for object-to-category mapping."""

    @pytest.mark.parametrize(
        "object_name, expected_category",
        [
            ("keys", "portable"),
            ("phone", "portable"),
            ("wallet", "portable"),
            ("glasses", "portable"),
            ("remote", "portable"),
            ("bag", "portable"),
            ("shoes", "semi_fixed"),
            ("jacket", "semi_fixed"),
            ("laptop", "semi_fixed"),
            ("tablet", "semi_fixed"),
            ("book", "semi_fixed"),
            ("couch", "fixed"),
            ("table", "fixed"),
            ("chair", "fixed"),
            ("tv", "fixed"),
        ],
    )
    def test_known_objects(self, object_name, expected_category):
        assert CATEGORY_MAP[object_name] == expected_category

    def test_all_categories_present(self):
        categories = set(CATEGORY_MAP.values())
        assert categories == {"portable", "semi_fixed", "fixed"}


# ---------------------------------------------------------------------------
# get_half_life
# ---------------------------------------------------------------------------

class TestGetHalfLife:
    """Tests for half-life lookup by object name."""

    def test_portable_object(self):
        assert get_half_life("keys") == 4.0

    def test_semi_fixed_object(self):
        assert get_half_life("laptop") == 24.0

    def test_fixed_object(self):
        assert get_half_life("couch") == 168.0

    def test_unknown_object_defaults_to_portable(self):
        """Unknown objects default to the portable half-life."""
        assert get_half_life("mystery_widget") == 4.0

    def test_case_insensitive(self):
        """Lookup should handle mixed case."""
        assert get_half_life("Keys") == 4.0
        assert get_half_life("PHONE") == 4.0
        assert get_half_life("Laptop") == 24.0


# ---------------------------------------------------------------------------
# DEFAULT_DECAY_CONFIGS
# ---------------------------------------------------------------------------

class TestDecayConfigs:
    def test_three_configs_exist(self):
        assert len(DEFAULT_DECAY_CONFIGS) == 3

    def test_config_categories(self):
        categories = {c.category for c in DEFAULT_DECAY_CONFIGS}
        assert categories == {"portable", "semi_fixed", "fixed"}

    def test_portable_half_life(self):
        portable = next(c for c in DEFAULT_DECAY_CONFIGS if c.category == "portable")
        assert portable.half_life_hours == 4.0

    def test_semi_fixed_half_life(self):
        semi = next(c for c in DEFAULT_DECAY_CONFIGS if c.category == "semi_fixed")
        assert semi.half_life_hours == 24.0

    def test_fixed_half_life(self):
        fixed = next(c for c in DEFAULT_DECAY_CONFIGS if c.category == "fixed")
        assert fixed.half_life_hours == 168.0

    def test_decay_config_dataclass(self):
        config = DecayConfig(category="test", half_life_hours=12.0)
        assert config.category == "test"
        assert config.half_life_hours == 12.0

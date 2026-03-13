"""Time-based confidence decay for stale sightings.

Applies exponential decay to sighting confidence scores based on
how long ago the object was last seen. Configurable half-life per
object category (e.g., keys decay faster than furniture).
This is a library module, not a ROS node.
"""

import math
import sqlite3
from dataclasses import dataclass


@dataclass
class DecayConfig:
    """Decay configuration for an object category."""

    category: str
    half_life_hours: float


# Default decay rates by category. Portable objects decay faster.
DEFAULT_DECAY_CONFIGS: list[DecayConfig] = [
    DecayConfig(category="portable", half_life_hours=4.0),
    DecayConfig(category="semi_fixed", half_life_hours=24.0),
    DecayConfig(category="fixed", half_life_hours=168.0),
]

# Object-to-category mapping for common household items
CATEGORY_MAP: dict[str, str] = {
    "keys": "portable",
    "phone": "portable",
    "wallet": "portable",
    "glasses": "portable",
    "remote": "portable",
    "bag": "portable",
    "shoes": "semi_fixed",
    "jacket": "semi_fixed",
    "laptop": "semi_fixed",
    "tablet": "semi_fixed",
    "book": "semi_fixed",
    "couch": "fixed",
    "table": "fixed",
    "chair": "fixed",
    "tv": "fixed",
}


def compute_decayed_confidence(
    original_confidence: float,
    age_hours: float,
    half_life_hours: float,
) -> float:
    """Compute confidence after exponential time decay.

    Args:
        original_confidence: Detection confidence at time of sighting [0, 1].
        age_hours: Hours since the sighting was recorded.
        half_life_hours: Time in hours for confidence to halve.

    Returns:
        Decayed confidence value, clamped to [0, 1].
    """
    if age_hours <= 0 or half_life_hours <= 0:
        return original_confidence

    decay_factor = math.pow(0.5, age_hours / half_life_hours)
    return max(0.0, min(1.0, original_confidence * decay_factor))


def get_half_life(object_name: str) -> float:
    """Look up the decay half-life for an object.

    Args:
        object_name: Canonical object name.

    Returns:
        Half-life in hours. Defaults to portable rate if unknown.
    """
    category = CATEGORY_MAP.get(object_name.lower(), "portable")
    for config in DEFAULT_DECAY_CONFIGS:
        if config.category == category:
            return config.half_life_hours
    return 4.0


def expire_stale_sightings(conn: sqlite3.Connection, min_confidence: float = 0.05) -> int:
    """Delete sightings whose decayed confidence has dropped below threshold.

    Args:
        conn: SQLite database connection.
        min_confidence: Minimum confidence to keep a sighting.

    Returns:
        Number of rows deleted.
    """
    # TODO: SELECT sightings where time-decayed confidence < min_confidence
    # TODO: DELETE those rows
    # TODO: Return count of deleted rows
    return 0

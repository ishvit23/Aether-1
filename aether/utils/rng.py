"""Centralised RNG factory for deterministic simulation runs.

All randomness in Aether-1 must flow through RNG instances created here.
Never call random.random() or random.randint() directly.
"""

from __future__ import annotations

import random


def create_rng(seed: int | None = None) -> random.Random:
    """Create a seeded Random instance for deterministic behaviour.

    Args:
        seed: Integer seed. If None, uses system entropy (non-deterministic).

    Returns:
        A random.Random instance seeded with the given value.
    """
    return random.Random(seed)

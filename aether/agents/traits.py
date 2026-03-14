"""Trait generation and mutation for agents."""

from __future__ import annotations

import random
from typing import Any

from aether.utils.constants import TRAIT_RANGES


def generate_traits(rng: random.Random, config: dict[str, Any] | None = None) -> dict[str, float]:
    """Generate a random set of traits for a new agent.

    Args:
        rng: Seeded random.Random instance.
        config: Optional config with custom trait ranges.

    Returns:
        Dict mapping trait name to a float value within configured bounds.
    """
    ranges = dict(TRAIT_RANGES)
    if config and "trait_ranges" in config:
        for trait, bounds in config["trait_ranges"].items():
            ranges[trait] = (bounds[0], bounds[1])

    return {trait: rng.uniform(low, high) for trait, (low, high) in ranges.items()}


def mutate_traits(
    parent_traits: dict[str, float],
    rng: random.Random,
    mutation_rate: float = 0.05,
    max_delta: float = 0.1,
    config: dict[str, Any] | None = None,
) -> dict[str, float]:
    """Create a child's traits by mutating parent traits.

    Each trait has a probability of mutation_rate of being changed.
    When mutated, a random delta in [-max_delta, +max_delta] is applied,
    then the result is clamped to the trait's valid range.

    Args:
        parent_traits: Parent agent's trait dictionary.
        rng: Seeded random.Random instance.
        mutation_rate: Probability of each trait mutating.
        max_delta: Maximum absolute change per mutation.
        config: Optional config with custom trait ranges.

    Returns:
        New dict of child traits.
    """
    ranges = dict(TRAIT_RANGES)
    if config and "trait_ranges" in config:
        for trait, bounds in config["trait_ranges"].items():
            ranges[trait] = (bounds[0], bounds[1])

    child_traits: dict[str, float] = {}
    for trait, value in parent_traits.items():
        if rng.random() < mutation_rate:
            delta = rng.uniform(-max_delta, max_delta)
            new_value = value + delta
            low, high = ranges.get(trait, (0.0, 1.0))
            child_traits[trait] = max(low, min(high, new_value))
        else:
            child_traits[trait] = value

    return child_traits

"""Default constants for the Aether-1 simulation engine."""

from __future__ import annotations

# World defaults
DEFAULT_WIDTH: int = 50
DEFAULT_HEIGHT: int = 50
DEFAULT_WRAP: bool = True
DEFAULT_SEED: int = 42
DEFAULT_TICKS: int = 1000

# Agent stat defaults
DEFAULT_STATS: dict[str, float] = {
    "energy": 100.0,
    "health": 100.0,
    "hunger": 0.0,
    "age": 0.0,
}

# Agent trait ranges (min, max)
TRAIT_RANGES: dict[str, tuple[float, float]] = {
    "speed": (0.1, 1.0),
    "strength": (0.1, 1.0),
    "intelligence": (0.1, 1.0),
    "aggression": (0.0, 1.0),
    "greed": (0.0, 1.0),
    "cooperation": (0.0, 1.0),
}

# Rule parameter defaults
DEFAULT_RULE_PARAMS: dict[str, dict[str, float]] = {
    "hunger": {"decay_rate": 0.6, "critical_threshold": 15.0},
    "movement": {"max_steps": 1.0, "energy_cost": 0.5, "goal_bias": 0.3},
    "resource_spawn": {"spawn_interval": 1.0, "spawn_prob": 0.12, "amount": 12.0},
    "collect": {"max_per_tick": 10.0, "capacity": 50.0},
    "combat": {"range": 1.0, "damage_multiplier": 5.0, "flee_threshold": 25.0},
    "trade": {"offer_threshold": 5.0, "acceptance_prob_base": 0.5},
    "reproduction": {"energy_threshold": 60.0, "child_cost": 25.0},
    "mutation": {"rate": 0.05, "max_delta": 0.1},
    "death": {"energy_floor": 0.0, "max_age": 500.0},
}

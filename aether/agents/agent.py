"""Agent model for Aether-1 simulation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Agent:
    """A simulation agent with traits, stats, inventory, and decision-making.

    Agents do NOT directly mutate the world. Their decide() method returns
    an Action which the engine validates and executes.

    Attributes:
        id: Unique integer identifier.
        x: Column position on the grid.
        y: Row position on the grid.
        stats: Numeric stats like energy, health, hunger, age.
        traits: Numeric traits like speed, strength, aggression, cooperation.
        inventory: Resource name -> amount currently held.
        state: Current state string (idle, moving, eating, attacking, etc.).
        memory: List for future agent memory (empty in V1).
    """

    id: int
    x: int
    y: int
    stats: dict[str, float] = field(default_factory=dict)
    traits: dict[str, float] = field(default_factory=dict)
    inventory: dict[str, float] = field(default_factory=dict)
    state: str = "idle"
    memory: list[Any] = field(default_factory=list)

    @property
    def energy(self) -> float:
        """Shortcut for stats['energy']."""
        return self.stats.get("energy", 0.0)

    @energy.setter
    def energy(self, value: float) -> None:
        self.stats["energy"] = value

    @property
    def health(self) -> float:
        """Shortcut for stats['health']."""
        return self.stats.get("health", 0.0)

    @health.setter
    def health(self, value: float) -> None:
        self.stats["health"] = value

    @property
    def hunger(self) -> float:
        """Shortcut for stats['hunger']."""
        return self.stats.get("hunger", 0.0)

    @hunger.setter
    def hunger(self, value: float) -> None:
        self.stats["hunger"] = value

    @property
    def age(self) -> float:
        """Shortcut for stats['age']."""
        return self.stats.get("age", 0.0)

    @age.setter
    def age(self, value: float) -> None:
        self.stats["age"] = value

    def is_alive(self) -> bool:
        """Check if the agent is still alive.

        Returns:
            True if energy > 0 and health > 0.
        """
        return self.energy > 0 and self.health > 0

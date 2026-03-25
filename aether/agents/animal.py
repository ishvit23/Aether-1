"""Animal entity for the Aether-1 V4 multi-tier ecology system.

Animals are distinct from Agents: they have no faction, no inventory, no
decision framework. Their behaviour is governed entirely by AnimalRule.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Animal:
    """A non-agent creature in the world.

    Attributes:
        id: Unique integer identifier (shares namespace with agents).
        kind: Species string — "rabbit" (prey) or "wolf" (predator).
        x: Column position on the grid.
        y: Row position on the grid.
        health: Current health points. Animal dies when <= 0.
        energy: Current energy. Affects movement frequency.
    """

    id: int
    kind: str  # "rabbit" | "wolf"
    x: int
    y: int
    health: float = field(default=100.0)
    energy: float = field(default=80.0)

    def is_alive(self) -> bool:
        """Return True if the animal is still alive."""
        return self.health > 0.0

    @property
    def food_yield(self) -> float:
        """Food granted to an agent who successfully hunts this animal."""
        return 30.0 if self.kind == "wolf" else 20.0

    @property
    def is_predator(self) -> bool:
        """True for wolves, who can attack agents."""
        return self.kind == "wolf"

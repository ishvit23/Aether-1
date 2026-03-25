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
        q_table: Dict defining Q-values for State -> Action -> Value.
        epsilon: Exploration rate for epsilon-greedy selection.
        gamma: Discount factor for future rewards.
        alpha: Learning rate.
        state_representation: The most recent discrete state string from observe().
        last_action: The literal discrete action chosen in the last tick.
    """

    id: int
    x: int
    y: int
    stats: dict[str, float] = field(default_factory=dict)
    traits: dict[str, float] = field(default_factory=dict)
    inventory: dict[str, float] = field(default_factory=dict)
    state: str = "idle"
    memory: list[Any] = field(default_factory=list)
    faction_id: str | None = None

    # RL Attributes
    q_table: dict[str, dict[str, float]] | None = None
    epsilon: float = 0.1
    gamma: float = 0.9
    alpha: float = 0.1
    state_representation: str | None = None
    last_action: str | None = None

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

    def add_memory(self, event: dict[str, Any], max_memories: int = 50) -> None:
        """Add an event to the agent's memory, maintaining a bounded capacity.

        Args:
            event: A dictionary containing event details (e.g., tick, type, agent_id).
            max_memories: The maximum number of events to retain in memory.
        """
        self.memory.insert(0, event)
        if len(self.memory) > max_memories:
            self.memory.pop()

"""Hunger rule: decays agent energy and increases hunger each tick."""

from __future__ import annotations

from aether.rules.base_rule import Rule
from aether.world.world import World


class HungerRule(Rule):
    """Applies hunger decay to all agents each tick.

    Config params:
        decay_rate (float): Energy lost per tick. Default 1.0.
        critical_threshold (float): Hunger level considered critical. Default 20.0.
    """

    name = "hunger"

    def apply(self, world: World, tick: int) -> None:
        """Decay agent energy and increase hunger.

        Args:
            world: The simulation world.
            tick: Current tick number.
        """
        decay_rate = self.params.get("decay_rate", 1.0)

        for agent in world.living_agents():
            agent.energy = max(0.0, agent.energy - decay_rate)
            agent.hunger = agent.hunger + decay_rate * 0.5
            agent.age = agent.age + 1.0

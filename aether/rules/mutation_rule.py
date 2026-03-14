"""Mutation rule: applies random trait mutations to the population."""

from __future__ import annotations

from aether.rules.base_rule import Rule
from aether.world.world import World


class MutationRule(Rule):
    """Applies occasional random mutations to agent traits.

    This rule provides ongoing genetic drift beyond just reproduction mutations.

    Config params:
        rate (float): Per-trait mutation probability per tick. Default 0.01 (low).
        max_delta (float): Maximum change per mutation. Default 0.05.
    """

    name = "mutation"

    def apply(self, world: World, tick: int) -> None:
        """Apply random mutations to agent traits.

        Args:
            world: The simulation world.
            tick: Current tick number.
        """
        rate = self.params.get("rate", 0.01)
        max_delta = self.params.get("max_delta", 0.05)

        for agent in world.living_agents():
            for trait_name, value in agent.traits.items():
                if world.rng.random() < rate:
                    delta = world.rng.uniform(-max_delta, max_delta)
                    agent.traits[trait_name] = max(0.0, min(1.0, value + delta))

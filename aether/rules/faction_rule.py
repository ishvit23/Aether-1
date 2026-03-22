"""Faction rule: assigns and manages agent factions."""

from __future__ import annotations

from aether.rules.base_rule import Rule
from aether.world.world import World


class FactionRule(Rule):
    """Assigns factions to agents based on dominant traits if they have none."""

    name = "faction"

    # Composite trait buckets for balanced faction assignment
    FACTION_PROFILES: dict[str, dict[str, float]] = {
        "Warrior": {"strength": 0.4, "aggression": 0.4, "speed": 0.2},
        "Scout": {"speed": 0.5, "intelligence": 0.3, "cooperation": 0.2},
        "Merchant": {"cooperation": 0.4, "greed": 0.3, "intelligence": 0.3},
        "Scholar": {"intelligence": 0.5, "cooperation": 0.3, "speed": 0.2},
        "Raider": {"aggression": 0.5, "greed": 0.3, "strength": 0.2},
        "Builder": {"cooperation": 0.3, "strength": 0.3, "intelligence": 0.4},
    }

    def apply(self, world: World, tick: int) -> None:
        """Assign factions using composite trait scoring for balanced distribution.

        Args:
            world: The simulation world.
            tick: Current tick number.
        """
        for agent in world.agents.values():
            if not agent.is_alive():
                continue

            if agent.faction_id is None:
                if not agent.traits:
                    agent.faction_id = f"Faction_{world.rng.randint(1, 6)}"
                    continue

                best_faction = None
                best_score = -1.0
                for faction_name, weights in self.FACTION_PROFILES.items():
                    score = sum(
                        agent.traits.get(trait, 0.0) * weight for trait, weight in weights.items()
                    )
                    if score > best_score:
                        best_score = score
                        best_faction = faction_name
                agent.faction_id = best_faction

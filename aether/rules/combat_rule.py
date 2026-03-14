"""Combat rule: resolves combat between agents sharing cells or nearby."""

from __future__ import annotations

from aether.rules.base_rule import Rule
from aether.world.world import World


class CombatRule(Rule):
    """Handles automatic combat when aggressive agents share a cell.

    Config params:
        range (float): Combat engagement range. Default 1.0.
        damage_multiplier (float): Damage scaling factor. Default 10.0.
        flee_threshold (float): Health below which agents try to flee. Default 15.0.
    """

    name = "combat"

    def apply(self, world: World, tick: int) -> None:
        """Check for and resolve combat between co-located agents.

        Args:
            world: The simulation world.
            tick: Current tick number.
        """
        damage_mult = self.params.get("damage_multiplier", 10.0)

        # Find cells with multiple agents
        for row in world.grid:
            for cell in row:
                if len(cell.agents) < 2:
                    continue

                agent_ids = list(cell.agents)
                for i, aid_a in enumerate(agent_ids):
                    for aid_b in agent_ids[i + 1 :]:
                        a = world.agents.get(aid_a)
                        b = world.agents.get(aid_b)
                        if a is None or b is None:
                            continue
                        if not a.is_alive() or not b.is_alive():
                            continue

                        # Combat happens if either agent is aggressive
                        aggr_a = a.traits.get("aggression", 0.0)
                        aggr_b = b.traits.get("aggression", 0.0)

                        if world.rng.random() < max(aggr_a, aggr_b) * 0.3:
                            # Resolve combat based on strength
                            str_a = a.traits.get("strength", 0.5)
                            str_b = b.traits.get("strength", 0.5)

                            dmg_to_b = str_a * damage_mult * world.rng.uniform(0.5, 1.5)
                            dmg_to_a = str_b * damage_mult * world.rng.uniform(0.5, 1.5)

                            b.health = max(0.0, b.health - dmg_to_b)
                            a.health = max(0.0, a.health - dmg_to_a)
                            a.energy = max(0.0, a.energy - 3.0)
                            b.energy = max(0.0, b.energy - 3.0)

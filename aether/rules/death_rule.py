"""Death rule: removes agents that have died (energy/health <= 0 or max age)."""

from __future__ import annotations

from aether.rules.base_rule import Rule
from aether.world.world import World


class DeathRule(Rule):
    """Removes dead agents from the simulation.

    An agent dies if:
        - energy <= energy_floor (starvation)
        - health <= 0 (killed in combat)
        - age >= max_age (old age)

    Config params:
        energy_floor (float): Energy at or below which agent dies. Default 0.0.
        max_age (float): Maximum age before death. Default 500.0.
    """

    name = "death"

    def apply(self, world: World, tick: int) -> None:
        """Remove dead agents from the world.

        Args:
            world: The simulation world.
            tick: Current tick number.
        """
        energy_floor = self.params.get("energy_floor", 0.0)
        max_age = self.params.get("max_age", 500.0)

        dead_ids: list[int] = []
        for agent in world.living_agents():
            if agent.energy <= energy_floor or agent.health <= 0 or agent.age >= max_age:
                dead_ids.append(agent.id)

        for aid in dead_ids:
            world.remove_agent(aid)

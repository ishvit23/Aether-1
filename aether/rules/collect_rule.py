"""Collect rule: allows agents to pick up resources from their cell."""

from __future__ import annotations

from aether.agents.inventory import add_resource
from aether.rules.base_rule import Rule
from aether.world.world import World


class CollectRule(Rule):
    """Auto-collects a small amount of resources if the agent is standing on them.

    This supplements the action-based collection. Agents passively pick up
    small amounts of resources each tick.

    Config params:
        max_per_tick (float): Max resource amount to auto-collect. Default 2.0.
        capacity (float): Max total inventory capacity. Default 50.0.
    """

    name = "collect"

    def apply(self, world: World, tick: int) -> None:
        """Auto-collect resources for agents standing on resource cells.

        Args:
            world: The simulation world.
            tick: Current tick number.
        """
        max_per_tick = self.params.get("max_per_tick", 2.0)

        for agent in world.living_agents():
            cell = world.get_cell(agent.x, agent.y)
            if not cell.has_resources():
                continue

            for resource_name in list(cell.resources.keys()):
                collected = cell.remove_resource(resource_name, max_per_tick)
                if collected > 0:
                    add_resource(agent.inventory, resource_name, collected)

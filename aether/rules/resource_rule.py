"""Resource spawn rule: periodically spawns resources on the grid."""

from __future__ import annotations

from aether.rules.base_rule import Rule
from aether.world.world import World


class ResourceSpawnRule(Rule):
    """Spawns resources on grid cells at configurable intervals.

    Config params:
        spawn_interval (float): Spawn every N ticks. Default 1.0.
        spawn_prob (float): Probability per cell per spawn tick. Default 0.02.
        amount (float): Base amount to spawn. Default 5.0.
    """

    name = "resource_spawn"

    def apply(self, world: World, tick: int) -> None:
        """Spawn resources on the grid.

        Args:
            world: The simulation world.
            tick: Current tick number.
        """
        interval = int(self.params.get("spawn_interval", 1))
        if tick % max(interval, 1) != 0:
            return

        spawn_prob = self.params.get("spawn_prob", 0.02)
        amount = self.params.get("amount", 5.0)

        if world.weather_state == "Winter":
            spawn_prob *= 0.1
            amount *= 0.2
        elif world.weather_state == "Summer":
            spawn_prob *= 1.5
            amount *= 1.5
        elif world.weather_state == "Autumn":
            spawn_prob *= 0.8

        for row in world.grid:
            for cell in row:
                if world.rng.random() < spawn_prob:
                    # Randomly choose food or material
                    resource = world.rng.choice(["food", "material"])
                    spawn_amount = world.rng.uniform(1.0, amount)
                    cell.add_resource(resource, spawn_amount)

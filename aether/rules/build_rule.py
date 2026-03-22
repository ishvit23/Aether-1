"""Build rule: handles passive environmental effects of structures."""

from __future__ import annotations

from aether.rules.base_rule import Rule
from aether.world.world import World


class BuildRule(Rule):
    """Applies passive effects for structures.

    Nests apply energy regeneration buff to agents occupying or adjacent to the cell.
    """

    name = "build"

    def apply(self, world: World, tick: int) -> None:
        """Apply structure passive effects.

        Args:
            world: The simulation world.
            tick: Current tick number.
        """
        heal_amount = self.params.get("nest_heal", 2.0)

        for agent in world.living_agents():
            current_cell = world.get_cell(agent.x, agent.y)
            healed = False

            # Check cell directly
            if current_cell.structure == "nest":
                agent.energy = min(100.0, agent.energy + heal_amount)
                healed = True

            # If not healed, check neighbors
            if not healed:
                neighbors = world.get_neighbors(agent.x, agent.y, radius=1)
                for n in neighbors:
                    if n.structure == "nest":
                        agent.energy = min(100.0, agent.energy + heal_amount)
                        break

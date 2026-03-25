"""Decay rule — structures lose health during Winter; destroyed ones are cleared."""

from __future__ import annotations

from aether.rules.base_rule import Rule
from aether.world.world import World


class DecayRule(Rule):
    """Applies structural decay to walls and nests during Winter.

    In non-Winter seasons structures are stable. During Winter:
      - Walls lose ``wall_decay`` HP per tick.
      - Nests lose ``nest_decay`` HP per tick.

    Structures reaching 0 HP are removed from the grid.

    Config params:
        wall_decay (float): HP lost per tick in Winter. Default 2.0.
        nest_decay (float): HP lost per tick in Winter. Default 1.0.
    """

    name = "decay"

    def apply(self, world: World, tick: int) -> None:
        """Apply decay to all structures, removing destroyed ones.

        Args:
            world: The simulation world.
            tick: Current tick number.
        """
        if world.weather_state != "Winter":
            return  # Structures only decay in winter

        wall_decay: float = float(self.params.get("wall_decay", 2.0))
        nest_decay: float = float(self.params.get("nest_decay", 1.0))

        for row in world.grid:
            for cell in row:
                if cell.structure is None:
                    continue
                rate = wall_decay if cell.structure.kind == "wall" else nest_decay
                cell.structure.health -= rate

                if cell.structure.is_destroyed():
                    cell.structure = None

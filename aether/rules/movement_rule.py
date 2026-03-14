"""Movement rule: generates movement decisions for agents."""

from __future__ import annotations

from aether.rules.base_rule import Rule
from aether.world.world import World


class MovementRule(Rule):
    """Applies movement costs and updates agent positions.

    This rule doesn't directly move agents — it adjusts energy costs.
    Actual movement happens through the action system in TickEngine.

    Config params:
        energy_cost (float): Energy cost per movement. Default 0.5.
        max_steps (float): Max cells an agent can move per tick. Default 1.0.
    """

    name = "movement"

    def apply(self, world: World, tick: int) -> None:
        """Apply movement-related state updates.

        Args:
            world: The simulation world.
            tick: Current tick number.
        """
        # Movement is handled by the action system (decide -> move_action).
        # This rule is a placeholder for any pre-movement processing.
        pass

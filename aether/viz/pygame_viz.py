"""Pygame visualization placeholder for Aether-1."""

from __future__ import annotations

from aether.world.world import World


def render_pygame(world: World, tick: int) -> None:
    """Render the world using Pygame (placeholder for V2).

    Args:
        world: The simulation world.
        tick: Current tick number.
    """
    # Pygame renderer will be implemented in Milestone 8 / V2
    raise NotImplementedError("Pygame renderer not yet implemented. Use --viz console instead.")

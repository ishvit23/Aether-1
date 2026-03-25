"""Move action executor."""

from __future__ import annotations

from typing import Any

from aether.world.world import World


def execute_move(actor_id: int, target: tuple[int, int] | None, world: World) -> dict[str, Any]:
    """Execute a move action for an agent.

    Args:
        actor_id: ID of the moving agent.
        target: (x, y) destination coordinates.
        world: The world instance.

    Returns:
        Event payload dict for logging.
    """
    agent = world.agents.get(actor_id)
    if agent is None or target is None:
        return {"success": False, "reason": "invalid_agent_or_target"}

    new_x, new_y = target
    target_cell = world.get_cell(new_x, new_y)
    if target_cell.structure_kind == "wall":
        return {"success": False, "reason": "blocked_by_wall"}

    old_x, old_y = agent.x, agent.y
    world.move_agent(actor_id, new_x, new_y)

    # Deduct movement energy cost
    agent.energy = max(0.0, agent.energy - 0.5)

    return {
        "agent_id": actor_id,
        "from": (old_x, old_y),
        "to": (agent.x, agent.y),
        "success": True,
    }

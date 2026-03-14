"""Collect action executor."""

from __future__ import annotations

from typing import Any

from aether.agents.inventory import add_resource
from aether.world.world import World


def execute_collect(
    actor_id: int, target: tuple[int, int] | None, payload: dict[str, Any], world: World
) -> dict[str, Any]:
    """Execute a collect action: transfer resource from cell to agent inventory.

    Args:
        actor_id: ID of the collecting agent.
        target: (x, y) of the cell to collect from (usually agent's own cell).
        payload: Must contain 'resource' key with the resource name.
        world: The world instance.

    Returns:
        Event payload dict for logging.
    """
    agent = world.agents.get(actor_id)
    if agent is None:
        return {"success": False, "reason": "invalid_agent"}

    resource_name = payload.get("resource", "food")
    cell = world.get_cell(agent.x, agent.y)
    max_collect = 10.0  # max per tick

    collected = cell.remove_resource(resource_name, max_collect)
    if collected > 0:
        add_resource(agent.inventory, resource_name, collected)

    return {
        "agent_id": actor_id,
        "resource": resource_name,
        "amount": collected,
        "success": collected > 0,
    }

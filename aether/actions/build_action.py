"""Build action executor."""

from __future__ import annotations

from typing import Any

from aether.world.world import World


def execute_build(
    actor_id: int, target: tuple[int, int] | None, payload: dict[str, Any], world: World
) -> dict[str, Any]:
    """Execute a build action for an agent.

    Args:
        actor_id: ID of the building agent.
        target: (x, y) target coordinates.
        payload: Dict containing 'structure_type'.
        world: The world instance.

    Returns:
        Event payload dict for logging.
    """
    agent = world.agents.get(actor_id)
    if agent is None or target is None:
        return {"success": False, "reason": "invalid_agent_or_target"}

    structure_type = payload.get("structure_type")

    if structure_type not in ["wall", "nest"]:
        return {"success": False, "reason": "invalid_structure_type"}

    # Costs material
    material_cost = 15.0 if structure_type == "wall" else 20.0
    material_available = agent.inventory.get("material", 0.0)

    if material_available < material_cost:
        return {"success": False, "reason": "insufficient_material"}

    target_cell = world.get_cell(target[0], target[1])
    if target_cell.structure is not None:
        return {"success": False, "reason": "structure_already_exists"}

    # Walls can't be built on agents.
    if structure_type == "wall" and target_cell.agents:
        return {"success": False, "reason": "cell_occupied"}

    agent.inventory["material"] -= material_cost
    if agent.inventory["material"] <= 0.0:
        del agent.inventory["material"]

    target_cell.structure = structure_type

    return {
        "success": True,
        "agent_id": actor_id,
        "structure": structure_type,
        "at": target,
    }

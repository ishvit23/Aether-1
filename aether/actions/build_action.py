"""Build action executor."""

from __future__ import annotations

from typing import Any

from aether.world.cell import StructureData
from aether.world.world import World


def execute_build(
    actor_id: int, target: tuple[int, int] | None, payload: dict[str, Any], world: World
) -> dict[str, Any]:
    """Execute a build action for an agent.

    If the target cell already has a friendly structure, repair it instead of
    building a new one (adds 30 HP). If the structure belongs to a rival
    faction, building is blocked.

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

    material_cost = 15.0 if structure_type == "wall" else 20.0
    material_available = agent.inventory.get("material", 0.0)

    if material_available < material_cost:
        return {"success": False, "reason": "insufficient_material"}

    target_cell = world.get_cell(target[0], target[1])

    # Repair existing friendly structure
    if target_cell.structure is not None:
        existing = target_cell.structure
        if existing.kind != structure_type:
            return {"success": False, "reason": "structure_already_exists"}
        if existing.faction_id == agent.faction_id:
            agent.inventory["material"] = material_available - (material_cost / 2)
            existing.health = min(100.0, existing.health + 30.0)
            return {
                "success": True,
                "action": "repair",
                "agent_id": actor_id,
                "structure": existing.kind,
                "health": existing.health,
                "at": target,
            }
        return {"success": False, "reason": "structure_already_exists"}

    # Walls can't be built on occupied cells
    if structure_type == "wall" and target_cell.agents:
        return {"success": False, "reason": "cell_occupied"}

    agent.inventory["material"] = material_available - material_cost
    if agent.inventory["material"] <= 0.0:
        del agent.inventory["material"]

    target_cell.structure = StructureData(
        kind=structure_type,
        health=100.0,
        faction_id=agent.faction_id,
    )

    return {
        "success": True,
        "action": "build",
        "agent_id": actor_id,
        "structure": structure_type,
        "at": target,
    }

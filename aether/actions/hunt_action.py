"""Hunt action — allows agents to hunt and kill animals for high-yield food."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from aether.world.world import World


def execute_hunt(actor_id: int, target_animal_id: int | None, world: World) -> dict[str, Any]:
    """Execute a hunt action: agent kills a target animal and gains food.

    Args:
        actor_id: ID of the hunting agent.
        target_animal_id: ID of the animal to hunt.
        world: The simulation world.

    Returns:
        Result dict with 'success', 'food_gained', and optionally 'reason'.
    """
    agent = world.agents.get(actor_id)
    if agent is None or not agent.is_alive():
        return {"success": False, "reason": "actor_dead"}

    if target_animal_id is None:
        return {"success": False, "reason": "no_target"}

    animal = world.animals.get(target_animal_id)
    if animal is None or not animal.is_alive():
        return {"success": False, "reason": "target_dead"}

    # Must be adjacent (within distance 1)
    dx = abs(agent.x - animal.x)
    dy = abs(agent.y - animal.y)
    if world.wrap:
        dx = min(dx, world.width - dx)
        dy = min(dy, world.height - dy)
    if dx > 1 or dy > 1:
        return {"success": False, "reason": "out_of_range"}

    # Hunt success roll — wolves fight back
    strength = agent.traits.get("strength", 0.5)
    if animal.is_predator:
        # Wolves retaliate
        wolf_dmg = world.rng.uniform(5.0, 15.0)
        agent.health = max(0.0, agent.health - wolf_dmg)
        # Agent needs enough strength to win
        if world.rng.random() > strength:
            return {"success": False, "reason": "hunt_failed", "damage_taken": wolf_dmg}

    # Kill the animal and reward the hunter
    food_gained = animal.food_yield
    world.remove_animal(target_animal_id)
    from aether.agents.inventory import add_resource

    add_resource(agent.inventory, "food", food_gained)

    return {
        "success": True,
        "agent_id": actor_id,
        "animal_id": target_animal_id,
        "kind": animal.kind,
        "food_gained": food_gained,
    }

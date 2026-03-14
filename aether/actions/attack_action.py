"""Attack action executor."""

from __future__ import annotations

from typing import Any

from aether.world.world import World


def execute_attack(actor_id: int, target_id: int | None, world: World) -> dict[str, Any]:
    """Execute an attack action.

    Damage is based on attacker's strength trait. Defender takes damage
    to health AND energy.

    Args:
        actor_id: ID of the attacking agent.
        target_id: ID of the defending agent.
        world: The world instance.

    Returns:
        Event payload dict for logging.
    """
    attacker = world.agents.get(actor_id)
    if attacker is None or target_id is None:
        return {"success": False, "reason": "invalid_attacker"}

    defender = world.agents.get(target_id)
    if defender is None:
        return {"success": False, "reason": "invalid_target"}

    strength = attacker.traits.get("strength", 0.5)
    damage = strength * 10.0

    defender.health = max(0.0, defender.health - damage)
    defender.energy = max(0.0, defender.energy - damage * 0.5)

    # Attacker also uses energy
    attacker.energy = max(0.0, attacker.energy - 2.0)

    return {
        "attacker_id": actor_id,
        "defender_id": target_id,
        "damage": damage,
        "defender_health": defender.health,
        "success": True,
    }

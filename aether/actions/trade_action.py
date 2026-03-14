"""Trade action executor."""

from __future__ import annotations

from typing import Any

from aether.agents.inventory import add_resource, has_resource, remove_resource
from aether.world.world import World


def execute_trade(
    actor_id: int, target_id: int | None, payload: dict[str, Any], world: World
) -> dict[str, Any]:
    """Execute a trade action: bilateral resource exchange.

    Args:
        actor_id: ID of the initiating agent.
        target_id: ID of the trade partner.
        payload: Must contain 'offer_resource' and 'offer_amount'.
        world: The world instance.

    Returns:
        Event payload dict for logging.
    """
    agent_a = world.agents.get(actor_id)
    if agent_a is None or target_id is None:
        return {"success": False, "reason": "invalid_agent"}

    agent_b = world.agents.get(target_id)
    if agent_b is None:
        return {"success": False, "reason": "invalid_partner"}

    offer_resource = payload.get("offer_resource", "")
    offer_amount = payload.get("offer_amount", 1.0)

    if not has_resource(agent_a.inventory, offer_resource, offer_amount):
        return {"success": False, "reason": "insufficient_resource"}

    # Find something B can offer in return
    want_resource = None
    for res in agent_b.inventory:
        if res != offer_resource and has_resource(agent_b.inventory, res):
            want_resource = res
            break

    if want_resource is None:
        return {"success": False, "reason": "no_reciprocal_resource"}

    # Execute trade: A gives offer, B gives want
    removed_a = remove_resource(agent_a.inventory, offer_resource, offer_amount)
    removed_b = remove_resource(agent_b.inventory, want_resource, offer_amount)
    add_resource(agent_b.inventory, offer_resource, removed_a)
    add_resource(agent_a.inventory, want_resource, removed_b)

    return {
        "a": actor_id,
        "b": target_id,
        "a_gave": offer_resource,
        "a_gave_amount": removed_a,
        "b_gave": want_resource,
        "b_gave_amount": removed_b,
        "success": True,
    }

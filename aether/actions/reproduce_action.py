"""Reproduce action executor."""

from __future__ import annotations

from typing import Any

from aether.agents.agent import Agent
from aether.agents.traits import mutate_traits
from aether.utils.constants import DEFAULT_STATS
from aether.world.world import World


def execute_reproduce(
    actor_id: int,
    world: World,
    child_cost: float = 30.0,
    mutation_rate: float = 0.05,
    max_delta: float = 0.1,
) -> dict[str, Any]:
    """Execute a reproduction action: parent spawns a child agent.

    The parent pays child_cost energy. The child inherits mutated traits.

    Args:
        actor_id: ID of the parent agent.
        world: The world instance.
        child_cost: Energy cost to the parent.
        mutation_rate: Probability of each trait mutating.
        max_delta: Maximum mutation delta.

    Returns:
        Event payload dict for logging.
    """
    parent = world.agents.get(actor_id)
    if parent is None:
        return {"success": False, "reason": "invalid_parent"}

    if parent.energy < child_cost:
        return {"success": False, "reason": "insufficient_energy"}

    # Population cap (matches reproduction rule)
    if world.population_size() >= 80:
        return {"success": False, "reason": "population_cap"}

    # Cooldown check
    last_repro = parent.stats.get("last_repro_tick", -999.0)
    current_tick = world.tick
    if current_tick - last_repro < 30:
        return {"success": False, "reason": "cooldown"}

    # Deduct cost from parent
    parent.energy -= child_cost
    parent.stats["last_repro_tick"] = float(current_tick)

    # Create child
    child_id = world.next_agent_id()
    child_traits = mutate_traits(
        parent.traits,
        world.rng,
        mutation_rate=mutation_rate,
        max_delta=max_delta,
    )
    child_stats = dict(DEFAULT_STATS)
    child_stats["energy"] = child_cost * 0.8  # child starts with portion of cost

    child = Agent(
        id=child_id,
        x=parent.x,
        y=parent.y,
        traits=child_traits,
        stats=child_stats,
    )
    world.add_agent(child)

    return {
        "parent_id": actor_id,
        "child_id": child_id,
        "x": child.x,
        "y": child.y,
        "success": True,
    }

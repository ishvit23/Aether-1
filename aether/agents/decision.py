"""Agent decision-making: observation and action selection."""

from __future__ import annotations

import random
from typing import Any

from aether.actions.action import Action, ActionType
from aether.agents.agent import Agent
from aether.agents.inventory import has_resource
from aether.world.world import World


def observe(agent: Agent, world: World, radius: int = 2) -> dict[str, Any]:
    """Build an observation dict for an agent based on nearby cells.

    Args:
        agent: The observing agent.
        world: The world state.
        radius: Vision radius in cells.

    Returns:
        Dict with keys: self_stats, self_traits, self_inventory, nearby_cells,
        nearby_agents, current_cell.
    """
    current_cell = world.get_cell(agent.x, agent.y)
    neighbors = world.get_neighbors(agent.x, agent.y, radius)

    nearby_agents: list[dict[str, Any]] = []
    for cell in neighbors:
        for aid in cell.agents:
            if aid != agent.id and aid in world.agents:
                other = world.agents[aid]
                nearby_agents.append(
                    {
                        "id": other.id,
                        "x": other.x,
                        "y": other.y,
                        "state": other.state,
                    }
                )

    return {
        "self_stats": dict(agent.stats),
        "self_traits": dict(agent.traits),
        "self_inventory": dict(agent.inventory),
        "current_cell": {
            "x": current_cell.x,
            "y": current_cell.y,
            "resources": dict(current_cell.resources),
            "agent_count": current_cell.agent_count(),
        },
        "nearby_cells": [
            {
                "x": c.x,
                "y": c.y,
                "resources": dict(c.resources),
                "agent_count": c.agent_count(),
            }
            for c in neighbors
        ],
        "nearby_agents": nearby_agents,
    }


def decide(agent: Agent, observation: dict[str, Any], rng: random.Random) -> Action:
    """Decide an action based on agent traits and observations.

    Priority table (spec §9):
        1. eat     — hunger > critical threshold
        2. collect — nearby resource and inventory below capacity
        3. attack  — aggression trait check + target in range
        4. trade   — cooperation trait check + mutually beneficial neighbour
        5. reproduce — energy >= reproduction threshold
        6. move    — goal-directed or random walk
        7. idle    — no condition met

    Args:
        agent: The deciding agent.
        observation: Observation dict from observe().
        rng: Seeded RNG for deterministic decisions.

    Returns:
        An Action TypedDict.
    """
    stats = observation["self_stats"]
    traits = observation["self_traits"]
    current_cell = observation["current_cell"]
    nearby_agents = observation["nearby_agents"]

    # Priority 1: Eat if hungry and has food
    hunger = stats.get("hunger", 0.0)
    if hunger > 20.0 and has_resource(agent.inventory, "food"):
        return Action(
            type=ActionType.EAT,
            actor_id=agent.id,
            target=None,
            payload={"resource": "food"},
        )

    # Priority 2: Collect if resources on current cell
    cell_resources = current_cell.get("resources", {})
    if cell_resources:
        best_resource = max(cell_resources, key=lambda r: cell_resources[r])
        return Action(
            type=ActionType.COLLECT,
            actor_id=agent.id,
            target=(current_cell["x"], current_cell["y"]),
            payload={"resource": best_resource},
        )

    # Priority 3: Attack if aggressive and nearby target
    aggression = traits.get("aggression", 0.0)
    if nearby_agents and rng.random() < aggression:
        target_agent = rng.choice(nearby_agents)
        return Action(
            type=ActionType.ATTACK,
            actor_id=agent.id,
            target=target_agent["id"],
            payload={},
        )

    # Priority 4: Trade if cooperative and has resources
    cooperation = traits.get("cooperation", 0.0)
    if nearby_agents and rng.random() < cooperation and agent.inventory:
        partner = rng.choice(nearby_agents)
        offer_resource = rng.choice(list(agent.inventory.keys()))
        return Action(
            type=ActionType.TRADE,
            actor_id=agent.id,
            target=partner["id"],
            payload={"offer_resource": offer_resource, "offer_amount": 1.0},
        )

    # Priority 5: Reproduce if enough energy
    from aether.utils.constants import DEFAULT_RULE_PARAMS

    repro_threshold = DEFAULT_RULE_PARAMS["reproduction"].get("energy_threshold", 80.0)
    energy = stats.get("energy", 0.0)
    if energy >= repro_threshold:
        return Action(
            type=ActionType.REPRODUCE,
            actor_id=agent.id,
            target=None,
            payload={},
        )

    # Priority 6: Move toward resources (prefer food if hungry)
    nearby = observation.get("nearby_cells", [])
    food_cells = [c for c in nearby if "food" in c.get("resources", {})]
    resource_cells = [c for c in nearby if c.get("resources")]
    
    target_cells = food_cells if food_cells and hunger > 5.0 else resource_cells
    if target_cells:
        target_cell = rng.choice(target_cells)
        return Action(
            type=ActionType.MOVE,
            actor_id=agent.id,
            target=(target_cell["x"], target_cell["y"]),
            payload={},
        )

    # Random walk
    dx = rng.randint(-1, 1)
    dy = rng.randint(-1, 1)
    return Action(
        type=ActionType.MOVE,
        actor_id=agent.id,
        target=(agent.x + dx, agent.y + dy),
        payload={},
    )

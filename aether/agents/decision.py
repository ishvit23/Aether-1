"""Agent decision-making: observation and action selection."""

from __future__ import annotations

import random
import typing
from typing import Any

from aether.actions.action import Action, ActionType
from aether.agents.agent import Agent
from aether.agents.inventory import has_resource
from aether.world.world import World

RL_ACTIONS = [
    "EAT",
    "COLLECT",
    "ATTACK",
    "TRADE",
    "REPRODUCE",
    "BUILD_NEST",
    "BUILD_WALL",
    "HUNT",
    "MOVE_TOWARD_FOOD",
    "MOVE_TOWARD_AGENT",
    "MOVE_TOWARD_PREY",
    "FLEE",
    "EXPLORE",
]


def observe(agent: Agent, world: World, radius: int = 2) -> dict[str, Any]:
    """Build an observation dict for an agent based on nearby cells."""
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
                        "faction_id": other.faction_id,
                    }
                )

    nearby_animals: list[dict[str, Any]] = []
    for animal in world.living_animals():
        if abs(animal.x - agent.x) <= radius and abs(animal.y - agent.y) <= radius:
            nearby_animals.append(
                {
                    "id": animal.id,
                    "x": animal.x,
                    "y": animal.y,
                    "kind": animal.kind,
                }
            )

    return {
        "self_stats": dict(agent.stats),
        "self_traits": dict(agent.traits),
        "self_inventory": dict(agent.inventory),
        "memory": list(agent.memory),
        "weather_state": getattr(world, "weather_state", "Spring"),
        "current_cell": {
            "x": current_cell.x,
            "y": current_cell.y,
            "resources": dict(current_cell.resources),
            "agent_count": current_cell.agent_count(),
            "structure_kind": current_cell.structure_kind,
        },
        "nearby_cells": [
            {
                "x": c.x,
                "y": c.y,
                "resources": dict(c.resources),
                "agent_count": c.agent_count(),
                "structure_kind": c.structure_kind,
            }
            for c in neighbors
        ],
        "nearby_agents": nearby_agents,
        "nearby_animals": nearby_animals,
    }


def _get_discrete_state(agent: Agent, observation: dict[str, Any]) -> str:
    """Convert continuous observation into a discrete state string for Q-Table mapping."""
    stats = observation["self_stats"]
    weather = observation.get("weather_state", "Spring")

    hunger = stats.get("hunger", 0.0)
    health = stats.get("health", 100.0)

    nearby_a = observation.get("nearby_agents", [])
    nearby_an = observation.get("nearby_animals", [])

    is_hungry = "1" if hunger > 50.0 else "0"
    is_hurt = "1" if health < 50.0 else "0"

    has_food = "1" if "food" in agent.inventory and agent.inventory["food"] >= 10.0 else "0"
    can_see_food = (
        "1"
        if any("food" in c.get("resources", {}) for c in observation.get("nearby_cells", []))
        else "0"
    )

    can_see_enemy = "1" if any(a.get("faction_id") != agent.faction_id for a in nearby_a) else "0"
    can_see_wolf = "1" if any(an.get("kind") == "wolf" for an in nearby_an) else "0"
    can_see_rabbit = "1" if any(an.get("kind") == "rabbit" for an in nearby_an) else "0"
    is_winter = "1" if weather == "Winter" else "0"

    return (
        f"{is_hungry}{is_hurt}{has_food}{can_see_food}"
        f"{can_see_enemy}{can_see_wolf}{can_see_rabbit}{is_winter}"
    )


def _map_abstract_action(
    action_str: str, agent: Agent, observation: dict[str, Any], rng: random.Random
) -> Action:
    """Map a discrete RL action string to an executable Action dictionary."""
    nearby_agents = observation.get("nearby_agents", [])
    nearby_animals = observation.get("nearby_animals", [])
    nearby_cells = observation.get("nearby_cells", [])
    current_cell = observation.get("current_cell", {})

    target_tuple = None
    target_id = None
    payload: dict[str, Any] = {}

    if action_str == "EAT":
        action_type = ActionType.EAT
        payload = {"resource": "food"}

    elif action_str == "COLLECT":
        action_type = ActionType.COLLECT
        res = current_cell.get("resources", {})
        if res:
            payload = {"resource": max(res, key=lambda k: res[k])}
        target_tuple = (current_cell.get("x", agent.x), current_cell.get("y", agent.y))

    elif action_str == "ATTACK":
        action_type = ActionType.ATTACK
        enemies = [a for a in nearby_agents if a.get("faction_id") != agent.faction_id]
        if enemies:
            target_id = rng.choice(enemies)["id"]

    elif action_str == "TRADE":
        action_type = ActionType.TRADE
        if nearby_agents and agent.inventory:
            target_id = rng.choice(nearby_agents)["id"]
            payload = {
                "offer_resource": rng.choice(list(agent.inventory.keys())),
                "offer_amount": 1.0,
            }

    elif action_str == "REPRODUCE":
        action_type = ActionType.REPRODUCE

    elif action_str == "BUILD_NEST":
        action_type = ActionType.BUILD
        target_tuple = (current_cell.get("x", agent.x), current_cell.get("y", agent.y))
        payload = {"structure_type": "nest"}

    elif action_str == "BUILD_WALL":
        action_type = ActionType.BUILD
        empty_spots = [
            c
            for c in nearby_cells
            if c.get("structure_kind") is None and c.get("agent_count", 0) == 0
        ]
        if empty_spots:
            c = rng.choice(empty_spots)
            target_tuple = (c["x"], c["y"])
        else:
            target_tuple = (agent.x, agent.y)
        payload = {"structure_type": "wall"}

    elif action_str == "HUNT":
        action_type = ActionType.HUNT
        if nearby_animals:
            target_id = nearby_animals[0]["id"]

    elif action_str == "MOVE_TOWARD_FOOD":
        action_type = ActionType.MOVE
        food_cells = [
            c
            for c in nearby_cells
            if "food" in c.get("resources", {}) and c.get("structure_kind") != "wall"
        ]
        if food_cells:
            c = max(food_cells, key=lambda x: x["resources"]["food"])
            target_tuple = (c["x"], c["y"])
        else:
            target_tuple = (agent.x + rng.randint(-1, 1), agent.y + rng.randint(-1, 1))

    elif action_str == "MOVE_TOWARD_AGENT":
        action_type = ActionType.MOVE
        if nearby_agents:
            a = nearby_agents[0]
            dx = 0 if a["x"] == agent.x else (1 if a["x"] > agent.x else -1)
            dy = 0 if a["y"] == agent.y else (1 if a["y"] > agent.y else -1)
            target_tuple = (agent.x + dx, agent.y + dy)
        else:
            target_tuple = (agent.x + rng.randint(-1, 1), agent.y + rng.randint(-1, 1))

    elif action_str == "MOVE_TOWARD_PREY":
        action_type = ActionType.MOVE
        prey = [an for an in nearby_animals if an.get("kind") == "rabbit"]
        if prey:
            p = prey[0]
            dx = 0 if p["x"] == agent.x else (1 if p["x"] > agent.x else -1)
            dy = 0 if p["y"] == agent.y else (1 if p["y"] > agent.y else -1)
            target_tuple = (agent.x + dx, agent.y + dy)
        else:
            target_tuple = (agent.x + rng.randint(-1, 1), agent.y + rng.randint(-1, 1))

    elif action_str == "FLEE":
        action_type = ActionType.MOVE
        threats = [an for an in nearby_animals if an.get("kind") == "wolf"] + [
            a for a in nearby_agents if a.get("faction_id") != agent.faction_id
        ]
        if threats:
            t = threats[0]
            dx = 1 if agent.x < t["x"] else -1
            dy = 1 if agent.y < t["y"] else -1
            target_tuple = (agent.x - dx, agent.y - dy)
        else:
            target_tuple = (agent.x + rng.randint(-1, 1), agent.y + rng.randint(-1, 1))

    elif action_str == "EXPLORE":
        action_type = ActionType.MOVE
        target_tuple = (agent.x + rng.randint(-1, 1), agent.y + rng.randint(-1, 1))

    else:
        # Fallback
        action_type = ActionType.IDLE

    # Pack into expected dict
    action = {"type": action_type, "actor_id": agent.id, "payload": payload}
    if target_tuple is not None:
        action["target"] = target_tuple
    elif target_id is not None:
        action["target"] = target_id

    return typing.cast(Action, action)


def _q_learning_decide(agent: Agent, observation: dict[str, Any], rng: random.Random) -> Action:
    """Make a decision using epsilon-greedy Q-Learning."""
    state_str = _get_discrete_state(agent, observation)
    agent.state_representation = state_str

    if agent.q_table is None:
        agent.q_table = {}

    if state_str not in agent.q_table:
        agent.q_table[state_str] = {a: 0.0 for a in RL_ACTIONS}

    q_vals = agent.q_table[state_str]

    if rng.random() < agent.epsilon:
        chosen = rng.choice(RL_ACTIONS)
    else:
        # Find action with max Q (break ties randomly)
        max_val = max(q_vals.values())
        best_actions = [a for a, v in q_vals.items() if v == max_val]
        chosen = rng.choice(best_actions)

    agent.last_action = chosen
    return _map_abstract_action(chosen, agent, observation, rng)


def decide(agent: Agent, observation: dict[str, Any], rng: random.Random) -> Action:
    """Decide an action based on agent traits and observations.

    Routes to Q-Learning if agent.q_table is initialized, otherwise uses legacy heuristic.
    """
    if agent.q_table is not None:
        return _q_learning_decide(agent, observation, rng)

    # === LEGACY HEURISTIC FALLBACK ===
    stats = observation["self_stats"]
    traits = observation["self_traits"]
    current_cell = observation["current_cell"]
    nearby_agents = observation["nearby_agents"]

    hunger = stats.get("hunger", 0.0)
    energy = stats.get("energy", 0.0)
    weather_state = observation.get("weather_state", "Spring")

    hunger_threshold = 10.0 if weather_state == "Autumn" else 5.0

    if (hunger > hunger_threshold or energy < 40.0) and has_resource(agent.inventory, "food"):
        return Action(
            type=ActionType.EAT,
            actor_id=agent.id,
            target=None,
            payload={"resource": "food"},
        )

    cell_resources = current_cell.get("resources", {})
    if cell_resources:
        if weather_state == "Autumn" and "food" in cell_resources:
            best_resource = "food"
        else:
            best_resource = max(cell_resources, key=lambda r: cell_resources[r])
        return Action(
            type=ActionType.COLLECT,
            actor_id=agent.id,
            target=(current_cell["x"], current_cell["y"]),
            payload={"resource": best_resource},
        )

    aggression = traits.get("aggression", 0.0)
    if nearby_agents and rng.random() < aggression:
        target_agent = rng.choice(nearby_agents)
        return Action(
            type=ActionType.ATTACK,
            actor_id=agent.id,
            target=target_agent["id"],
            payload={},
        )

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

    from aether.utils.constants import DEFAULT_RULE_PARAMS

    repro_threshold = DEFAULT_RULE_PARAMS["reproduction"].get("energy_threshold", 60.0)
    age = stats.get("age", 0.0)
    if energy >= repro_threshold and age >= 20.0:
        return Action(
            type=ActionType.REPRODUCE,
            actor_id=agent.id,
            target=None,
            payload={},
        )

    material = agent.inventory.get("material", 0.0)
    if material >= 20.0:
        if weather_state in ["Autumn", "Winter"] and current_cell.get("structure_kind") is None:
            return Action(
                type=ActionType.BUILD,
                actor_id=agent.id,
                target=(current_cell["x"], current_cell["y"]),
                payload={"structure_type": "nest"},
            )

        if aggression > 0.6 and material >= 15.0:
            empty_spots = [
                c
                for c in observation.get("nearby_cells", [])
                if c.get("structure_kind") is None and c.get("agent_count", 0) == 0
            ]
            if empty_spots:
                target_cell = rng.choice(empty_spots)
                return Action(
                    type=ActionType.BUILD,
                    actor_id=agent.id,
                    target=(target_cell["x"], target_cell["y"]),
                    payload={"structure_type": "wall"},
                )

    nearby = observation.get("nearby_cells", [])
    memory = observation.get("memory", [])
    feared_agents = {m["agent_id"] for m in memory if m.get("type") == "attacked_by"}
    trusted_agents = {m["agent_id"] for m in memory if m.get("type") == "successful_trade"}

    best_move = None
    best_score = -999.0

    for c in nearby:
        if c.get("structure_kind") == "wall":
            continue

        score = 0.0
        if "food" in c.get("resources", {}) and (
            hunger > hunger_threshold or weather_state == "Autumn"
        ):
            score += 10.0
        elif c.get("resources"):
            score += 5.0

        c_agents = [a for a in nearby_agents if a["x"] == c["x"] and a["y"] == c["y"]]
        for ca in c_agents:
            if ca["id"] in feared_agents:
                score -= 50.0
            if ca["id"] in trusted_agents:
                score += 20.0

        score += rng.uniform(0, 0.5)

        if score > best_score:
            best_score = score
            best_move = (c["x"], c["y"])

    if best_score > -40.0 and best_move:
        return Action(
            type=ActionType.MOVE,
            actor_id=agent.id,
            target=best_move,
            payload={},
        )

    dx = rng.randint(-1, 1)
    dy = rng.randint(-1, 1)
    return Action(
        type=ActionType.MOVE,
        actor_id=agent.id,
        target=(agent.x + dx, agent.y + dy),
        payload={},
    )

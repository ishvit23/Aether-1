import random

from aether.actions.action import ActionType
from aether.actions.move_action import execute_move
from aether.agents.agent import Agent
from aether.agents.decision import decide, observe
from aether.rules.combat_rule import CombatRule
from aether.rules.hunger_rule import HungerRule
from aether.rules.weather_rule import WeatherRule
from aether.world.world import World


def test_factions_prevent_combat():
    world = World(10, 10, wrap=False)
    a = Agent(id=1, x=5, y=5, traits={"strength": 10.0}, stats={"health": 100.0}, faction_id="Red")
    b = Agent(id=2, x=5, y=5, traits={"strength": 5.0}, stats={"health": 100.0}, faction_id="Red")
    world.add_agent(a)
    world.add_agent(b)

    # Force combat decisions
    a.current_action = {"type": "attack", "actor_id": 1, "target": 2, "payload": {}}
    b.current_action = {"type": "attack", "actor_id": 2, "target": 1, "payload": {}}

    rule = CombatRule({})
    rule.apply(world, tick=1)

    # Since they are same faction, health should not decrease
    assert a.health == 100.0
    assert b.health == 100.0


def test_weather_and_hunger_scaling():
    world = World(10, 10, wrap=False)
    world.weather_state = "Spring"
    a = Agent(id=1, x=5, y=5, stats={"health": 100.0, "energy": 100.0, "hunger": 0.0})
    world.add_agent(a)

    weather = WeatherRule({"season_length": 100})
    hunger = HungerRule({"decay_rate": 1.0})

    # Tick 0: Spring
    weather.apply(world, tick=0)
    assert world.weather_state == "Spring"
    hunger.apply(world, tick=0)
    assert a.energy == 99.0

    # Fast forward to Winter (Tick 300)
    weather.apply(world, tick=300)
    assert world.weather_state == "Winter"
    # Winter decay rate = 2.0
    hunger.apply(world, tick=300)
    assert a.energy == 97.0


def test_memory_fleeing():
    world = World(10, 10, wrap=False)
    a = Agent(id=1, x=5, y=5, stats={"health": 100.0, "energy": 100.0, "hunger": 0.0})
    # Agent 2 attacked Agent 1 before
    a.add_memory({"tick": 10, "agent_id": 2, "type": "attacked_by"})
    world.add_agent(a)

    # Agent 2 is directly north
    b = Agent(id=2, x=5, y=4, stats={"health": 100.0, "energy": 100.0})
    world.add_agent(b)

    rng = random.Random(42)
    obs = observe(a, world)
    action = decide(a, obs, rng)

    # Should move, but NOT toward attacker at (5,4)
    assert action["type"] == ActionType.MOVE
    assert action["target"] is not None
    assert action["target"] != (5, 4)


def test_building_walls_block_move():
    world = World(10, 10, wrap=False)
    a = Agent(id=1, x=5, y=5, stats={"energy": 100.0})
    world.add_agent(a)

    # Build wall at (6, 5)
    from aether.world.cell import StructureData

    world.get_cell(6, 5).structure = StructureData(kind="wall")

    # Attempt to move there
    result = execute_move(1, (6, 5), world)
    assert result["success"] is False
    assert result["reason"] == "blocked_by_wall"
    assert a.x == 5 and a.y == 5

    # Move normally to an open cell (4, 5)
    result = execute_move(1, (4, 5), world)
    assert result["success"] is True
    assert a.x == 4 and a.y == 5

import pytest
from aether.world.world import World
from aether.agents.agent import Agent
from aether.agents.animal import Animal
from aether.actions.hunt_action import execute_hunt

@pytest.fixture
def world() -> World:
    return World(width=5, height=5, seed=42)

def test_hunt_success_rabbit(world: World):
    agent = Agent(id=1, x=2, y=2)
    agent.health = 100.0
    agent.energy = 100.0
    world.add_agent(agent)
    rabbit = Animal(id=10, x=2, y=2, kind="rabbit")
    world.add_animal(rabbit)
    
    result = execute_hunt(1, 10, world)
    
    assert result["success"] is True
    assert result["food_gained"] > 0
    assert "food" in agent.inventory
    # Animal is removed from world immediately
    assert world.animals.get(10) is None

def test_hunt_fail_out_of_range(world: World):
    agent = Agent(id=1, x=0, y=0)
    agent.health = 100.0
    agent.energy = 100.0
    world.add_agent(agent)
    rabbit = Animal(id=10, x=2, y=2, kind="rabbit")
    world.add_animal(rabbit)
    
    result = execute_hunt(1, 10, world)
    
    assert result["success"] is False
    assert result["reason"] == "out_of_range"

def test_hunt_fail_wolf_retaliation_and_loss(world: World):
    agent = Agent(id=1, x=2, y=2)
    agent.health = 100.0
    agent.energy = 100.0
    agent.traits["strength"] = 0.0  # Forces loss vs wolf
    world.add_agent(agent)
    wolf = Animal(id=10, x=2, y=2, kind="wolf")
    world.add_animal(wolf)
    
    # Override RNG to ensure loss
    world.rng.random = lambda: 0.99 
    
    result = execute_hunt(1, 10, world)
    
    assert result["success"] is False
    assert result["reason"] == "hunt_failed"
    assert "damage_taken" in result
    assert agent.health < 100.0
    assert world.animals.get(10) is not None

def test_hunt_invalid_targets(world: World):
    agent = Agent(id=1, x=2, y=2)
    agent.health = 100.0
    agent.energy = 100.0
    world.add_agent(agent)
    
    res1 = execute_hunt(99, 10, world)
    assert res1["success"] is False
    assert res1["reason"] == "actor_dead"
    
    res2 = execute_hunt(1, None, world)
    assert res2["success"] is False
    assert res2["reason"] == "no_target"
    
    res3 = execute_hunt(1, 99, world)
    assert res3["success"] is False
    assert res3["reason"] == "target_dead"

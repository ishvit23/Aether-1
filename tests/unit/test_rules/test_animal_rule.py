import pytest
from aether.world.world import World
from aether.agents.animal import Animal
from aether.agents.agent import Agent
from aether.rules.animal_rule import AnimalRule

@pytest.fixture
def world() -> World:
    return World(width=10, height=10, seed=42)

def test_animal_rule_rabbit_spawning(world: World):
    rule = AnimalRule(params={"rabbit_spawn_prob": 1.0, "rabbit_cap": 5, "wolf_spawn_prob": 0.0})
    rule.apply(world, tick=1)
    # Should spawn exactly 1 rabbit because the spawning loop runs once per tick with 1.0 probability
    rabbits = [a for a in world.living_animals() if a.kind == "rabbit"]
    assert len(rabbits) == 1

def test_animal_rule_wolf_spawning(world: World):
    rule = AnimalRule(params={"rabbit_spawn_prob": 0.0, "wolf_spawn_prob": 1.0, "wolf_cap": 2})
    rule.apply(world, tick=1)
    wolves = [a for a in world.living_animals() if a.kind == "wolf"]
    assert len(wolves) == 1
    assert wolves[0].health == 150.0

def test_rabbit_fleeing(world: World):
    # Place a rabbit and an agent next to it to force fleeing
    rabbit = Animal(id=1, kind="rabbit", x=5, y=5)
    world.add_animal(rabbit)
    agent = Agent(id=10, x=5, y=4)
    agent.energy = 100.0
    agent.health = 100.0
    world.add_agent(agent)
    
    rule = AnimalRule(params={"rabbit_spawn_prob": 0.0, "wolf_spawn_prob": 0.0, "vision_radius": 3})
    rule.apply(world, tick=1)
    
    # Rabbit should move away from y=4, so y should become 6
    assert rabbit.y == 6

def test_wolf_hunting_agent(world: World):
    wolf = Animal(id=1, kind="wolf", x=5, y=5, health=150.0)
    world.add_animal(wolf)
    agent = Agent(id=10, x=5, y=6)
    agent.health = 100.0
    agent.energy = 100.0
    world.add_agent(agent)
    
    rule = AnimalRule(params={"rabbit_spawn_prob": 0.0, "wolf_spawn_prob": 0.0, "wolf_attack_damage": 20.0, "vision_radius": 3})
    rule.apply(world, tick=1)
    
    # Wolf should move into agent's tile and attack
    assert wolf.y == 6
    assert agent.health == 80.0

def test_wolf_hunting_rabbit(world: World):
    wolf = Animal(id=1, kind="wolf", x=5, y=5, health=150.0)
    world.add_animal(wolf)
    rabbit = Animal(id=2, kind="rabbit", x=5, y=5)
    world.add_animal(rabbit)
    
    rule = AnimalRule(params={"rabbit_spawn_prob": 0.0, "wolf_spawn_prob": 0.0, "vision_radius": 3})
    rule.apply(world, tick=1)
    
    # Wolf attacks rabbit to death (health=0)
    assert rabbit.health == 0.0

def test_remove_dead_animals(world: World):
    wolf = Animal(id=1, kind="wolf", x=5, y=5, health=0.0)
    rabbit = Animal(id=2, kind="rabbit", x=5, y=6, health=0.0)
    world.add_animal(wolf)
    world.add_animal(rabbit)
    
    rule = AnimalRule(params={})
    rule.apply(world, tick=1)
    
    assert len(world.living_animals()) == 0

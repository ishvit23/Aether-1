import pytest
from aether.world.world import World
from aether.world.cell import StructureData
from aether.rules.decay_rule import DecayRule

@pytest.fixture
def world() -> World:
    return World(width=5, height=5, seed=42)

def test_decay_rule_ignored_in_summer(world: World):
    cell = world.get_cell(2, 2)
    cell.structure = StructureData(kind="wall", health=100.0)
    world.weather_state = "Summer"
    
    rule = DecayRule(params={"wall_decay": 5.0})
    rule.apply(world, tick=1)
    
    assert cell.structure is not None
    assert cell.structure.health == 100.0

def test_decay_rule_active_in_winter(world: World):
    cell = world.get_cell(2, 2)
    cell.structure = StructureData(kind="wall", health=100.0)
    world.weather_state = "Winter"
    
    rule = DecayRule(params={"wall_decay": 15.0})
    rule.apply(world, tick=1)
    
    assert cell.structure is not None
    assert cell.structure.health == 85.0

def test_decay_rule_destroys_structure(world: World):
    cell = world.get_cell(2, 2)
    cell.structure = StructureData(kind="nest", health=2.0)
    world.weather_state = "Winter"
    
    rule = DecayRule(params={"nest_decay": 5.0})
    rule.apply(world, tick=1)
    
    # Destroyed because 2 - 5 < 0
    assert cell.structure is None

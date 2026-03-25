"""Unit tests for the BuildRule and related build mechanics."""

import pytest

from aether.actions.build_action import execute_build
from aether.agents.agent import Agent
from aether.rules.build_rule import BuildRule
from aether.world.world import World


@pytest.fixture
def world():
    return World(width=10, height=10)


@pytest.fixture
def agent(world):
    a = Agent(id=1, x=5, y=5)
    world.add_agent(a)
    return a


def test_nest_healing_effect(world, agent):
    # Setup a nest at (5, 5)
    cell = world.get_cell(5, 5)
    from aether.world.cell import StructureData

    cell.structure = StructureData(kind="nest")

    agent.energy = 50.0

    rule = BuildRule(params={"nest_heal": 5.0})
    rule.apply(world, tick=1)

    # Agent should heal due to standing on the nest
    assert agent.energy == 55.0


def test_nest_healing_adjacent(world, agent):
    # Setup a nest adjacent at (6, 5)
    cell = world.get_cell(6, 5)
    from aether.world.cell import StructureData

    cell.structure = StructureData(kind="nest")

    agent.energy = 80.0

    rule = BuildRule(params={"nest_heal": 10.0})
    rule.apply(world, tick=1)

    # Agent should heal due to being adjacent
    assert agent.energy == 90.0


def test_build_action_costs_and_validation(world, agent):
    # Missing materials
    agent.inventory["material"] = 5.0
    result = execute_build(agent.id, (5, 6), {"structure_type": "wall"}, world)
    assert not result["success"]
    assert result["reason"] == "insufficient_material"

    # Valid wall creation
    agent.inventory["material"] = 20.0
    result = execute_build(agent.id, (5, 6), {"structure_type": "wall"}, world)
    assert result["success"]
    assert agent.inventory["material"] == 5.0
    assert world.get_cell(5, 6).structure is not None
    assert world.get_cell(5, 6).structure.kind == "wall"

    # Cell already occupied by a structure
    agent.inventory["material"] = 50.0
    result = execute_build(agent.id, (5, 6), {"structure_type": "nest"}, world)
    assert not result["success"]
    assert result["reason"] == "structure_already_exists"

    # Cannot build wall on occupied agents
    agent2 = Agent(id=2, x=7, y=7)
    world.add_agent(agent2)

    result = execute_build(agent.id, (7, 7), {"structure_type": "wall"}, world)
    assert not result["success"]
    assert result["reason"] == "cell_occupied"

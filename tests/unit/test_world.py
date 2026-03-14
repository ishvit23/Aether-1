"""Unit tests for World and Cell modules."""

from __future__ import annotations

import pytest

from aether.agents.agent import Agent
from aether.utils.constants import DEFAULT_STATS
from aether.world.cell import Cell
from aether.world.world import World


class TestCell:
    """Tests for the Cell dataclass."""

    def test_cell_creation(self):
        cell = Cell(x=0, y=0)
        assert cell.x == 0
        assert cell.y == 0
        assert cell.resources == {}
        assert cell.agents == []
        assert cell.terrain is None

    def test_add_resource(self):
        cell = Cell(x=0, y=0)
        cell.add_resource("food", 5.0)
        assert cell.resources["food"] == 5.0
        cell.add_resource("food", 3.0)
        assert cell.resources["food"] == 8.0

    def test_remove_resource(self):
        cell = Cell(x=0, y=0)
        cell.add_resource("food", 10.0)
        removed = cell.remove_resource("food", 3.0)
        assert removed == 3.0
        assert cell.resources["food"] == 7.0

    def test_remove_resource_more_than_available(self):
        cell = Cell(x=0, y=0)
        cell.add_resource("food", 2.0)
        removed = cell.remove_resource("food", 5.0)
        assert removed == 2.0
        assert "food" not in cell.resources

    def test_remove_resource_nonexistent(self):
        cell = Cell(x=0, y=0)
        removed = cell.remove_resource("gold", 5.0)
        assert removed == 0.0

    def test_add_remove_agent(self):
        cell = Cell(x=0, y=0)
        cell.add_agent(1)
        assert 1 in cell.agents
        cell.add_agent(1)  # duplicate should not add
        assert cell.agents.count(1) == 1
        cell.remove_agent(1)
        assert 1 not in cell.agents

    def test_has_resources(self):
        cell = Cell(x=0, y=0)
        assert not cell.has_resources()
        cell.add_resource("food", 1.0)
        assert cell.has_resources()

    def test_agent_count(self):
        cell = Cell(x=0, y=0)
        assert cell.agent_count() == 0
        cell.add_agent(1)
        cell.add_agent(2)
        assert cell.agent_count() == 2


class TestWorld:
    """Tests for the World class."""

    def test_world_creation(self):
        world = World(width=10, height=10)
        assert world.width == 10
        assert world.height == 10
        assert world.wrap is True
        assert world.tick == 0
        assert len(world.grid) == 10
        assert len(world.grid[0]) == 10

    def test_get_cell(self):
        world = World(width=10, height=10)
        cell = world.get_cell(5, 5)
        assert cell.x == 5
        assert cell.y == 5

    def test_torus_wrapping(self):
        world = World(width=10, height=10, wrap=True)
        cell = world.get_cell(-1, -1)
        assert cell.x == 9
        assert cell.y == 9
        cell2 = world.get_cell(10, 10)
        assert cell2.x == 0
        assert cell2.y == 0

    def test_no_wrap_raises(self):
        world = World(width=10, height=10, wrap=False)
        with pytest.raises(IndexError):
            world.get_cell(-1, 0)
        with pytest.raises(IndexError):
            world.get_cell(10, 0)

    def test_get_neighbors(self):
        world = World(width=10, height=10, wrap=True)
        neighbors = world.get_neighbors(5, 5, radius=1)
        assert len(neighbors) == 8  # 3x3 minus center

    def test_get_neighbors_corner_with_wrap(self):
        world = World(width=10, height=10, wrap=True)
        neighbors = world.get_neighbors(0, 0, radius=1)
        assert len(neighbors) == 8  # wrapping means all neighbors exist

    def test_get_neighbors_corner_no_wrap(self):
        world = World(width=10, height=10, wrap=False)
        neighbors = world.get_neighbors(0, 0, radius=1)
        assert len(neighbors) == 3  # only (1,0), (0,1), (1,1)

    def test_add_agent(self):
        world = World(width=10, height=10, seed=42)
        agent = Agent(id=0, x=5, y=5, stats=dict(DEFAULT_STATS))
        world.add_agent(agent)
        assert 0 in world.agents
        assert 0 in world.get_cell(5, 5).agents

    def test_remove_agent(self):
        world = World(width=10, height=10, seed=42)
        agent = Agent(id=0, x=5, y=5, stats=dict(DEFAULT_STATS))
        world.add_agent(agent)
        removed = world.remove_agent(0)
        assert removed is agent
        assert 0 not in world.agents
        assert 0 not in world.get_cell(5, 5).agents

    def test_move_agent(self):
        world = World(width=10, height=10, seed=42)
        agent = Agent(id=0, x=5, y=5, stats=dict(DEFAULT_STATS))
        world.add_agent(agent)
        world.move_agent(0, 7, 3)
        assert agent.x == 7
        assert agent.y == 3
        assert 0 not in world.get_cell(5, 5).agents
        assert 0 in world.get_cell(7, 3).agents

    def test_move_agent_wrapping(self):
        world = World(width=10, height=10, wrap=True, seed=42)
        agent = Agent(id=0, x=0, y=0, stats=dict(DEFAULT_STATS))
        world.add_agent(agent)
        world.move_agent(0, -1, -1)
        assert agent.x == 9
        assert agent.y == 9

    def test_next_agent_id(self):
        world = World(width=10, height=10)
        assert world.next_agent_id() == 0
        assert world.next_agent_id() == 1
        assert world.next_agent_id() == 2

    def test_population_size(self, small_world):
        assert small_world.population_size() == 5

    def test_living_agents_sorted(self, small_world):
        agents = small_world.living_agents()
        ids = [a.id for a in agents]
        assert ids == sorted(ids)

    def test_deterministic_with_seed(self):
        world1 = World(width=10, height=10, seed=42)
        world2 = World(width=10, height=10, seed=42)
        vals1 = [world1.rng.random() for _ in range(10)]
        vals2 = [world2.rng.random() for _ in range(10)]
        assert vals1 == vals2

    def test_post_tick_cleanup(self):
        world = World(width=10, height=10)
        world.get_cell(0, 0).resources["food"] = 0.0
        world.get_cell(0, 0).resources["material"] = 5.0
        world.post_tick_cleanup(0)
        assert "food" not in world.get_cell(0, 0).resources
        assert world.get_cell(0, 0).resources["material"] == 5.0
        assert world.tick == 1

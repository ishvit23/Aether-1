"""Unit tests for the death rule."""

from __future__ import annotations

from aether.agents.agent import Agent
from aether.rules.death_rule import DeathRule
from aether.utils.constants import DEFAULT_STATS
from aether.world.world import World


class TestDeathRule:
    """Tests for DeathRule."""

    def test_removes_zero_energy_agent(self):
        world = World(width=10, height=10, seed=0)
        stats = dict(DEFAULT_STATS)
        stats["energy"] = 0.0
        agent = Agent(id=0, x=0, y=0, stats=stats)
        world.add_agent(agent)

        rule = DeathRule({"energy_floor": 0.0, "max_age": 500.0})
        rule.apply(world, tick=0)

        assert world.population_size() == 0

    def test_removes_zero_health_agent(self):
        world = World(width=10, height=10, seed=0)
        stats = dict(DEFAULT_STATS)
        stats["health"] = 0.0
        agent = Agent(id=0, x=0, y=0, stats=stats)
        world.add_agent(agent)

        rule = DeathRule({"energy_floor": 0.0, "max_age": 500.0})
        rule.apply(world, tick=0)

        assert world.population_size() == 0

    def test_removes_old_agent(self):
        world = World(width=10, height=10, seed=0)
        stats = dict(DEFAULT_STATS)
        stats["age"] = 600.0
        agent = Agent(id=0, x=0, y=0, stats=stats)
        world.add_agent(agent)

        rule = DeathRule({"energy_floor": 0.0, "max_age": 500.0})
        rule.apply(world, tick=0)

        assert world.population_size() == 0

    def test_keeps_healthy_agent(self):
        world = World(width=10, height=10, seed=0)
        agent = Agent(id=0, x=0, y=0, stats=dict(DEFAULT_STATS))
        world.add_agent(agent)

        rule = DeathRule({"energy_floor": 0.0, "max_age": 500.0})
        rule.apply(world, tick=0)

        assert world.population_size() == 1

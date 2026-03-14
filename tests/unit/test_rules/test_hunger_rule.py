"""Unit tests for the hunger rule."""

from __future__ import annotations

from aether.agents.agent import Agent
from aether.rules.hunger_rule import HungerRule
from aether.utils.constants import DEFAULT_STATS
from aether.world.world import World


class TestHungerRule:
    """Tests for HungerRule."""

    def test_energy_decay(self):
        world = World(width=10, height=10, seed=0)
        agent = Agent(id=0, x=0, y=0, stats=dict(DEFAULT_STATS))
        world.add_agent(agent)

        rule = HungerRule({"decay_rate": 2.0})
        rule.apply(world, tick=0)

        assert agent.energy == 98.0
        assert agent.hunger == 1.0
        assert agent.age == 1.0

    def test_energy_does_not_go_below_zero(self):
        world = World(width=10, height=10, seed=0)
        stats = dict(DEFAULT_STATS)
        stats["energy"] = 1.0
        agent = Agent(id=0, x=0, y=0, stats=stats)
        world.add_agent(agent)

        rule = HungerRule({"decay_rate": 5.0})
        rule.apply(world, tick=0)

        assert agent.energy == 0.0

    def test_applies_to_all_agents(self, small_world):
        rule = HungerRule({"decay_rate": 1.0})
        initial_energies = {a.id: a.energy for a in small_world.living_agents()}
        rule.apply(small_world, tick=0)
        for agent in small_world.living_agents():
            assert agent.energy == initial_energies[agent.id] - 1.0

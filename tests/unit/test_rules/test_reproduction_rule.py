"""Unit tests for reproduction rule."""

from __future__ import annotations

from aether.agents.agent import Agent
from aether.rules.reproduction_rule import ReproductionRule
from aether.utils.constants import DEFAULT_STATS
from aether.world.world import World


class TestReproductionRule:
    """Tests for ReproductionRule."""

    def test_reproduction_when_energy_sufficient(self):
        world = World(width=10, height=10, seed=42)
        stats = dict(DEFAULT_STATS)
        stats["energy"] = 100.0
        traits = {
            "speed": 0.5,
            "strength": 0.5,
            "intelligence": 0.5,
            "aggression": 0.3,
            "greed": 0.3,
            "cooperation": 0.5,
        }
        agent = Agent(id=0, x=5, y=5, stats=stats, traits=traits)
        world.add_agent(agent)

        rule = ReproductionRule({"energy_threshold": 80.0, "child_cost": 30.0})
        rule.apply(world, tick=0)

        assert world.population_size() == 2  # parent + child
        assert agent.energy == 70.0  # 100 - 30

    def test_no_reproduction_insufficient_energy(self):
        world = World(width=10, height=10, seed=42)
        stats = dict(DEFAULT_STATS)
        stats["energy"] = 50.0
        agent = Agent(id=0, x=5, y=5, stats=stats)
        world.add_agent(agent)

        rule = ReproductionRule({"energy_threshold": 80.0, "child_cost": 30.0})
        rule.apply(world, tick=0)

        assert world.population_size() == 1

    def test_child_has_mutated_traits(self):
        world = World(width=10, height=10, seed=42)
        stats = dict(DEFAULT_STATS)
        stats["energy"] = 100.0
        traits = {
            "speed": 0.5,
            "strength": 0.5,
            "intelligence": 0.5,
            "aggression": 0.3,
            "greed": 0.3,
            "cooperation": 0.5,
        }
        agent = Agent(id=0, x=5, y=5, stats=stats, traits=traits)
        world.add_agent(agent)

        rule = ReproductionRule(
            {"energy_threshold": 80.0, "child_cost": 30.0, "mutation_rate": 1.0, "max_delta": 0.2}
        )
        rule.apply(world, tick=0)

        agents = world.living_agents()
        child = [a for a in agents if a.id != 0][0]
        # With mutation_rate=1.0, child traits should differ
        assert child.traits != agent.traits

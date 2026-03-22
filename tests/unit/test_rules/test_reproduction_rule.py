"""Unit tests for action-based reproduction (reproduce_action.py)."""

from __future__ import annotations

from aether.actions.reproduce_action import execute_reproduce
from aether.agents.agent import Agent
from aether.utils.constants import DEFAULT_STATS
from aether.world.world import World


class TestReproduceAction:
    """Tests for execute_reproduce action."""

    def test_reproduction_when_energy_sufficient(self):
        world = World(width=10, height=10, seed=42)
        stats = dict(DEFAULT_STATS)
        stats["energy"] = 100.0
        stats["age"] = 25.0
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

        result = execute_reproduce(actor_id=0, world=world, child_cost=30.0)

        assert result["success"] is True
        assert world.population_size() == 2  # parent + child
        assert agent.energy == 70.0  # 100 - 30

    def test_no_reproduction_insufficient_energy(self):
        world = World(width=10, height=10, seed=42)
        stats = dict(DEFAULT_STATS)
        stats["energy"] = 20.0
        agent = Agent(id=0, x=5, y=5, stats=stats)
        world.add_agent(agent)

        result = execute_reproduce(actor_id=0, world=world, child_cost=30.0)

        assert result["success"] is False
        assert result["reason"] == "insufficient_energy"
        assert world.population_size() == 1

    def test_child_has_mutated_traits(self):
        world = World(width=10, height=10, seed=42)
        stats = dict(DEFAULT_STATS)
        stats["energy"] = 100.0
        stats["age"] = 25.0
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

        result = execute_reproduce(
            actor_id=0,
            world=world,
            child_cost=30.0,
            mutation_rate=1.0,
            max_delta=0.2,
        )

        assert result["success"] is True
        agents = world.living_agents()
        child = [a for a in agents if a.id != 0][0]
        # With mutation_rate=1.0, child traits should differ
        assert child.traits != agent.traits

    def test_population_cap(self):
        world = World(width=10, height=10, seed=42)
        # Fill world to cap
        for i in range(150):
            stats = dict(DEFAULT_STATS)
            stats["energy"] = 100.0
            agent = Agent(id=i, x=i % 10, y=i // 10, stats=stats)
            world.add_agent(agent)

        result = execute_reproduce(actor_id=0, world=world, child_cost=30.0)
        assert result["success"] is False
        assert result["reason"] == "population_cap"

    def test_cooldown(self):
        world = World(width=10, height=10, seed=42)
        stats = dict(DEFAULT_STATS)
        stats["energy"] = 100.0
        stats["last_repro_tick"] = 5.0
        agent = Agent(id=0, x=5, y=5, stats=stats)
        world.add_agent(agent)
        world.tick = 10  # Only 5 ticks since last repro, cooldown is 30

        result = execute_reproduce(actor_id=0, world=world, child_cost=30.0)
        assert result["success"] is False
        assert result["reason"] == "cooldown"

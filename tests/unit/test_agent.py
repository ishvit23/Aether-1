"""Unit tests for the Agent model."""

from __future__ import annotations

from aether.agents.agent import Agent
from aether.agents.inventory import add_resource, has_resource, remove_resource, total_resources
from aether.agents.traits import generate_traits, mutate_traits
from aether.utils.constants import DEFAULT_STATS
from aether.utils.rng import create_rng


class TestAgent:
    """Tests for the Agent dataclass."""

    def test_agent_creation(self):
        agent = Agent(id=0, x=5, y=5, stats=dict(DEFAULT_STATS))
        assert agent.id == 0
        assert agent.x == 5
        assert agent.y == 5
        assert agent.energy == 100.0
        assert agent.health == 100.0
        assert agent.state == "idle"

    def test_stat_properties(self):
        agent = Agent(id=0, x=0, y=0, stats=dict(DEFAULT_STATS))
        agent.energy = 50.0
        assert agent.energy == 50.0
        assert agent.stats["energy"] == 50.0

        agent.health = 75.0
        assert agent.health == 75.0

        agent.hunger = 10.0
        assert agent.hunger == 10.0

        agent.age = 5.0
        assert agent.age == 5.0

    def test_is_alive(self):
        agent = Agent(id=0, x=0, y=0, stats=dict(DEFAULT_STATS))
        assert agent.is_alive()

        agent.energy = 0.0
        assert not agent.is_alive()

        agent.energy = 50.0
        agent.health = 0.0
        assert not agent.is_alive()

    def test_default_memory_empty(self):
        agent = Agent(id=0, x=0, y=0)
        assert agent.memory == []


class TestTraits:
    """Tests for trait generation and mutation."""

    def test_generate_traits(self):
        rng = create_rng(42)
        traits = generate_traits(rng)
        assert "speed" in traits
        assert "strength" in traits
        assert "intelligence" in traits
        assert "aggression" in traits
        assert "greed" in traits
        assert "cooperation" in traits
        assert all(0.0 <= v <= 1.0 for v in traits.values())

    def test_generate_traits_deterministic(self):
        traits1 = generate_traits(create_rng(42))
        traits2 = generate_traits(create_rng(42))
        assert traits1 == traits2

    def test_mutate_traits(self):
        rng = create_rng(42)
        parent = generate_traits(rng)
        child = mutate_traits(parent, rng, mutation_rate=1.0, max_delta=0.1)
        # With rate=1.0, all traits should be mutated
        assert child != parent
        # All within bounds
        assert all(0.0 <= v <= 1.0 for v in child.values())

    def test_mutate_traits_no_mutation(self):
        rng = create_rng(42)
        parent = generate_traits(rng)
        child = mutate_traits(parent, rng, mutation_rate=0.0, max_delta=0.1)
        assert child == parent


class TestInventory:
    """Tests for inventory helper functions."""

    def test_add_resource(self):
        inv: dict[str, float] = {}
        add_resource(inv, "food", 5.0)
        assert inv["food"] == 5.0
        add_resource(inv, "food", 3.0)
        assert inv["food"] == 8.0

    def test_remove_resource(self):
        inv = {"food": 10.0}
        removed = remove_resource(inv, "food", 3.0)
        assert removed == 3.0
        assert inv["food"] == 7.0

    def test_remove_more_than_available(self):
        inv = {"food": 2.0}
        removed = remove_resource(inv, "food", 5.0)
        assert removed == 2.0
        assert "food" not in inv

    def test_has_resource(self):
        inv = {"food": 5.0}
        assert has_resource(inv, "food")
        assert not has_resource(inv, "gold")
        assert not has_resource(inv, "food", min_amount=10.0)

    def test_total_resources(self):
        inv = {"food": 5.0, "material": 3.0}
        assert total_resources(inv) == 8.0
        assert total_resources({}) == 0.0

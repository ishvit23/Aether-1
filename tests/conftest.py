"""Shared test fixtures for Aether-1."""

from __future__ import annotations

import pytest

from aether.agents.agent import Agent
from aether.agents.traits import generate_traits
from aether.engine.rule_engine import RuleEngine, register_all_rules
from aether.utils.constants import DEFAULT_STATS
from aether.utils.rng import create_rng
from aether.world.world import World


@pytest.fixture
def rng():
    """Seeded RNG for deterministic tests."""
    return create_rng(42)


@pytest.fixture
def small_world():
    """A small 10x10 world with 5 agents for testing."""
    world = World(width=10, height=10, wrap=True, seed=42)
    for _ in range(5):
        aid = world.next_agent_id()
        x = world.rng.randint(0, 9)
        y = world.rng.randint(0, 9)
        traits = generate_traits(world.rng)
        stats = dict(DEFAULT_STATS)
        agent = Agent(id=aid, x=x, y=y, traits=traits, stats=stats)
        world.add_agent(agent)
    return world


@pytest.fixture
def empty_world():
    """An empty 10x10 world with no agents."""
    return World(width=10, height=10, wrap=True, seed=0)


@pytest.fixture
def rule_engine():
    """A rule engine with all V1 rules registered."""
    register_all_rules()
    engine = RuleEngine()
    return engine

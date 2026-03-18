"""Integration test: seeded full simulation run."""

from __future__ import annotations

import pytest

from aether.agents.agent import Agent
from aether.agents.traits import generate_traits
from aether.engine.rule_engine import RuleEngine, register_all_rules
from aether.engine.tick_engine import TickEngine
from aether.utils.constants import DEFAULT_STATS
from aether.world.world import World


@pytest.fixture
def seeded_simulation():
    """Build a full seeded simulation for integration testing."""
    register_all_rules()
    world = World(width=20, height=20, wrap=True, seed=42)
    for _ in range(10):
        aid = world.next_agent_id()
        x = world.rng.randint(0, 19)
        y = world.rng.randint(0, 19)
        traits = generate_traits(world.rng)
        stats = dict(DEFAULT_STATS)
        agent = Agent(id=aid, x=x, y=y, traits=traits, stats=stats)
        world.add_agent(agent)

    rule_engine = RuleEngine()
    rule_engine.load_rules(
        [
            "hunger",
            "resource_spawn",
            "collect",
            "combat",
            "trade",
            "mutation",
            "death",
        ],
        {
            "hunger": {"decay_rate": 0.5},
            "resource_spawn": {"spawn_interval": 1, "spawn_prob": 0.05, "amount": 8.0},
            "collect": {"max_per_tick": 5.0},
            "combat": {"damage_multiplier": 5.0},
            "trade": {"offer_threshold": 3.0, "acceptance_prob_base": 0.5},
            "mutation": {"rate": 0.05, "max_delta": 0.1},
            "death": {"energy_floor": 0.0, "max_age": 300.0},
        },
    )
    engine = TickEngine(world=world, rule_engine=rule_engine, max_ticks=100)
    return engine, world


@pytest.mark.integration
class TestFullRun:
    """Integration tests for a full seeded simulation run."""

    def test_simulation_completes(self, seeded_simulation):
        engine, world = seeded_simulation
        engine.run()
        # Simulation should complete without errors
        assert world.tick == 100

    def test_population_nonzero_at_tick_50(self, seeded_simulation):
        engine, world = seeded_simulation
        for tick in range(50):
            engine.run_tick(tick)
        # Population should still be > 0 at tick 50
        assert world.population_size() > 0

    def test_deterministic_outcome(self):
        """Two identical seeded runs should produce the same final population."""
        register_all_rules()

        def build_and_run(seed: int) -> int:
            world = World(width=15, height=15, wrap=True, seed=seed)
            for _ in range(8):
                aid = world.next_agent_id()
                x = world.rng.randint(0, 14)
                y = world.rng.randint(0, 14)
                traits = generate_traits(world.rng)
                stats = dict(DEFAULT_STATS)
                agent = Agent(id=aid, x=x, y=y, traits=traits, stats=stats)
                world.add_agent(agent)

            rule_engine = RuleEngine()
            rule_engine.load_rules(
                ["hunger", "resource_spawn", "collect", "death"],
                {
                    "hunger": {"decay_rate": 0.5},
                    "resource_spawn": {"spawn_interval": 1, "spawn_prob": 0.05, "amount": 5.0},
                    "collect": {"max_per_tick": 5.0},
                    "death": {"energy_floor": 0.0, "max_age": 500.0},
                },
            )
            engine = TickEngine(world=world, rule_engine=rule_engine, max_ticks=50)
            engine.run()
            return world.population_size()

        pop1 = build_and_run(99)
        pop2 = build_and_run(99)
        assert pop1 == pop2

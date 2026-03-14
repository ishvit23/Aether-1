"""Unit tests for the engine: TickEngine and RuleEngine."""

from __future__ import annotations

from aether.agents.agent import Agent
from aether.agents.traits import generate_traits
from aether.engine.rule_engine import RuleEngine, register_all_rules
from aether.engine.tick_engine import TickEngine
from aether.rules.base_rule import Rule
from aether.utils.constants import DEFAULT_STATS
from aether.world.world import World


class DummyRule(Rule):
    """A test rule that counts how many times apply() is called."""

    name = "dummy"
    call_count = 0

    def apply(self, world: World, tick: int) -> None:
        DummyRule.call_count += 1


class TestRuleEngine:
    """Tests for the RuleEngine."""

    def test_register_and_load(self):
        RuleEngine.register("dummy", DummyRule)
        engine = RuleEngine()
        engine.load_rules(["dummy"], {"dummy": {}})
        assert len(engine.rules) == 1
        assert engine.rules[0].name == "dummy"

    def test_apply_all(self, small_world):
        DummyRule.call_count = 0
        RuleEngine.register("dummy", DummyRule)
        engine = RuleEngine()
        engine.load_rules(["dummy"], {"dummy": {}})
        engine.apply_all(small_world, tick=0)
        assert DummyRule.call_count == 1

    def test_load_unknown_rule(self):
        engine = RuleEngine()
        import pytest

        with pytest.raises(KeyError, match="not_a_rule"):
            engine.load_rules(["not_a_rule"], {})

    def test_register_all_rules(self):
        register_all_rules()
        registry = RuleEngine.get_registered()
        expected = [
            "hunger",
            "movement",
            "resource_spawn",
            "collect",
            "combat",
            "trade",
            "reproduction",
            "mutation",
            "death",
        ]
        for name in expected:
            assert name in registry


class TestTickEngine:
    """Tests for the TickEngine."""

    def test_single_tick(self, small_world):
        register_all_rules()
        rule_engine = RuleEngine()
        rule_engine.load_rules(
            ["hunger", "death"],
            {"hunger": {"decay_rate": 1.0}, "death": {"energy_floor": 0.0, "max_age": 500.0}},
        )
        engine = TickEngine(world=small_world, rule_engine=rule_engine, max_ticks=1)
        engine.run_tick(0)
        # All agents should have lost energy
        for agent in small_world.living_agents():
            assert agent.energy < 100.0

    def test_deterministic_runs(self):
        """Two runs with the same seed should produce identical results."""
        register_all_rules()

        def run_simulation(seed: int) -> int:
            world = World(width=10, height=10, wrap=True, seed=seed)
            for _ in range(5):
                aid = world.next_agent_id()
                x = world.rng.randint(0, 9)
                y = world.rng.randint(0, 9)
                traits = generate_traits(world.rng)
                stats = dict(DEFAULT_STATS)
                agent = Agent(id=aid, x=x, y=y, traits=traits, stats=stats)
                world.add_agent(agent)

            rule_engine = RuleEngine()
            rule_engine.load_rules(
                ["hunger", "resource_spawn", "collect", "death"],
                {
                    "hunger": {"decay_rate": 1.0},
                    "resource_spawn": {"spawn_interval": 1, "spawn_prob": 0.1, "amount": 5.0},
                    "collect": {"max_per_tick": 5.0},
                    "death": {"energy_floor": 0.0, "max_age": 500.0},
                },
            )
            engine = TickEngine(world=world, rule_engine=rule_engine, max_ticks=10)
            engine.run()
            return world.population_size()

        pop1 = run_simulation(42)
        pop2 = run_simulation(42)
        assert pop1 == pop2

    def test_collect_actions(self, small_world):
        register_all_rules()
        rule_engine = RuleEngine()
        rule_engine.load_rules(["hunger"], {"hunger": {"decay_rate": 0.1}})
        engine = TickEngine(world=small_world, rule_engine=rule_engine, max_ticks=1)
        actions = engine.collect_actions()
        assert len(actions) == 5  # one per agent

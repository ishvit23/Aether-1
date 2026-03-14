"""Unit tests for combat and trade rules."""

from __future__ import annotations

from aether.agents.agent import Agent
from aether.agents.inventory import add_resource
from aether.rules.combat_rule import CombatRule
from aether.rules.trade_rule import TradeRule
from aether.utils.constants import DEFAULT_STATS
from aether.world.world import World


class TestCombatRule:
    """Tests for CombatRule."""

    def test_combat_between_aggressive_agents(self):
        world = World(width=10, height=10, seed=42)

        traits_a = {
            "strength": 0.8,
            "aggression": 1.0,
            "speed": 0.5,
            "intelligence": 0.5,
            "greed": 0.5,
            "cooperation": 0.1,
        }
        traits_b = {
            "strength": 0.3,
            "aggression": 1.0,
            "speed": 0.5,
            "intelligence": 0.5,
            "greed": 0.5,
            "cooperation": 0.1,
        }

        a = Agent(id=0, x=5, y=5, stats=dict(DEFAULT_STATS), traits=traits_a)
        b = Agent(id=1, x=5, y=5, stats=dict(DEFAULT_STATS), traits=traits_b)
        world.add_agent(a)
        world.add_agent(b)

        rule = CombatRule({"damage_multiplier": 10.0})
        # Run multiple times to ensure combat triggers (probabilistic)
        for tick in range(20):
            rule.apply(world, tick)

        # At least one agent should have taken damage
        assert a.health < 100.0 or b.health < 100.0

    def test_no_combat_single_agent(self):
        world = World(width=10, height=10, seed=42)
        agent = Agent(
            id=0, x=5, y=5, stats=dict(DEFAULT_STATS), traits={"aggression": 1.0, "strength": 0.5}
        )
        world.add_agent(agent)

        rule = CombatRule({"damage_multiplier": 10.0})
        rule.apply(world, tick=0)

        assert agent.health == 100.0  # no opponent, no damage


class TestTradeRule:
    """Tests for TradeRule."""

    def test_trade_between_cooperative_agents(self):
        world = World(width=10, height=10, seed=42)

        traits = {
            "cooperation": 1.0,
            "speed": 0.5,
            "strength": 0.5,
            "intelligence": 0.5,
            "greed": 0.1,
            "aggression": 0.0,
        }
        a = Agent(id=0, x=5, y=5, stats=dict(DEFAULT_STATS), traits=dict(traits))
        b = Agent(id=1, x=5, y=5, stats=dict(DEFAULT_STATS), traits=dict(traits))
        add_resource(a.inventory, "food", 20.0)
        add_resource(b.inventory, "material", 20.0)
        world.add_agent(a)
        world.add_agent(b)

        rule = TradeRule({"offer_threshold": 5.0, "acceptance_prob_base": 1.0})
        rule.apply(world, tick=0)

        # After trade, inventories should have changed
        # A should now have some material, B should have some food
        has_material_a = a.inventory.get("material", 0.0) > 0
        has_food_b = b.inventory.get("food", 0.0) > 0
        assert has_material_a or has_food_b  # at least one direction traded

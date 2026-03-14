"""Unit tests for the resource spawn rule."""

from __future__ import annotations

from aether.rules.resource_rule import ResourceSpawnRule
from aether.world.world import World


class TestResourceSpawnRule:
    """Tests for ResourceSpawnRule."""

    def test_spawns_resources(self):
        world = World(width=10, height=10, seed=42)
        rule = ResourceSpawnRule({"spawn_interval": 1, "spawn_prob": 1.0, "amount": 5.0})
        rule.apply(world, tick=0)

        # With prob=1.0, every cell should have resources
        cells_with_resources = sum(1 for row in world.grid for cell in row if cell.has_resources())
        assert cells_with_resources == 100  # all cells

    def test_respects_interval(self):
        world = World(width=10, height=10, seed=42)
        rule = ResourceSpawnRule({"spawn_interval": 5, "spawn_prob": 1.0, "amount": 5.0})

        # Tick 1 should NOT spawn (not a multiple of 5)
        rule.apply(world, tick=1)
        cells_with_resources = sum(1 for row in world.grid for cell in row if cell.has_resources())
        assert cells_with_resources == 0

    def test_no_spawn_with_zero_prob(self):
        world = World(width=10, height=10, seed=42)
        rule = ResourceSpawnRule({"spawn_interval": 1, "spawn_prob": 0.0, "amount": 5.0})
        rule.apply(world, tick=0)

        cells_with_resources = sum(1 for row in world.grid for cell in row if cell.has_resources())
        assert cells_with_resources == 0

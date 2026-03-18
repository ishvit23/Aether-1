"""Reproduction rule: agents spawn children when energy threshold is met."""

from __future__ import annotations

from aether.agents.agent import Agent
from aether.agents.traits import mutate_traits
from aether.rules.base_rule import Rule
from aether.utils.constants import DEFAULT_STATS
from aether.world.world import World


class ReproductionRule(Rule):
    """Handles agent reproduction when energy conditions are met.

    Config params:
        energy_threshold (float): Min energy to reproduce. Default 80.0.
        child_cost (float): Energy cost to parent. Default 30.0.
    """

    name = "reproduction"

    def apply(self, world: World, tick: int) -> None:
        """Check and execute reproduction for eligible agents.

        Args:
            world: The simulation world.
            tick: Current tick number.
        """
        threshold = self.params.get("energy_threshold", 80.0)
        child_cost = self.params.get("child_cost", 30.0)
        mutation_rate = self.params.get("mutation_rate", 0.05)
        max_delta = self.params.get("max_delta", 0.1)

        new_agents: list[Agent] = []

        for agent in world.living_agents():
            if agent.energy < threshold:
                continue

            # Reproduce
            agent.energy -= child_cost

            child_id = world.next_agent_id()
            child_traits = mutate_traits(
                agent.traits,
                world.rng,
                mutation_rate=mutation_rate,
                max_delta=max_delta,
            )
            child_stats = dict(DEFAULT_STATS)
            child_stats["energy"] = child_cost * 0.8

            # Try to spawn child in a neighbor cell to avoid immediate combat
            neighbors = world.get_neighbors(agent.x, agent.y)
            if neighbors:
                target_cell = world.rng.choice(neighbors)
                cx, cy = target_cell.x, target_cell.y
            else:
                cx, cy = agent.x, agent.y

            child = Agent(
                id=child_id,
                x=cx,
                y=cy,
                traits=child_traits,
                stats=child_stats,
            )
            new_agents.append(child)

            if self.logger:
                self.logger.log_event(
                    tick,
                    "birth",
                    {"parent_id": agent.id, "child_id": child_id, "x": cx, "y": cy},
                )

        for child in new_agents:
            world.add_agent(child)

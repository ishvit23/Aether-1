"""Trade rule: facilitates bilateral resource exchange between neighbours."""

from __future__ import annotations

from aether.agents.inventory import add_resource, has_resource, remove_resource
from aether.rules.base_rule import Rule
from aether.world.world import World


class TradeRule(Rule):
    """Facilitates trades between neighbouring agents when mutually beneficial.

    Config params:
        offer_threshold (float): Min resource amount to consider offering. Default 5.0.
        acceptance_prob_base (float): Base probability of trade acceptance. Default 0.5.
    """

    name = "trade"

    def apply(self, world: World, tick: int) -> None:
        """Check for and execute trades between neighbouring agents.

        Args:
            world: The simulation world.
            tick: Current tick number.
        """
        offer_threshold = self.params.get("offer_threshold", 5.0)
        acceptance_base = self.params.get("acceptance_prob_base", 0.5)

        # Find cells with multiple agents for potential trades
        for row in world.grid:
            for cell in row:
                if len(cell.agents) < 2:
                    continue

                agent_ids = list(cell.agents)
                for i, aid_a in enumerate(agent_ids):
                    for aid_b in agent_ids[i + 1 :]:
                        a = world.agents.get(aid_a)
                        b = world.agents.get(aid_b)
                        if a is None or b is None:
                            continue
                        if not a.is_alive() or not b.is_alive():
                            continue

                        coop_a = a.traits.get("cooperation", 0.5)
                        coop_b = b.traits.get("cooperation", 0.5)
                        trade_prob = acceptance_base * (coop_a + coop_b) / 2.0

                        if world.rng.random() > trade_prob:
                            continue

                        # Find resources A has that B wants, and vice versa
                        for res_a in list(a.inventory.keys()):
                            if not has_resource(a.inventory, res_a, offer_threshold):
                                continue
                            for res_b in list(b.inventory.keys()):
                                if res_b == res_a:
                                    continue
                                if not has_resource(b.inventory, res_b, 1.0):
                                    continue

                                # Execute swap
                                amount = min(
                                    a.inventory.get(res_a, 0.0) * 0.2,
                                    b.inventory.get(res_b, 0.0) * 0.2,
                                    offer_threshold,
                                )
                                if amount <= 0:
                                    continue

                                removed_a = remove_resource(a.inventory, res_a, amount)
                                removed_b = remove_resource(b.inventory, res_b, amount)
                                add_resource(b.inventory, res_a, removed_a)
                                add_resource(a.inventory, res_b, removed_b)
                                return  # One trade per tick is enough

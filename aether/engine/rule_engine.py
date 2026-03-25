"""Rule engine: loads, registers, and executes rules in configured order."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from aether.rules.base_rule import Rule
from aether.world.world import World

if TYPE_CHECKING:
    from aether.utils.logger import EventLogger


class RuleEngine:
    """Manages rule registration and ordered execution.

    Rules are registered by name and instantiated with their config params.
    The engine executes rules in the order specified by config.rules_order.

    Attributes:
        rules: Ordered list of instantiated Rule objects.
    """

    # Class-level registry mapping rule names to Rule subclasses
    _registry: dict[str, type[Rule]] = {}

    def __init__(self) -> None:
        self.rules: list[Rule] = []

    @classmethod
    def register(cls, name: str, rule_cls: type[Rule]) -> None:
        """Register a rule class by name.

        Args:
            name: Rule identifier (e.g. 'hunger', 'movement').
            rule_cls: The Rule subclass to register.
        """
        cls._registry[name] = rule_cls

    @classmethod
    def get_registered(cls) -> dict[str, type[Rule]]:
        """Return a copy of the rule registry."""
        return dict(cls._registry)

    def load_rules(
        self,
        rules_order: list[str],
        rule_params: dict[str, dict[str, Any]],
        logger: EventLogger | None = None,
    ) -> None:
        """Instantiate rules in the specified order with config params.

        Args:
            rules_order: List of rule names in execution order.
            rule_params: Mapping of rule name to parameter dict.

        Raises:
            KeyError: If a rule name is not found in the registry.
        """
        self.rules = []
        for name in rules_order:
            if name not in self._registry:
                raise KeyError(
                    f"Rule '{name}' not found in registry. Available: {list(self._registry.keys())}"
                )
            params = rule_params.get(name, {})
            rule_instance = self._registry[name](params, logger=logger)
            self.rules.append(rule_instance)

    def apply_all(self, world: World, tick: int) -> None:
        """Execute all loaded rules in order.

        Args:
            world: The world to apply rules to.
            tick: Current simulation tick.
        """
        for rule in self.rules:
            rule.apply(world, tick)


def register_all_rules() -> None:
    """Register all built-in rules with the RuleEngine."""
    from aether.rules.animal_rule import AnimalRule
    from aether.rules.build_rule import BuildRule
    from aether.rules.collect_rule import CollectRule
    from aether.rules.combat_rule import CombatRule
    from aether.rules.death_rule import DeathRule
    from aether.rules.decay_rule import DecayRule
    from aether.rules.faction_rule import FactionRule
    from aether.rules.hunger_rule import HungerRule
    from aether.rules.movement_rule import MovementRule
    from aether.rules.mutation_rule import MutationRule
    from aether.rules.resource_rule import ResourceSpawnRule
    from aether.rules.trade_rule import TradeRule
    from aether.rules.weather_rule import WeatherRule

    RuleEngine.register("animal", AnimalRule)
    RuleEngine.register("decay", DecayRule)
    RuleEngine.register("hunger", HungerRule)
    RuleEngine.register("movement", MovementRule)
    RuleEngine.register("resource_spawn", ResourceSpawnRule)
    RuleEngine.register("weather", WeatherRule)
    RuleEngine.register("build", BuildRule)
    RuleEngine.register("collect", CollectRule)
    RuleEngine.register("combat", CombatRule)
    RuleEngine.register("trade", TradeRule)
    RuleEngine.register("faction", FactionRule)
    RuleEngine.register("mutation", MutationRule)
    RuleEngine.register("death", DeathRule)

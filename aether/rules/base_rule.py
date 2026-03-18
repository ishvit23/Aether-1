"""Base Rule abstract class for the Aether-1 rule engine."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from aether.world.world import World

if TYPE_CHECKING:
    from aether.utils.logger import EventLogger


class Rule(ABC):
    """Abstract base class for all simulation rules.

    Rules are modular, independent modules that implement apply().
    Each rule receives its parameters from the config at init time.

    Attributes:
        name: Unique rule identifier string.
        params: Configuration parameters for this rule.
        logger: Optional event logger for rule-specific events.
    """

    name: str
    params: dict[str, Any]
    logger: EventLogger | None

    def __init__(self, params: dict[str, Any], logger: EventLogger | None = None) -> None:
        self.params = params
        self.logger = logger

    @abstractmethod
    def apply(self, world: World, tick: int) -> None:
        """Apply this rule to the world state for the given tick.

        Args:
            world: The world to modify.
            tick: Current simulation tick.
        """
        ...

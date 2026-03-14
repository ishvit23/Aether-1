"""Action types and TypedDict for the Aether-1 action system."""

from __future__ import annotations

from enum import StrEnum
from typing import Any, TypedDict


class ActionType(StrEnum):
    """All possible action types an agent can take."""

    MOVE = "move"
    COLLECT = "collect"
    EAT = "eat"
    ATTACK = "attack"
    TRADE = "trade"
    REPRODUCE = "reproduce"
    IDLE = "idle"


class Action(TypedDict):
    """A single action produced by an agent's decide() function.

    The engine validates and executes actions — agents never
    directly mutate the world.

    Keys:
        type: The ActionType string.
        actor_id: ID of the agent taking the action.
        target: Target agent ID, coordinate tuple, or None.
        payload: Additional action-specific data.
    """

    type: ActionType
    actor_id: int
    target: int | tuple[int, int] | None
    payload: dict[str, Any]

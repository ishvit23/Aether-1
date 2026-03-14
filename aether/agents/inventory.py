"""Inventory helper functions for agents."""

from __future__ import annotations


def add_resource(inventory: dict[str, float], name: str, amount: float) -> None:
    """Add a resource amount to an inventory.

    Args:
        inventory: Agent inventory dict (resource_name -> amount).
        name: Resource name.
        amount: Amount to add.
    """
    inventory[name] = inventory.get(name, 0.0) + amount


def remove_resource(inventory: dict[str, float], name: str, amount: float) -> float:
    """Remove up to *amount* of a resource from inventory.

    Args:
        inventory: Agent inventory dict.
        name: Resource name.
        amount: Maximum quantity to remove.

    Returns:
        The actual amount removed.
    """
    available = inventory.get(name, 0.0)
    removed = min(available, amount)
    inventory[name] = available - removed
    if inventory[name] <= 0:
        inventory.pop(name, None)
    return removed


def has_resource(inventory: dict[str, float], name: str, min_amount: float = 0.01) -> bool:
    """Check if an inventory has at least min_amount of a resource.

    Args:
        inventory: Agent inventory dict.
        name: Resource name.
        min_amount: Minimum threshold to consider 'having' the resource.

    Returns:
        True if the resource exists above the threshold.
    """
    return inventory.get(name, 0.0) >= min_amount


def total_resources(inventory: dict[str, float]) -> float:
    """Sum of all resource amounts in inventory.

    Args:
        inventory: Agent inventory dict.

    Returns:
        Total quantity across all resource types.
    """
    return sum(inventory.values())

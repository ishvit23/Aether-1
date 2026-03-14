"""Resource model and type registry for Aether-1."""

from __future__ import annotations

from dataclasses import dataclass

# Default resource types available in V1
DEFAULT_RESOURCE_TYPES: list[str] = ["food", "material"]


@dataclass
class Resource:
    """A generic resource instance.

    Attributes:
        name: Resource type identifier (e.g. 'food', 'material').
        amount: Quantity of this resource.
    """

    name: str
    amount: float

    def deplete(self, quantity: float) -> float:
        """Remove up to *quantity* from this resource.

        Args:
            quantity: Maximum amount to remove.

        Returns:
            Actual amount removed.
        """
        removed = min(self.amount, quantity)
        self.amount -= removed
        return removed

    def replenish(self, quantity: float) -> None:
        """Add quantity to this resource.

        Args:
            quantity: Amount to add.
        """
        self.amount += quantity

    @property
    def is_depleted(self) -> bool:
        """Check if the resource is fully depleted."""
        return self.amount <= 0.0

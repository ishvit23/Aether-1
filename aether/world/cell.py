"""Cell model for the Aether-1 world grid."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class StructureData:
    """Represents a structure placed on a cell.

    Attributes:
        kind: Structure type — 'wall' or 'nest'.
        health: Durability points. Structure is destroyed when <= 0.
        faction_id: The faction that owns this structure (None = neutral).
    """

    kind: str  # "wall" | "nest"
    health: float = 100.0
    faction_id: str | None = None

    def is_destroyed(self) -> bool:
        """Return True if this structure has been fully damaged."""
        return self.health <= 0.0


@dataclass
class Cell:
    """A single cell in the world grid.

    Attributes:
        x: Column position.
        y: Row position.
        resources: Mapping of resource name to amount present in this cell.
        agents: List of agent IDs currently occupying this cell.
        terrain: Optional terrain type string (future use).
    """

    x: int
    y: int
    resources: dict[str, float] = field(default_factory=dict)
    agents: list[int] = field(default_factory=list)
    terrain: str | None = None
    structure: StructureData | None = None

    @property
    def structure_kind(self) -> str | None:
        """Convenience accessor for the structure type string."""
        return self.structure.kind if self.structure else None

    def add_resource(self, name: str, amount: float) -> None:
        """Add a quantity of a resource to this cell.

        Args:
            name: Resource name (e.g. 'food', 'material').
            amount: Quantity to add (must be >= 0).
        """
        self.resources[name] = self.resources.get(name, 0.0) + amount

    def remove_resource(self, name: str, amount: float) -> float:
        """Remove up to *amount* of a resource from this cell.

        Args:
            name: Resource name.
            amount: Maximum quantity to remove.

        Returns:
            The actual amount removed (may be less than requested).
        """
        available = self.resources.get(name, 0.0)
        removed = min(available, amount)
        self.resources[name] = available - removed
        if self.resources[name] <= 0.0:
            self.resources.pop(name, None)
        return removed

    def add_agent(self, agent_id: int) -> None:
        """Register an agent as present in this cell.

        Args:
            agent_id: ID of the agent entering the cell.
        """
        if agent_id not in self.agents:
            self.agents.append(agent_id)

    def remove_agent(self, agent_id: int) -> None:
        """Remove an agent from this cell.

        Args:
            agent_id: ID of the agent leaving the cell.
        """
        if agent_id in self.agents:
            self.agents.remove(agent_id)

    def has_resources(self) -> bool:
        """Check if this cell has any resources."""
        return bool(self.resources)

    def agent_count(self) -> int:
        """Return number of agents in this cell."""
        return len(self.agents)

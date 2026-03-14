"""World model: 2D grid of cells with torus wrapping support."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from aether.world.cell import Cell

if TYPE_CHECKING:
    from aether.agents.agent import Agent


class World:
    """2D grid world that contains cells, agents, and resources.

    The grid supports configurable wrap-around (torus) boundaries.
    All cell access must go through get_cell() which handles wrapping.

    Attributes:
        width: Number of columns.
        height: Number of rows.
        wrap: If True, coordinates wrap around (torus topology).
        tick: Current simulation tick.
        agents: Mapping of agent_id to Agent instance.
        rng: Seeded random.Random for deterministic behaviour.
    """

    def __init__(
        self,
        width: int,
        height: int,
        wrap: bool = True,
        seed: int | None = None,
    ) -> None:
        self.width = width
        self.height = height
        self.wrap = wrap
        self.tick: int = 0
        self.agents: dict[int, Agent] = {}
        self.rng: random.Random = random.Random(seed)
        self._next_agent_id: int = 0

        # Build grid
        self.grid: list[list[Cell]] = [
            [Cell(x=x, y=y) for x in range(width)] for y in range(height)
        ]

    def get_cell(self, x: int, y: int) -> Cell:
        """Get a cell by coordinates, applying wrapping if enabled.

        Args:
            x: Column coordinate.
            y: Row coordinate.

        Returns:
            The Cell at the (possibly wrapped) coordinates.

        Raises:
            IndexError: If wrapping is disabled and coordinates are out of bounds.
        """
        if self.wrap:
            x = x % self.width
            y = y % self.height
        elif not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError(
                f"Coordinates ({x}, {y}) out of bounds for {self.width}x{self.height} grid"
            )
        return self.grid[y][x]

    def get_neighbors(self, x: int, y: int, radius: int = 1) -> list[Cell]:
        """Get all cells within a given radius (excluding the center cell).

        Args:
            x: Center column.
            y: Center row.
            radius: Manhattan distance radius (default 1 for immediate neighbors).

        Returns:
            List of neighboring Cell objects.
        """
        neighbors: list[Cell] = []
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if self.wrap:
                    nx = nx % self.width
                    ny = ny % self.height
                    neighbors.append(self.grid[ny][nx])
                elif 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbors.append(self.grid[ny][nx])
        return neighbors

    def next_agent_id(self) -> int:
        """Generate the next unique agent ID.

        Returns:
            An integer ID that has not been used before.
        """
        aid = self._next_agent_id
        self._next_agent_id += 1
        return aid

    def add_agent(self, agent: Agent) -> None:
        """Add an agent to the world and register it in its cell.

        Args:
            agent: Agent instance to add.
        """
        self.agents[agent.id] = agent
        self.get_cell(agent.x, agent.y).add_agent(agent.id)
        if agent.id >= self._next_agent_id:
            self._next_agent_id = agent.id + 1

    def remove_agent(self, agent_id: int) -> Agent | None:
        """Remove an agent from the world and its cell.

        Args:
            agent_id: ID of the agent to remove.

        Returns:
            The removed Agent, or None if not found.
        """
        agent = self.agents.pop(agent_id, None)
        if agent is not None:
            self.get_cell(agent.x, agent.y).remove_agent(agent_id)
        return agent

    def move_agent(self, agent_id: int, new_x: int, new_y: int) -> None:
        """Move an agent to a new position, updating cell registrations.

        Args:
            agent_id: ID of the agent to move.
            new_x: Target column.
            new_y: Target row.
        """
        agent = self.agents.get(agent_id)
        if agent is None:
            return
        # Remove from old cell
        self.get_cell(agent.x, agent.y).remove_agent(agent_id)
        # Apply wrapping
        if self.wrap:
            new_x = new_x % self.width
            new_y = new_y % self.height
        agent.x = new_x
        agent.y = new_y
        # Add to new cell
        self.get_cell(new_x, new_y).add_agent(agent_id)

    def living_agents(self) -> list[Agent]:
        """Return a list of all living agents, sorted by ID.

        Returns:
            Sorted list of Agent instances.
        """
        return sorted(self.agents.values(), key=lambda a: a.id)

    def population_size(self) -> int:
        """Return the current number of agents."""
        return len(self.agents)

    def post_tick_cleanup(self, tick: int) -> None:
        """Perform post-tick housekeeping.

        Args:
            tick: The tick number that just completed.
        """
        self.tick = tick + 1
        # Clean up cells with zero resources
        for row in self.grid:
            for cell in row:
                empty_resources = [k for k, v in cell.resources.items() if v <= 0.0]
                for k in empty_resources:
                    del cell.resources[k]

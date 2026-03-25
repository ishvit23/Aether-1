"""WebSocket custom renderer for serializing World state."""

from __future__ import annotations

from typing import Any

from aether.world.world import World


class WSRenderer:
    """Extracts exactly what the React client needs to draw the grid and charts."""

    def __init__(self, world: World):
        self.world = world

    def render_full_state(self) -> dict[str, Any]:
        """Returns the complete static grid and dynamic agents."""
        cells = []
        # Pre-pack static cells and resources
        for y in range(self.world.height):
            for x in range(self.world.width):
                cell = self.world.get_cell(x, y)
                if cell.structure or cell.resources:
                    struct_val = None
                    if cell.structure:
                        if hasattr(cell.structure, "kind"):
                            struct_val = {
                                "kind": cell.structure.kind,
                                "health": cell.structure.health,
                            }
                        else:
                            struct_val = {"kind": str(cell.structure), "health": 100.0}

                    cells.append(
                        {
                            "x": x,
                            "y": y,
                            "structure": struct_val,
                            "resources": dict(cell.resources),
                        }
                    )

        agents = []
        for agent in self.world.living_agents():
            agents.append(self._serialize_agent(agent))

        animals = []
        for animal in self.world.living_animals():
            animals.append(
                {
                    "id": animal.id,
                    "kind": animal.kind,
                    "x": animal.x,
                    "y": animal.y,
                    "health": animal.health,
                }
            )

        # Basic distribution for pie charts
        factions: dict[str, int] = {}
        for a in self.world.living_agents():
            fid = a.faction_id or "None"
            factions[fid] = factions.get(fid, 0) + 1

        return {
            "tick": self.world.tick,
            "weather": getattr(self.world, "weather_state", "Spring"),
            "population": self.world.population_size(),
            "grid": {"width": self.world.width, "height": self.world.height},
            "cells": cells,
            "agents": agents,
            "animals": animals,
            "factions": factions,
        }

    def render_diff_state(self) -> dict[str, Any]:
        """In a real app this might be a diff, but for simplicity we send a lighter full state."""
        return self.render_full_state()

    def _serialize_agent(self, agent: Any) -> dict[str, Any]:
        """Convert agent to simple Dict."""
        return {
            "id": agent.id,
            "x": agent.x,
            "y": agent.y,
            "faction": agent.faction_id,
            "energy": agent.energy,
            "health": agent.health,
            "state": agent.state,
        }

"""Pygame visualization for the Aether-1 simulation.

Renders the world grid, resources, and agents in a graphical window.
Toggle with --viz pygame at the CLI.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aether.world.world import World

# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------
CELL_SIZE: int = 14  # pixels per cell
SIDEBAR_W: int = 260  # width of the stats panel on the right
FPS_CAP: int = 60  # max frames per second for event polling

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------
BG_COLOUR = (18, 18, 28)  # deep dark background
GRID_LINE = (30, 30, 46)  # subtle grid lines
EMPTY_CELL = (22, 22, 34)  # empty cell fill

FOOD_COLOUR = (52, 168, 83)  # green  – food resource
MATERIAL_COLOUR = (251, 188, 5)  # amber  – material resource
MULTI_COLOUR = (66, 133, 244)  # blue   – cell with multiple resource types

SIDEBAR_BG = (14, 14, 22)
SIDEBAR_BORDER = (60, 60, 90)
TEXT_COLOUR = (220, 220, 240)
TITLE_COLOUR = (160, 140, 255)
ACCENT_COLOUR = (100, 220, 180)

# Agent dot colours keyed by state
STATE_COLOURS: dict[str, tuple[int, int, int]] = {
    "idle": (130, 130, 200),
    "moving": (80, 200, 255),
    "eating": (80, 255, 130),
    "attacking": (255, 80, 80),
    "trading": (255, 220, 60),
    "reproducing": (255, 130, 230),
    "fleeing": (255, 150, 50),
}
DEFAULT_AGENT_COLOUR = (180, 180, 220)

# ---------------------------------------------------------------------------
# Module-level pygame state (lazy-initialised on first call)
# ---------------------------------------------------------------------------
_pygame_ready: bool = False
_screen = None  # pygame.Surface
_font_small = None  # pygame.font.Font
_font_normal = None  # pygame.font.Font
_font_title = None  # pygame.font.Font
_clock = None  # pygame.time.Clock


def _init_pygame(world_width: int, world_height: int) -> None:
    """Initialise pygame window and fonts (called once).

    Args:
        world_width: Number of grid columns.
        world_height: Number of grid rows.
    """
    global _pygame_ready, _screen, _font_small, _font_normal, _font_title, _clock

    import pygame  # noqa: PLC0415

    pygame.init()
    pygame.display.set_caption("Aether-1 Simulation")

    win_w = world_width * CELL_SIZE + SIDEBAR_W
    win_h = world_height * CELL_SIZE

    _screen = pygame.display.set_mode((win_w, win_h))
    _font_small = pygame.font.SysFont("monospace", 11)
    _font_normal = pygame.font.SysFont("monospace", 13, bold=False)
    _font_title = pygame.font.SysFont("monospace", 15, bold=True)
    _clock = pygame.time.Clock()
    _pygame_ready = True


def _resource_colour(cell_resources: dict[str, float]) -> tuple[int, int, int] | None:
    """Return the fill colour for a cell based on its resources.

    Returns None if the cell has no resources.
    """
    has_food = cell_resources.get("food", 0.0) > 0
    has_material = cell_resources.get("material", 0.0) > 0
    has_other = any(k not in ("food", "material") for k in cell_resources if cell_resources[k] > 0)

    count = sum([has_food, has_material, has_other])
    if count == 0:
        return None
    if count > 1:
        return MULTI_COLOUR
    if has_food:
        return FOOD_COLOUR
    if has_material:
        return MATERIAL_COLOUR
    return ACCENT_COLOUR  # other single resource


def _draw_grid(world: World) -> None:
    """Draw all grid cells with resource tinting."""
    import pygame  # noqa: PLC0415

    assert _screen is not None

    for y in range(world.height):
        for x in range(world.width):
            cell = world.get_cell(x, y)
            rx = x * CELL_SIZE
            ry = y * CELL_SIZE
            rect = pygame.Rect(rx, ry, CELL_SIZE - 1, CELL_SIZE - 1)

            res_col = _resource_colour(cell.resources)
            if res_col is not None:
                # Blend resource colour into background for gentle tint
                dominant = cell.resources.get("food") or cell.resources.get("material") or 1.0
                intensity = min(dominant / 10.0, 1.0)  # normalise; cap at 1
                r = int(EMPTY_CELL[0] + (res_col[0] - EMPTY_CELL[0]) * intensity * 0.7)
                g = int(EMPTY_CELL[1] + (res_col[1] - EMPTY_CELL[1]) * intensity * 0.7)
                b = int(EMPTY_CELL[2] + (res_col[2] - EMPTY_CELL[2]) * intensity * 0.7)
                fill = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
            else:
                fill = EMPTY_CELL

            _screen.fill(fill, rect)


def _draw_agents(world: World) -> None:
    """Draw each agent as a circle scaled by their health."""
    import pygame  # noqa: PLC0415

    assert _screen is not None

    for agent in world.living_agents():
        cx = agent.x * CELL_SIZE + CELL_SIZE // 2
        cy = agent.y * CELL_SIZE + CELL_SIZE // 2

        colour = STATE_COLOURS.get(agent.state, DEFAULT_AGENT_COLOUR)

        # Radius: 2–5px depending on health proportion
        max_health = 100.0
        health_ratio = max(0.0, min(1.0, agent.health / max_health))
        radius = max(2, int(2 + health_ratio * 3))

        pygame.draw.circle(_screen, colour, (cx, cy), radius)

        # Aggression ring: bright red outline when aggression > 0.7
        aggression = agent.traits.get("aggression", 0.0)
        if aggression > 0.7:
            pygame.draw.circle(_screen, (255, 60, 60), (cx, cy), radius + 1, 1)


def _draw_sidebar(world: World, tick: int) -> None:
    """Render the right-hand stats panel."""
    import pygame  # noqa: PLC0415

    assert _screen is not None
    assert _font_small is not None
    assert _font_normal is not None
    assert _font_title is not None

    sidebar_x = world.width * CELL_SIZE
    win_h = world.height * CELL_SIZE
    sidebar_rect = pygame.Rect(sidebar_x, 0, SIDEBAR_W, win_h)
    _screen.fill(SIDEBAR_BG, sidebar_rect)

    # Border line
    pygame.draw.line(_screen, SIDEBAR_BORDER, (sidebar_x, 0), (sidebar_x, win_h), 2)

    agents = world.living_agents()
    pop = len(agents)

    def _avg(attr: str) -> float:
        if not agents:
            return 0.0
        return sum(getattr(a, attr, 0.0) for a in agents) / pop

    def _avg_trait(t: str) -> float:
        if not agents:
            return 0.0
        return sum(a.traits.get(t, 0.0) for a in agents) / pop

    lines: list[tuple[str, str, tuple[int, int, int]]] = [
        ("AETHER-1", "", TITLE_COLOUR),
        (f"Tick: {tick}", "", ACCENT_COLOUR),
        ("", "", TEXT_COLOUR),
        ("── World ──────────", "", SIDEBAR_BORDER),
        (f"  Size:       {world.width}×{world.height}", "", TEXT_COLOUR),
        (f"  Population: {pop}", "", TEXT_COLOUR),
        ("", "", TEXT_COLOUR),
        ("── Vitals ─────────", "", SIDEBAR_BORDER),
        (f"  Energy:     {_avg('energy'):6.1f}", "", TEXT_COLOUR),
        (f"  Health:     {_avg('health'):6.1f}", "", TEXT_COLOUR),
        (f"  Hunger:     {_avg('hunger'):6.1f}", "", TEXT_COLOUR),
        (f"  Age:        {_avg('age'):6.1f}", "", TEXT_COLOUR),
        ("", "", TEXT_COLOUR),
        ("── Traits ─────────", "", SIDEBAR_BORDER),
        (f"  Strength:   {_avg_trait('strength'):5.3f}", "", TEXT_COLOUR),
        (f"  Speed:      {_avg_trait('speed'):5.3f}", "", TEXT_COLOUR),
        (f"  Aggression: {_avg_trait('aggression'):5.3f}", "", TEXT_COLOUR),
        (f"  Cooperat'n: {_avg_trait('cooperation'):5.3f}", "", TEXT_COLOUR),
        (f"  Intellig':  {_avg_trait('intelligence'):5.3f}", "", TEXT_COLOUR),
        (f"  Greed:      {_avg_trait('greed'):5.3f}", "", TEXT_COLOUR),
        ("", "", TEXT_COLOUR),
        ("── Legend ─────────", "", SIDEBAR_BORDER),
        ("  ● idle/moving", "", STATE_COLOURS["moving"]),
        ("  ● eating", "", STATE_COLOURS["eating"]),
        ("  ● attacking", "", STATE_COLOURS["attacking"]),
        ("  ● trading", "", STATE_COLOURS["trading"]),
        ("  ● reproducing", "", STATE_COLOURS["reproducing"]),
        ("", "", TEXT_COLOUR),
        ("── Resources ──────", "", SIDEBAR_BORDER),
        ("  █ food", "", FOOD_COLOUR),
        ("  █ material", "", MATERIAL_COLOUR),
        ("  █ mixed", "", MULTI_COLOUR),
        ("", "", TEXT_COLOUR),
        ("[ESC / Q] quit", "", (100, 100, 120)),
    ]

    y_offset = 10
    for text, _unused, colour in lines:
        if text == "":
            y_offset += 6
            continue
        surf = _font_normal.render(text, True, colour)
        _screen.blit(surf, (sidebar_x + 8, y_offset))
        y_offset += 17


def render_pygame(world: World, tick: int) -> None:
    """Render the world using Pygame. Initialises the window on first call.

    This function is called by the TickEngine at regular intervals when
    ``--viz pygame`` is selected. It also processes Pygame events, so the
    window remains responsive and can be closed gracefully.

    Args:
        world: The current simulation world.
        tick: Current tick number.
    """
    import pygame  # noqa: PLC0415

    global _pygame_ready

    if not _pygame_ready:
        _init_pygame(world.width, world.height)

    # --- Event handling ---------------------------------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_q):
            pygame.quit()
            sys.exit(0)

    # --- Draw -------------------------------------------------------------
    assert _screen is not None
    assert _clock is not None

    _screen.fill(BG_COLOUR)
    _draw_grid(world)
    _draw_agents(world)
    _draw_sidebar(world, tick)

    pygame.display.flip()
    _clock.tick(FPS_CAP)

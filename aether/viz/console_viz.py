"""Console visualization using rich for the Aether-1 simulation."""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from aether.world.world import World

console = Console()


def render_console(world: World, tick: int, grid_sample_size: int = 20) -> None:
    """Render the world state to the console using rich.

    Displays a sampled grid view and a stats summary panel.

    Args:
        world: The simulation world to render.
        tick: Current tick number.
        grid_sample_size: Size of the grid sample to display (default 20x20).
    """
    # Determine sample bounds (center of grid)
    sample_w = min(grid_sample_size, world.width)
    sample_h = min(grid_sample_size, world.height)
    start_x = max(0, (world.width - sample_w) // 2)
    start_y = max(0, (world.height - sample_h) // 2)

    # Build grid text
    grid_text = Text()
    for y in range(start_y, start_y + sample_h):
        for x in range(start_x, start_x + sample_w):
            cell = world.get_cell(x, y)
            if cell.agents:
                grid_text.append("@", style="bold cyan")
            elif cell.resources.get("food", 0) > 0:
                grid_text.append("F", style="green")
            elif cell.resources.get("material", 0) > 0:
                grid_text.append("M", style="yellow")
            elif cell.has_resources():
                grid_text.append("·", style="dim blue")
            else:
                grid_text.append(".", style="dim")
        grid_text.append("\n")

    # Build stats table
    agents = world.living_agents()
    pop = len(agents)
    avg_energy = sum(a.energy for a in agents) / max(pop, 1)
    avg_health = sum(a.health for a in agents) / max(pop, 1)
    avg_hunger = sum(a.hunger for a in agents) / max(pop, 1)
    avg_strength = sum(a.traits.get("strength", 0.0) for a in agents) / max(pop, 1)
    avg_aggr = sum(a.traits.get("aggression", 0.0) for a in agents) / max(pop, 1)
    avg_coop = sum(a.traits.get("cooperation", 0.0) for a in agents) / max(pop, 1)

    stats_table = Table(title=f"Tick {tick}", show_header=True, header_style="bold magenta")
    stats_table.add_column("Metric", style="cyan", width=16)
    stats_table.add_column("Value", justify="right", style="white", width=10)
    stats_table.add_row("Population", str(pop))
    stats_table.add_row("Avg Energy", f"{avg_energy:.1f}")
    stats_table.add_row("Avg Health", f"{avg_health:.1f}")
    stats_table.add_row("Avg Hunger", f"{avg_hunger:.1f}")
    stats_table.add_row("Avg Strength", f"{avg_strength:.3f}")
    stats_table.add_row("Avg Aggression", f"{avg_aggr:.3f}")
    stats_table.add_row("Avg Cooperation", f"{avg_coop:.3f}")

    # Legend
    legend = Text()
    legend.append("Legend: ", style="bold")
    legend.append("@", style="bold cyan")
    legend.append("=Agent  ", style="dim")
    legend.append("F", style="green")
    legend.append("=Food  ", style="dim")
    legend.append("M", style="yellow")
    legend.append("=Material  ", style="dim")
    legend.append(".", style="dim")
    legend.append("=Empty", style="dim")

    # Clear and print
    console.clear()
    console.print(
        Panel(grid_text, title=f"World ({world.width}×{world.height})", border_style="blue")
    )
    console.print(stats_table)
    console.print(legend)


def replay_log(log_path: str) -> None:
    """Read a JSONL event log and display events tick-by-tick.

    Args:
        log_path: Path to the JSONL log file.
    """
    import json
    from collections import defaultdict

    events_by_tick: dict[int, list[dict[str, Any]]] = defaultdict(list)
    max_tick = 0

    try:
        with open(log_path, encoding="utf-8") as f:
            for line in f:
                event = json.loads(line)
                tick = event["tick"]
                events_by_tick[tick].append(event)
                max_tick = max(max_tick, tick)
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/] Log file not found: {log_path}")
        return

    console.clear()
    console.print(Panel(f"REPLAY MODE: {log_path}", style="bold magenta"))

    for tick in range(max_tick + 1):
        tick_events = events_by_tick.get(tick, [])
        if not tick_events:
            continue

        table = Table(title=f"Events for Tick {tick}", show_header=True, header_style="bold green")
        table.add_column("Type", style="cyan")
        table.add_column("Details", style="white")

        for ev in tick_events:
            event_type = ev["event"]
            payload = ev["payload"]
            details = ", ".join(f"{k}={v}" for k, v in payload.items())
            table.add_row(event_type, details)

        console.print(table)
        input("\nPress Enter for next tick (Ctrl+C to exit)...")
        console.clear()

    console.print("[bold green]Replay finished.[/]")

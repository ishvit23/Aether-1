"""Aether-1 CLI entry point using click."""

from __future__ import annotations

import click


@click.group()
def cli() -> None:
    """Aether-1: Configurable Multi-Agent Simulation Engine."""


@cli.command()
@click.option(
    "--config", default="config/world_v1.json", help="Path to config file (JSON or YAML)."
)
@click.option("--seed", default=None, type=int, help="RNG seed override.")
@click.option("--ticks", default=None, type=int, help="Max ticks override.")
@click.option(
    "--viz",
    default="none",
    type=click.Choice(["none", "console", "pygame"]),
    help="Visualization mode.",
)
@click.option(
    "--policy", default=None, help="Path to pre-trained JSON policy to inject."
)
def run(config: str, seed: int | None, ticks: int | None, viz: str, policy: str | None) -> None:
    """Run a simulation with the given config."""
    import json

    from aether.simulation.simulation import Simulation

    loaded_policy = None
    if policy:
        with open(policy) as f:
            loaded_policy = json.load(f)

    sim = Simulation(
        config_path=config, seed=seed, ticks=ticks, viz=viz, policy=loaded_policy
    )
    sim.run()


@cli.command()
@click.option("--log", required=True, help="Path to JSONL event log file.")
def replay(log: str) -> None:
    """Replay a simulation from a JSONL event log."""
    from aether.viz.console_viz import replay_log

    replay_log(log)


@cli.command(name="validate-config")
@click.option("--config", required=True, help="Path to config file to validate.")
def validate_config(config: str) -> None:
    """Validate a config file without running a simulation."""
    from aether.world.world_loader import ConfigValidationError, WorldLoader

    try:
        c = WorldLoader.load(config)
        click.echo(f"✓ Config is valid: {config}")
        click.echo(f"  World: {c['world']['width']}×{c['world']['height']}")
        click.echo(f"  Agents: {c['initial']['agents']}")
        click.echo(f"  Rules: {', '.join(c['rules_order'])}")
        click.echo(f"  Ticks: {c['ticks']}, Seed: {c['seed']}")
    except ConfigValidationError as e:
        click.echo(f"✗ Config validation failed: {e}", err=True)
        raise SystemExit(1) from e
    except FileNotFoundError as e:
        click.echo(f"✗ File not found: {e}", err=True)
        raise SystemExit(1) from e


if __name__ == "__main__":
    cli()

"""Simulation orchestrator: ties together world, engine, logging, and visualization."""

from __future__ import annotations

import logging
from typing import Any

from aether.engine.rule_engine import RuleEngine, register_all_rules
from aether.engine.tick_engine import TickEngine
from aether.utils.logger import (
    EventLogger,
    MetricsWriter,
    setup_console_logging,
    write_run_metadata,
)
from aether.viz.console_viz import render_console
from aether.world.world_loader import WorldLoader

logger = logging.getLogger("aether.simulation")


class Simulation:
    """Top-level simulation orchestrator.

    Loads config, builds world, sets up engine, logging, and viz,
    then runs the simulation.

    Args:
        config_path: Path to the config file (JSON or YAML).
        seed: RNG seed override (overrides config seed if provided).
        ticks: Max ticks override (overrides config ticks if provided).
        viz: Visualization mode ('none', 'console', 'pygame').
    """

    def __init__(
        self,
        config_path: str,
        seed: int | None = None,
        ticks: int | None = None,
        viz: str = "none",
        metrics_dir: str | None = "default",
        policy: dict[str, dict[str, float]] | None = None,
    ) -> None:
        setup_console_logging()

        # Load and parse config
        self.config: dict[str, Any] = WorldLoader.load(config_path)
        self.config_path = config_path

        # Apply overrides
        if seed is not None:
            self.config["seed"] = seed
        if ticks is not None:
            self.config["ticks"] = ticks

        actual_seed = self.config.get("seed", 42)
        actual_ticks = self.config.get("ticks", 1000)

        # Build world
        self.world = WorldLoader.build_world(self.config)

        # Inject policy
        if policy is not None:
            import copy

            for agent in self.world.agents.values():
                agent.q_table = copy.deepcopy(policy)

        # Set up logging
        self.event_logger: EventLogger | None = None
        self.metrics_writer: MetricsWriter | None = None

        if metrics_dir is not None:
            self.event_logger = EventLogger()
            self.metrics_writer = MetricsWriter()
            actual_seed = self.config.get("seed", 42)
            write_run_metadata(actual_seed, config_path)

        # Set up rules
        register_all_rules()
        self.rule_engine = RuleEngine()
        rule_params = WorldLoader.get_rule_params(self.config)
        self.rule_engine.load_rules(
            self.config["rules_order"], rule_params, logger=self.event_logger
        )

        # Build tick engine
        self.engine = TickEngine(
            world=self.world,
            rule_engine=self.rule_engine,
            max_ticks=actual_ticks,
            event_logger=self.event_logger,
            metrics_writer=self.metrics_writer,
        )

        # Visualization
        self.viz = viz

    def run(self) -> None:
        """Execute the full simulation."""
        render_cb: Any | None = None
        if self.viz == "console":
            render_cb = render_console
        elif self.viz == "pygame":
            from aether.viz.pygame_viz import render_pygame

            render_cb = render_pygame

        try:
            self.engine.run(render_callback=render_cb, render_interval=10)
        finally:
            if self.event_logger is not None:
                self.event_logger.close()
                logger.info("Event log: %s", self.event_logger.log_path)
            if self.metrics_writer is not None:
                self.metrics_writer.close()
                logger.info("Metrics CSV: %s", self.metrics_writer.csv_path)

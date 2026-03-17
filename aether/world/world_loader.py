"""World loader: parse config files and construct a fully initialised World."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from aether.agents.agent import Agent
from aether.agents.traits import generate_traits
from aether.utils.constants import DEFAULT_RULE_PARAMS, DEFAULT_STATS
from aether.world.world import World


class ConfigValidationError(Exception):
    """Raised when a config file is missing required keys or has invalid values."""


def _validate_config(config: dict[str, Any]) -> None:
    """Validate that a config dict has all required keys.

    Args:
        config: Parsed config dictionary.

    Raises:
        ConfigValidationError: On missing or invalid keys.
    """
    required_top = ["world", "initial", "rules_order", "ticks", "seed"]
    for key in required_top:
        if key not in config:
            raise ConfigValidationError(f"Missing required top-level config key: '{key}'")

    world_cfg = config["world"]
    for key in ["width", "height"]:
        if key not in world_cfg:
            raise ConfigValidationError(f"Missing required world config key: '{key}'")
        if not isinstance(world_cfg[key], int) or world_cfg[key] <= 0:
            raise ConfigValidationError(
                f"world.{key} must be a positive integer, got: {world_cfg[key]}"
            )

    initial_cfg = config["initial"]
    if "agents" not in initial_cfg:
        raise ConfigValidationError("Missing required initial config key: 'agents'")
    if not isinstance(initial_cfg["agents"], int) or initial_cfg["agents"] < 0:
        raise ConfigValidationError(
            f"initial.agents must be a non-negative integer, got: {initial_cfg['agents']}"
        )

    if not isinstance(config["rules_order"], list):
        raise ConfigValidationError("rules_order must be a list of rule name strings")

    if not isinstance(config["ticks"], int) or config["ticks"] <= 0:
        raise ConfigValidationError(f"ticks must be a positive integer, got: {config['ticks']}")


class WorldLoader:
    """Loads a world configuration from JSON or YAML and builds a World instance."""

    @staticmethod
    def load(config_path: str) -> dict[str, Any]:
        """Load and validate a config file, returning the parsed config dict.

        Args:
            config_path: Path to a JSON or YAML config file.

        Returns:
            Validated config dictionary.

        Raises:
            FileNotFoundError: If config file does not exist.
            ConfigValidationError: If config is invalid.
        """
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        raw = path.read_text(encoding="utf-8")

        if path.suffix in (".yaml", ".yml"):
            config: dict[str, Any] = yaml.safe_load(raw)
        else:
            config = json.loads(raw)

        _validate_config(config)
        return config

    @staticmethod
    def build_world(config: dict[str, Any]) -> World:
        """Construct a World from a validated config dict.

        Creates the grid, spawns initial resources, and creates initial agents.

        Args:
            config: Validated config dictionary (from load()).

        Returns:
            A fully initialised World instance.
        """
        world_cfg = config["world"]
        seed = config.get("seed", 42)

        world = World(
            width=world_cfg["width"],
            height=world_cfg["height"],
            wrap=world_cfg.get("wrap", True),
            seed=seed,
        )

        # Spawn initial resources
        initial = config.get("initial", {})
        resource_dist: dict[str, float] = initial.get("resource_distribution", {})
        for y in range(world.height):
            for x in range(world.width):
                for resource_name, probability in resource_dist.items():
                    if world.rng.random() < probability:
                        amount = world.rng.uniform(1.0, 10.0)
                        world.get_cell(x, y).add_resource(resource_name, amount)

        # Spawn initial agents
        agent_count = initial.get("agents", 0)
        agents_config = config.get("agents_config", {})
        for _ in range(agent_count):
            aid = world.next_agent_id()
            x = world.rng.randint(0, world.width - 1)
            y = world.rng.randint(0, world.height - 1)
            traits = generate_traits(world.rng, agents_config)
            stats = dict(DEFAULT_STATS)
            stats["energy"] = world.rng.uniform(50.0, 100.0)
            agent = Agent(id=aid, x=x, y=y, traits=traits, stats=stats)
            world.add_agent(agent)

        return world

    @staticmethod
    def get_rule_params(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
        """Extract per-rule parameters from config, merged with defaults.

        Args:
            config: Validated config dictionary.

        Returns:
            Dict mapping rule name to parameter dict.
        """
        base_params: dict[str, dict[str, Any]] = {
            k: dict(v) for k, v in DEFAULT_RULE_PARAMS.items()
        }
        config_params: dict[str, dict[str, Any]] = config.get("rule_params", {})
        for rule_name, params in config_params.items():
            if rule_name in base_params:
                base_params[rule_name].update(params)
            else:
                base_params[rule_name] = dict(params)
        return base_params

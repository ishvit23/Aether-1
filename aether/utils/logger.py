"""Logging utilities: JSONL event logger, CSV metrics exporter, run metadata writer."""

from __future__ import annotations

import csv
import hashlib
import json
import logging
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from rich.logging import RichHandler


def setup_console_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure rich-based console logging.

    Args:
        level: Logging level (default INFO).

    Returns:
        Configured root logger.
    """
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)],
    )
    return logging.getLogger("aether")


class EventLogger:
    """Writes JSONL event logs for a simulation run."""

    def __init__(self, log_dir: str = "logs") -> None:
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.log_dir / "latest_run.jsonl"
        self._file = open(self.log_path, "w", encoding="utf-8")  # noqa: SIM115

    def log_event(self, tick: int, event_type: str, payload: dict[str, Any]) -> None:
        """Write a single event to the JSONL log.

        Args:
            tick: Current simulation tick.
            event_type: Type of event (spawn, move, trade, death, etc.).
            payload: Event-specific data.
        """
        event = {
            "timestamp": datetime.now(tz=UTC).isoformat(),
            "tick": tick,
            "event": event_type,
            "payload": payload,
        }
        self._file.write(json.dumps(event) + "\n")

    def close(self) -> None:
        """Flush and close the log file."""
        self._file.flush()
        self._file.close()


class MetricsWriter:
    """Writes per-tick CSV metrics snapshots."""

    COLUMNS = [
        "tick",
        "population",
        "avg_energy",
        "avg_strength",
        "num_births",
        "num_deaths",
        "num_trades",
        "num_combats",
    ]

    def __init__(self, log_dir: str = "logs") -> None:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        self.csv_path = log_path / "latest_metrics.csv"
        self._file = open(self.csv_path, "w", newline="", encoding="utf-8")  # noqa: SIM115
        self._writer = csv.writer(self._file)
        self._writer.writerow(self.COLUMNS)

    def write_tick(self, metrics: dict[str, Any]) -> None:
        """Write a single tick's metrics row.

        Args:
            metrics: Dict with keys matching COLUMNS.
        """
        row = [metrics.get(col, 0) for col in self.COLUMNS]
        self._writer.writerow(row)

    def close(self) -> None:
        """Flush and close the CSV file."""
        self._file.flush()
        self._file.close()


def write_run_metadata(
    seed: int,
    config_path: str,
    log_dir: str = "logs",
) -> Path:
    """Write run metadata JSON file at start of simulation.

    Args:
        seed: RNG seed used.
        config_path: Path to config file used.
        log_dir: Directory to write metadata file.

    Returns:
        Path to the written metadata file.
    """
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    meta_path = log_path / "latest_meta.json"

    # Config hash
    config_hash = ""
    if os.path.exists(config_path):
        with open(config_path, "rb") as f:
            config_hash = f"sha256:{hashlib.sha256(f.read()).hexdigest()}"

    # Git commit (best effort)
    git_commit = "unknown"
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            git_commit = result.stdout.strip()
    except FileNotFoundError:
        pass

    metadata = {
        "seed": seed,
        "config_hash": config_hash,
        "git_commit": git_commit,
        "started_at": datetime.now(tz=UTC).isoformat(),
        "python": (f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"),
        "aether_version": "0.1.0",
    }

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    return meta_path

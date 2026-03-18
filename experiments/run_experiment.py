"""Batch simulation runner for Aether-1 experiments.

Supports basic multi-seed runs and parameter sweeps.

Usage:
    # Basic multi-seed run
    uv run python experiments/run_experiment.py --config config/world_v1.json --seeds 5

    # Parameter sweep (grid search)
    uv run python experiments/run_experiment.py \
        --config config/world_v1.json \
        --sweep "combat.damage_multiplier=3.0:10.0:2.0" \
        --sweep "reproduction.energy_threshold=50:80:10" \
        --seeds 3 --ticks 500
"""

import argparse
import csv
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from itertools import product

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("experiment_runner")


def parse_sweep(sweep_str: str) -> tuple[str, str, list[float]]:
    """Parse a sweep specification like 'combat.damage_multiplier=3.0:10.0:2.0'.

    Returns:
        (rule_name, param_name, list_of_values)
    """
    param_path, range_spec = sweep_str.split("=")
    rule_name, param_name = param_path.split(".")
    parts = range_spec.split(":")
    start, end, step = float(parts[0]), float(parts[1]), float(parts[2])
    values = []
    v = start
    while v <= end + 1e-9:
        values.append(round(v, 4))
        v += step
    return rule_name, param_name, values


def run_single_sim(config_path: str, seed: int, ticks: int, overrides: dict | None = None) -> dict:
    """Run a single simulation and parse the metrics CSV for results.

    Args:
        config_path: Path to config JSON.
        seed: RNG seed.
        ticks: Number of ticks.
        overrides: Optional dict of rule_param overrides to patch into config.

    Returns:
        Dict with run metadata and results.
    """
    # Load and optionally patch config
    with open(config_path) as f:
        config = json.load(f)

    if overrides:
        for key, value in overrides.items():
            rule, param = key.split(".")
            config["rule_params"][rule][param] = value

    # Write patched config to temp file
    tmp_config = f"/tmp/aether_sweep_{seed}_{os.getpid()}.json"
    with open(tmp_config, "w") as f:
        json.dump(config, f)

    cmd = [
        sys.executable,
        "main.py",
        "run",
        "--config",
        tmp_config,
        "--seed",
        str(seed),
        "--ticks",
        str(ticks),
        "--viz",
        "none",
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)

        # Find the most recent metrics CSV
        log_dir = "logs"
        csv_files = sorted(
            [f for f in os.listdir(log_dir) if f.startswith("metrics_")],
            reverse=True,
        )

        final_pop = 0
        extinction_tick = None
        max_pop = 0

        if csv_files:
            csv_path = os.path.join(log_dir, csv_files[0])
            with open(csv_path) as cf:
                reader = csv.DictReader(cf)
                for row in reader:
                    pop = int(row["population"])
                    tick = int(row["tick"])
                    max_pop = max(max_pop, pop)
                    if pop == 0 and extinction_tick is None:
                        extinction_tick = tick
                    final_pop = pop

        return {
            "seed": seed,
            "success": True,
            "final_population": final_pop,
            "max_population": max_pop,
            "extinction_tick": extinction_tick,
            "overrides": overrides or {},
        }

    except subprocess.CalledProcessError as e:
        logger.error(f"Seed {seed} failed: {e.stderr[:200]}")
        return {
            "seed": seed,
            "success": False,
            "error": str(e.stderr[:200]),
            "overrides": overrides or {},
        }
    finally:
        if os.path.exists(tmp_config):
            os.remove(tmp_config)


def main():
    parser = argparse.ArgumentParser(description="Aether-1 Experiment Runner")
    parser.add_argument("--config", default="config/world_v1.json", help="Path to config")
    parser.add_argument("--seeds", type=int, default=5, help="Number of seeds to run")
    parser.add_argument("--ticks", type=int, default=200, help="Ticks per run")
    parser.add_argument(
        "--sweep",
        action="append",
        default=[],
        help='Parameter sweep, e.g. "combat.damage_multiplier=3:10:2"',
    )
    args = parser.parse_args()

    out_root = "experiments/results"
    os.makedirs(out_root, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Build sweep combinations
    sweep_dims = []
    for s in args.sweep:
        rule, param, values = parse_sweep(s)
        sweep_dims.append((f"{rule}.{param}", values))

    if sweep_dims:
        keys = [d[0] for d in sweep_dims]
        value_lists = [d[1] for d in sweep_dims]
        combinations = list(product(*value_lists))
        logger.info(
            f"Sweep: {len(combinations)} combinations × {args.seeds} seeds "
            f"= {len(combinations) * args.seeds} runs"
        )
    else:
        keys = []
        combinations = [()]
        logger.info(f"Running {args.seeds} seeds (no sweep)")

    # Run all combinations
    all_results = []
    for combo in combinations:
        overrides = dict(zip(keys, combo, strict=False)) if combo else None

        if overrides:
            override_str = ", ".join(f"{k}={v}" for k, v in overrides.items())
            logger.info(f"  Sweep: {override_str}")

        for seed in range(args.seeds):
            result = run_single_sim(args.config, seed, args.ticks, overrides)
            all_results.append(result)
            status = "✓" if result.get("success") else "✗"
            fp = result.get("final_population", "?")
            ext = result.get("extinction_tick", "survived")
            logger.info(f"    {status} seed={seed} pop={fp} ext={ext}")

    # Write sweep results CSV
    out_path = os.path.join(out_root, f"sweep_{timestamp}.csv")
    fieldnames = ["seed", "success", "final_population", "max_population", "extinction_tick"]
    fieldnames.extend(keys)

    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in all_results:
            row = {
                "seed": r["seed"],
                "success": r.get("success", False),
                "final_population": r.get("final_population", 0),
                "max_population": r.get("max_population", 0),
                "extinction_tick": r.get("extinction_tick", ""),
            }
            for k in keys:
                row[k] = r.get("overrides", {}).get(k, "")
            writer.writerow(row)

    logger.info(f"Results written to {out_path}")

    # Summary
    successes = [r for r in all_results if r.get("success")]
    if successes:
        avg_pop = sum(r["final_population"] for r in successes) / len(successes)
        survived = sum(1 for r in successes if r["extinction_tick"] is None)
        logger.info(
            f"Summary: {len(successes)}/{len(all_results)} succeeded, "
            f"avg final pop={avg_pop:.1f}, {survived} survived full run"
        )


if __name__ == "__main__":
    main()

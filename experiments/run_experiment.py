"""Batch simulation runner for Aether-1 experiments."""

import subprocess
import argparse
import os
import json
import logging
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("experiment_runner")

def run_single_sim(config: str, seed: int, ticks: int, out_dir: str):
    """Run a single simulation and return the final population."""
    import sys
    cmd = [
        sys.executable, "main.py", "run",
        "--config", config,
        "--seed", str(seed),
        "--ticks", str(ticks),
        "--viz", "none"
    ]
    try:
        logger.info(f"Starting seed {seed}...")
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return {"seed": seed, "success": True}
    except subprocess.CalledProcessError as e:
        logger.error(f"Seed {seed} failed: {e.stderr}")
        return {"seed": seed, "success": False, "error": e.stderr}

def main():
    parser = argparse.ArgumentParser(description="Aether-1 Experiment Runner")
    parser.add_argument("--config", default="config/world_v1.json", help="Path to config")
    parser.add_argument("--seeds", type=int, default=5, help="Number of seeds to run")
    parser.add_argument("--ticks", type=int, default=200, help="Ticks per run")
    parser.add_argument("--workers", type=int, default=4, help="Parallel workers")
    args = parser.parse_args()

    out_root = "experiments/results"
    os.makedirs(out_root, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment_id = f"exp_{timestamp}"
    
    logger.info(f"Running experiment {experiment_id} ({args.seeds} seeds)...")

    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = [
            executor.submit(run_single_sim, args.config, i, args.ticks, out_root)
            for i in range(args.seeds)
        ]
        results = [f.result() for f in futures]

    success_count = sum(1 for r in results if r["success"])
    logger.info(f"Experiment finished. Successes: {success_count}/{args.seeds}")

if __name__ == "__main__":
    main()

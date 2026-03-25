"""Headless orchestrator to pre-train RL policies over multiple episodes."""

import argparse
import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any

from aether.simulation.simulation import Simulation

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def average_q_tables(agents: list[Any]) -> dict[str, dict[str, float]]:
    """Aggregate Q-tables from multiple agents by averaging learned values."""
    master_q: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    state_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for agent in agents:
        if not agent.q_table:
            continue
        for state, actions in agent.q_table.items():
            for action, q_val in actions.items():
                master_q[state][action] += q_val
                state_counts[state][action] += 1

    # Compute averages
    for state, actions in master_q.items():
        for action, total_q in actions.items():
            count = state_counts[state][action]
            if count > 0:
                master_q[state][action] = total_q / count

    # Convert back to regular dict
    return {state: dict(actions) for state, actions in master_q.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description="Pre-train Q-learning policy.")
    parser.add_argument("--config", type=str, required=True, help="Path to scenario JSON")
    parser.add_argument("--episodes", type=int, default=50, help="Number of training episodes")
    parser.add_argument("--ticks", type=int, default=1000, help="Ticks per episode")
    parser.add_argument(
        "--out", type=str, default="models/policy_v4.json", help="Output policy JSON"
    )  # noqa: E501
    args = parser.parse_args()

    master_policy: dict[str, dict[str, float]] = {}

    episodes = args.episodes
    for ep in range(episodes):
        logger.info(f"--- Episode {ep + 1}/{episodes} ---")

        sim = Simulation(
            config_path=args.config,
            ticks=args.ticks,
            metrics_dir=None,  # No file writing during training
            policy=master_policy,  # Inject latest policy
        )

        # Dynamically set epsilon to decay: starts at 0.5, ends at 0.05
        epsilon = max(0.05, 0.5 * (1 - (ep / episodes)))
        for a in sim.world.agents.values():
            a.epsilon = epsilon

        sim.run()

        # Extract surviving agents' knowledge
        survivors = sim.world.living_agents()
        logger.info(f"Survived: {len(survivors)} agents")

        if survivors:
            master_policy = average_q_tables(survivors)
            logger.info(f"Master policy now tracks {len(master_policy)} unique states.")
        else:
            logger.warning("Extinction event. Existing policy remains unchanged.")

    # Save the final policy
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as f:
        json.dump(master_policy, f, indent=2)

    logger.info(f"Training complete. Master policy saved to {out_path}")


if __name__ == "__main__":
    main()

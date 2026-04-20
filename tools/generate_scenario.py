"""Script to generate Aether-1 configs dynamically from Natural Language using LLMs."""

import argparse
import json
import logging
from pathlib import Path

from tools.llm_client import LLMClient

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are a simulation config generator for the artificial life engine Aether-1.
Given a user request, generate a strictly 100% valid JSON configuration for a world.
Do not wrap it in markdown. The JSON must exactly match the schema below.

Example target schema:
{
  "world": { "width": 50, "height": 50, "wrap": true },
  "initial": {
    "agents": 30,
    "resource_distribution": { "food": 0.01, "material": 0.005 }
  },
  "factions": [
    {
      "id": "Frost-Walkers",
      "color": "#00FFFF",
      "description": "Vicious nomadic warriors molded by extreme winter cold.",
      "traits": { "aggression": [0.8, 1.0], "speed": [1.0, 1.5] }
    },
    { "id": "Snow-Hunters", "color": "#FFFFFF", "traits": { "strength": [10.0, 15.0] } }
  ],
  "rules_order": [
    "hunger", "weather", "movement", "resource_spawn", "animal", "collect",
    "combat", "trade", "decay", "faction", "build", "mutation", "death"
  ],
  "rule_params": {
    "hunger":       { "decay_rate": 0.8, "critical_threshold": 15.0 },
    "movement":     { "max_steps": 1.0, "energy_cost": 0.5, "goal_bias": 0.3 },
    "resource_spawn": { "spawn_interval": 1, "spawn_prob": 0.12, "amount": 12.0 },
    "animal":       { "rabbit_cap": 80, "wolf_cap": 15 },
    "decay":        { "wall_decay": 2.0, "nest_decay": 1.0 },
    "reproduction": {
      "energy_threshold": 60.0,
      "child_cost": 25.0,
      "min_repro_age": 20.0,
      "repro_cooldown": 30.0,
      "max_population": 150.0
    },
    "mutation":     { "rate": 0.05, "max_delta": 0.1 },
    "death":        { "energy_floor": 0.0, "max_age": 500.0 }
  },
  "ticks": 1000,
  "seed": 42
}

Analyze the user's prompt. Tune the specific parameters, capacities, rates, and
resource distributions to perfectly model the ecosystem they requested as mathematical data.
ALWAYS output valid unescaped JSON. DO NOT include markdown backticks.
CRITICAL: The world.wrap parameter MUST ALWAYS be true to prevent agents from walking out of bounds.
"""


def generate_scenario(prompt: str, out_path: str, model: str) -> None:
    client = LLMClient(model=model)
    logger.info(f"Invoking target LLM '{model}' with atmospheric scenario: '{prompt}'")
    response = client.generate(prompt=prompt, system=SYSTEM_PROMPT)

    try:
        data = json.loads(response)
        if not data:
            raise ValueError(
                f"Target LLM '{model}' returned an empty payload. Is the server offline?"
            )

        out_file = Path(out_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        with out_file.open("w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Successfully generated simulation matrix at {out_path}")
    except json.JSONDecodeError as e:
        logger.error(f"LLM Hallucinated. Failed to securely parse model output as JSON: {e}")
        logger.debug(f"Raw Output: {response}")
    except Exception as e:
        logger.error(f"Fatal crash generating scenario: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--prompt", type=str, required=True, help="User prompt detailing the ecology."
    )
    parser.add_argument(
        "--out", type=str, default="config/generated_scenario.json", help="Saved path."
    )
    parser.add_argument(
        "--model", type=str, default="llama3.2:3b", help="Ollama target model name."
    )

    args = parser.parse_args()
    generate_scenario(args.prompt, args.out, args.model)

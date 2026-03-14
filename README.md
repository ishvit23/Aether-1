# Aether-1

Configurable multi-agent simulation engine for research-grade and production-grade simulations.

## Quick Start

```bash
# Install dependencies
uv sync

# Run a simulation
uv run python main.py run --config config/world_v1.json --seed 42 --ticks 100

# With console visualization
uv run python main.py run --config config/world_v1.json --ticks 100 --viz console

# Validate a config file
uv run python main.py validate-config --config config/world_v1.json
```

## Development

```bash
# Install with dev dependencies
uv sync

# Run tests
uv run pytest -v

# Run integration tests
uv run pytest -m integration -v

# Lint and format
uv run ruff check .
uv run ruff format .

# Type check
uv run mypy aether/
```

## Project Structure

```
aether/
  engine/       # Tick loop and rule engine
  world/        # Grid, cells, world loader
  agents/       # Agent model, traits, inventory, decision
  rules/        # Modular rule classes (hunger, combat, trade, etc.)
  actions/      # Action objects and executors
  resources/    # Generic resource models
  viz/          # Console (rich) and Pygame visualization
  utils/        # Logger, constants, RNG factory
  simulation/   # Orchestration
config/         # JSON/YAML world configs
tests/          # Unit and integration tests
```

## Recent Changes

- v0.1.0: Initial repo skeleton, CI, and placeholder tests
- v0.2.0-dev: Full V1 engine implementation — world, agents, rules, actions, visualization

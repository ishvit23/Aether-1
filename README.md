<div align="center">

# 🌌 Aether-1 

**A high-performance, deterministic, configurable multi-agent simulation engine.**

[![CI](https://github.com/ishvit23/Aether-1/actions/workflows/ci.yml/badge.svg)](https://github.com/ishvit23/Aether-1/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

## 📖 Overview

**Aether-1** is a deterministic, modular grid-based simulation engine built in Python. Designed for research, AI experimentation, and complex system modeling, it allows thousands of unique agents to interact, trade, fight, reproduce, and mutate over customizable torus-wrapped topologies. 

Powered by priority-based decision logic and an entirely decoupled rule engine, Aether-1 lets you define the physics and societal rules of the world exclusively through unified configuration structures.

---

## ✨ Key Features

*   **🧬 High-Fidelity Agent Models:** Agents possess nuanced statistics (health, energy, hunger, age) and fully mutable genetic traits (speed, strength, intelligence, aggression, greed, cooperation). 
*   **🌍 Deterministic Torus World:** The grid strictly adheres to seeded pseudorandom number generation to ensure 100% determinism. A torus wrapping matrix prevents boundary-clipping effects.
*   **⚙️ Uncoupled Rule Engine:** The game loop is completely data-driven. Rules like `hunger`, `combat`, `trade`, and `mutation` are decoupled classes injected into the simulation sequentially. 
*   **📊 Rich CLI & Metrics:** Experience beautiful console dashboards natively powered by `rich`. Automatically dump JSONL event structures and CSV metric checkpoints during execution. 
*   **🏎️ Production Ready Codebase:** Heavily sanitized using modern tooling: `uv` package management, `ruff` auto-linting, `mypy --strict` typings, and sprawling `pytest` suites.

---

## 🚀 Quick Start

### 1. Installation

Aether-1 uses the blazingly fast [uv](https://github.com/astral-sh/uv) package manager. 

```bash
# Clone the repository
git clone https://github.com/ishvit23/Aether-1.git
cd Aether-1

# Sync dependencies and create optimized virtual environment
uv sync
```

### 2. Run the Simulation

You can execute a full 500-tick simulation with a lively terminal dashboard using the built-in run command:

```bash
uv run python main.py run --config config/world_v1.json --ticks 500 --viz console
```

### 3. Validate Configurations

Verify your custom rule injections and population arrays before launching heavy simulations:
```bash
uv run python main.py validate-config --config config/world_v1.json
```

### 4. Step-by-Step Replay
Reconstruct and analyze past simulation events from a JSONL log file:
```bash
uv run python main.py replay --log logs/run_YYYYMMDD_HHMMSS.jsonl
```

### 5. Run Experiments
Execute batch simulations across multiple seeds for statistical analysis:
```bash
uv run python experiments/run_experiment.py --seeds 5 --ticks 200
```

### 6. Containerized Runs (Docker)
Build and run the simulation in a completely isolated environment:
```bash
docker build -t aether-1 .
docker run aether-1 run --ticks 100
```

---

## 🛠️ Project Structure

The engine's architecture enforces strict separation of concerns to allow easy drop-in implementations for future milestones.

```plaintext
aether/
├── actions/        # Executors for atomic operations (Trade, Attack, Move)
├── agents/         # Agent dataclass, genetic traits, and inventory logic
├── engine/         # The core TickEngine loop and sequential RuleEngine
├── resources/      # Abstracted models mapping world tangibles
├── rules/          # Drop-in ABC implementations for world physics/interaction
├── simulation/     # Top-level orchestration module
├── utils/          # Factory RNGs, constants, and logging mechanisms
└── viz/            # Console grid rendering and Pygame dashboard scaffolding
config/             # Extensible JSON/YAML files determining world states
tests/              # Robust 60+ assertion test suite matching strict metrics
```

---

## 💻 Development & Contributing

### Setup Hooks & Dependencies
Ensure you have the development layer installed to run local checks.
```bash
uv sync --extra dev
pre-commit install
```

### Running the Test Suite
Aether-1 maintains 100% passing tests for robust architectural guarantees.
```bash
# Execute unit and integration tests
uv run pytest -v 

# Static analysis 
uv run mypy aether/
uv run ruff check .
```

---

## 🗺️ Roadmap / Milestones

- [x] **Milestone 1:** World Core & Topology Wrapping
- [x] **Milestone 2:** Agent Models & Priority Matrix Decisions
- [x] **Milestone 3:** Core Engines (Tick / Rule) & Action TypedDicts
- [x] **Milestone 4:** Basic Rules (Hunger, Movement, Resources)
- [x] **Milestone 5:** Interactions (Combat, Trade)
- [x] **Milestone 6:** Evolution (Reproduction, Mutation)
- [x] **Milestone 7:** Advanced Logging, Diagnostic Replays & Experiments
- [x] **Milestone 8:** Containerization (Docker) & Final Documentation

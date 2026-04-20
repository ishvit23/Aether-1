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

**Aether-1** is a deterministic, modular grid-based simulation engine built in Python, paired with a modern React+Vite web dashboard for real-time visualization. Designed for research, AI experimentation, and complex system modeling, it allows thousands of unique agents to interact, trade, fight, reproduce, and mutate over customizable torus-wrapped topologies. 

Powered by priority-based decision logic and an entirely decoupled rule engine, Aether-1 lets you define the physics and societal rules of the world exclusively through unified configuration structures—now enhanced with Natural Language LLM generation!

---

## ✨ Key Features

*   **🧬 High-Fidelity Agent Models:** Agents possess nuanced statistics and fully mutable genetic traits. 
*   **🧠 RL & Tabular Q-Learning:** Intelligent agents natively map states using dynamic lifetimes, retaining generational success via *Fuzzy Lamarckian Inheritance*.
*   **🌍 Deterministic Torus World:** The grid strictly adheres to seeded pseudorandom number generation to ensure 100% determinism.
*   **🐺 Multi-Tier Artificial Ecology:** The maps populate natively with unscripted Prey (Rabbits) and Predators (Wolves) supporting complex hunting dependencies and seasonal shelter loops.
*   **⚙️ Uncoupled Rule Engine:** The game loop is data-driven. Rules like `hunger`, `combat`, `trade`, and `mutation` are decoupled classes.
*   **🗣️ LLM World Generation:** Generate fully compliant, mathematically-balanced ecosystem JSON configs directly from natural language prompts.
*   **🎨 Web Dashboard Visualization:** Explore your simulations in real-time or via replay with a sleek React + TypeScript HTML5 dashboard.

---

## 🚀 Quick Start

### 1. Backend Engine (Python / uv)

Aether-1 uses the blazingly fast [uv](https://github.com/astral-sh/uv) package manager for the simulation core.

```bash
# Clone the repository
git clone https://github.com/ishvit23/Aether-1.git
cd Aether-1

# Sync dependencies and create optimized virtual environment
uv sync
```

**Run a Simulation:**
```bash
uv run python main.py run --config config/world_v1.json --ticks 500 --viz console
```

**Validate Configurations:**
Verify your custom rule injections before launching heavy simulations:
```bash
uv run python main.py validate-config --config config/world_v1.json
```

**Step-by-Step Replay:**
Reconstruct past simulation events from a JSONL log file:
```bash
uv run python main.py replay --log logs/latest_run.jsonl
```

### 2. Frontend Web Dashboard (React / Vite)

The `web/` directory contains a modern 2D rendering dashboard.

```bash
cd web
npm install

# Start the Vite development server for live previews
npm run dev

# Build for production
npm run build

# Run linting
npm run lint
```

### 3. AI & Advanced Tools (`tools/`)

We provide several standalone utility scripts for advanced orchestration:

**LLM Scenario Generator:**
Generate JSON configs dynamically using local or remote LLMs (requires a configured LLM client).
```bash
uv run python -m tools.generate_scenario --prompt "A harsh winter landscape with heavily mutated wolves" --out config/generated_scenario.json --model llama3
```

**Q-Learning Policy Pre-Trainer:**
Train and average master RL policies across multi-episode headless runs to build smarter baseline agents.
```bash
uv run python -m tools.train_policy --config config/world_v1.json --episodes 50 --ticks 1000 --out models/policy_v4.json
```

**Simulation Analytics:**
Parse output metrics to quickly inspect run totals (births, deaths, hunts).
```bash
uv run python analyze_v4.py
```

---

## 🛠️ Project Structure

The project enforces strict separation of concerns across backend engine, web visuals, and toolkits.

```plaintext
Aether-1/
├── aether/         # Core Simulation Backend
│   ├── actions/    # Executors for atomic operations (Trade, Attack, Move)
│   ├── agents/     # Agent dataclass, genetic traits, and inventory logic
│   ├── engine/     # The core TickEngine loop and sequential RuleEngine
│   ├── rules/      # Drop-in implementations for world physics/interaction
│   └── viz/        # Console and backend render scaffolding
├── config/         # JSON/YAML files determining world states
├── logs/           # Output metrics, run histories, and JSONL replay files
├── tools/          # Standalone utilities
│   ├── generate_scenario.py  # LLM natural language config generation
│   ├── train_policy.py       # Multi-episode Q-Learning policy training
│   └── llm_client.py         # Submodule for LLM API negotiation
├── web/            # HTML5 Web Dashboard (React, TypeScript, Vite)
│   ├── src/        # Frontend components, rendering logic, and state management
│   └── package.json# NPM dependencies and scripts
├── experiments/    # Batch runners for multi-seed statistical analysis
├── tests/          # Robust pytest suite matching strict metrics
└── main.py         # Primary CLI entry point for the backend engine
```

---

## 💻 Development & Contributing

### Setup Hooks & Tests
Ensure you have the development layer installed to run local checks.
```bash
uv sync
pre-commit install
```

### Validating the Backend
Aether-1 maintains robust architectural guarantees.
```bash
# Execute unit and integration tests
uv run pytest -v 

# Static analysis and linting
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
- [x] **Milestone 9 (V4):** Learning Agents, Multi-Tier Ecology (Animals), Structure Sieging, and Titan-Scale Performance
- [x] **Milestone 10 (V5):** Language Model World Generation and HTML5 2D Pixel Art Overhaul

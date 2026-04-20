# Aether-1: Phase Highlights

This document tracks the high-level milestones, achievements, and major features of each development phase of the Aether-1 engine.

## Phase 1: Core Engine (V1)
**Theme**: Stable, deterministic foundational simulation.
- **Engine Stability**: Resolved initial population extinction bugs caused by extreme combat lethality and unchecked reproduction.
- **Action-Based Reproduction**: Eliminated passive reproduction; agents now explicitly choose to reproduce (`reproduce_action.py`) with strict guards (age limits, cooldowns, population caps).
- **Emergent Behavior**: Natural selection and essential agent behaviors (eating, moving, basic combat, trading) fully functional.
- **Testing & Quality**: Robust test suite with 65 passing automated tests and >95% code coverage.
- **Visualization**: Pygame visualizer for real-time tracking of agent actions and colors.

### Relevant Commands (V1)
```bash
# Full simulation run
uv run python main.py run --config config/world_v1.json --seed 42 --ticks 1000

# Run with Pygame visualization
uv run python main.py run --config config/world_v1.json --viz pygame

# Run unit and integration tests
uv run pytest --cov=aether

# Run linting and formatting
uv run ruff check . && uv run ruff format .
```

## Phase 2: Experiment Tooling (V2)
**Theme**: Scientific experiment platform and orchestrations.
- **Parameter Sweeping**: Grid-search support via `--sweep` flag in `run_experiment.py` to find optimal survival traits.
- **Results Analysis**: Automated `sweep_report.py` to rank the best/worst evolutionary parameter combinations.
- **Run Comparison**: standalone `compare_runs.py` allowing multi-file metrics comparison.
- **Scenario Library**: Created specialized configurable scenario worlds:
  - `colony_v1.json`: Peaceful, abundant resources, high cooperation.
  - `war_v1.json`: Hostile, scarce resources, double combat damage.
- **Clean Logging**: Refactored `logger.py` to maintain a single `latest_metrics.csv` to prevent log bloat.

### Relevant Commands (V2)
```bash
# Run a parameter sweep experiment
uv run python experiments/run_experiment.py --sweep "combat.damage_multiplier=3:8:1"

# Generate report from sweep results
uv run python experiments/sweep_report.py logs/sweep_results/

# Compare two previous metric runs
uv run python experiments/compare_runs.py logs/run_A.csv logs/run_B.csv

# Replay a specific simulation from event logs
uv run python main.py replay --log logs/run_1234.jsonl
```

## Phase 3: Civilization & Economy (V3)
**Theme**: Complex societal behaviors, environmental adaptation, and persistence.
- **Dynamic Factions**: Agents group into 6 semantic clans (`Warrior`, `Scout`, `Merchant`, `Scholar`, `Raider`, `Builder`) based on composite traits. Factions protect members and war against rivals.
- **Dynamic Environments**: Global weather states dynamically shift. Winter heavily spikes hunger decay and stops resource spawning, forcing survival strategies.
- **Memory Inheritance**: Agents accumulate and pass down up to 5 memories to their offspring, ensuring grudges and alliances persist across generations.
- **Base Building**: Agents alter map geometry by constructing defensive walls or energy-regenerating nests to survive harsh seasons.
- **Deep Lifecycles**: The population cap is expanded to 150, allowing highly dynamic boom-and-bust ecosystem cycles.

### Relevant Commands (V3)
```bash
# Run Aether-1 with the fully integrated V3 rules engine
uv run python main.py run --config config/world_v1.json --seed 42 --ticks 1000

# Execute the dedicated V3 Feature verification suite
uv run pytest tests/unit/test_v3_features.py

# Verify the full test suite with coverage
uv run pytest --cov=aether
```

## Phase 3.5: The God-Game Web Dashboard
**Theme**: High-performance streaming visualization and live metrics.
- **FastAPI Websocket Backend**: Upgraded the primitive CLI outputs into a high-performance Python backend (`aether/api/server.py`) that efficiently streams live JSON state payloads.
- **React/Vite Frontend**: Replaced the Pygame squares with a modern, high-quality dark mode web dashboard.
- **HTML5 Canvas Engine**: Custom-built `Renderer.tsx` that smoothly iterates over the grid, drawing structures, weather overlays, and faction-colored agents at 60 FPS.
- **Live Ecosystem Charts**: Real-time integration of Chart.js to natively plot the dynamic population boom-and-bust cycle sparklines and Faction dominance pie charts purely derived from the live socket stream.

### Relevant Commands (Phase 3.5)
```bash
# 1. Start the FastAPI Backend (Terminal 1)
uv run uvicorn aether.api.server:app --port 8000

# 2. Start the React/Vite Dashboard (Terminal 2)
cd web && npm run dev
```

## Phase 4: Learning Agents & Ecosystem Evolution
**Theme**: Intelligent RL decision systems and complex predator-prey dynamics.
- **Epsilon-Greedy Q-Learning**: Upgraded rigid heuristic Action logic to dynamic Reinforcement Learning. Agents learn optimal survival strategies via Bellman updates (Exploration vs Exploitation).
- **Lamarckian Brain Inheritance**: Offspring strictly `deepcopy` their parent's Q-Tables, representing evolutionary knowledge retention that enables complex, learned behaviors (like hunting) across generations.
- **Multi-Tier Ecology**: Balanced map saturation by spawning destructible organic entities. Agents hunt `Rabbit` prey for high food yields and dynamically defend against `Wolf` predators.
- **Destructible Architecture**: Structures natively transition into dynamic entities (`StructureData`) utilizing opacities that visually decay during Winter seasons on the live dashboard.
- **Headless Pre-Trainer**: Established an automated continuous-integration wrapper (`train_policy.py`) to pre-train, harvest, and serialize millions of ticks of RL brains into master JSON distributions.

### Relevant Commands (Phase 4)
```bash
# 1. Start the Headless Machine Learning Policy Trainer
uv run python -m tools.train_policy --config config/colony_v4.json --episodes 50 --ticks 1000

# 2. Run the Engine with dynamically loaded Brain Policies
uv run python main.py run --config config/colony_v4.json --policy models/policy_v4.json --ticks 500
```

## Phase 5: LLM World Generation & Visual Polish (V5)
**Theme**: Generative AI bootstrapping and massive visual immersion upgrades.
- **LLM Generator Architectural Pipeline**: Replaced hardcoded scenario configs with a generative matrix. `tools/generate_scenario.py` leverages `tools/llm_client.py` to ping local LLMs (like Ollama) using natural language prompts to mathematically deduce and construct rigorously constrained `JSON` simulation schemas.
- **Dynamic Faction Cultures**: The LLM natively outputs custom tribe Names, specific Hex colors, and rich socio-cultural lore descriptions, which are safely parsed by the `WorldLoader` directly into the agent mapping matrix.
- **2D Pixel Art Overhaul**: Transitioned entirely away from abstract UI shapes into high-resolution discrete 16x16 Pixel Art sprites loaded from `tiles.png`. 
- **Hue-Shifting Visualizer Cache**: The React frontend securely intercepts the Faction Hex Codes from the Python WebSocket and performs native HTML5 Off-Screen Canvas compositing to mathematically tint plain humanoid sprites to match their exact generated LLM cultures.
- **Micro-Animations & Atmosphere**: Implemented distinct biome coloring (Spring/Winter transparent screen-tints) and logic-bound floating emojis (⚔️, 💰, 💨) visibly tracking agent intent over their geographical placement on the Dashboard in real-time.

### Relevant Commands (Phase 5)
```bash
# 1. Orchestrate an entirely new universe using natural language
uv run python -m tools.generate_scenario --prompt "Generate a lush forest ecosystem containing a violent Viking tribe with high aggression, and a peaceful druid tribe that runs quickly away."

# 2. Start the FastAPI Backend against the generated LLM scenario 
uv run uvicorn aether.api.server:app --port 8000

# 3. Open the React Tile-Engine Visualizer
cd web && npm run dev
```

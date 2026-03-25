# AETHER-1 — MASTER SPECIFICATION

| Field | Value |
|---|---|
| Version | v2.0 |
| Role | Product Owner / System Architect |
| Status | Authoritative Specification |
| Date | 2026-03-14 |
| Python | >= 3.11 |
| License | MIT |

> **Purpose:** This document is the authoritative master specification and operator prompt for the Aether-1 project. It must be provided to any coding agent, IDE assistant, developer, or collaborator who will implement, run, or extend Aether-1. It covers the full design, folder structure, interfaces, tech stack, CI & git rules, version roadmap, milestones, acceptance criteria, and LLM integration plan.

---

## 1. Vision

Aether-1 is a configurable multi-agent simulation engine that runs worlds defined by modular rule sets and config files. Its purpose is to enable research-grade and production-grade simulations supporting evolution, trade, economy, conflict, cooperation, role-based behavior, and (later) LLM-driven high-level reasoning and world generation.

### Primary Goals

- Provide a stable, modular simulation engine (V1) that runs locally without LLMs or internet access.
- Expose a config-driven interface so any world (fantasy, economy, war, survival) can be instantiated by replacing a JSON/YAML config file.
- Support later integration of LLMs for world generation, scenario scripting, and leader-agent reasoning (optional and throttled).
- Deliver strong developer ergonomics: reproducible runs, event logging, experiment harness, CI pipelines, test coverage, and clear git workflows.

---

## 2. Core Philosophy

Every line of code and feature must conform to the following principles:

1. **Engine-neutral** — The core engine must not hardcode world-specific semantics. Rules, actions, and resources come entirely from configuration.
2. **Modularity** — Rules are independent modules implementing a small, stable interface. New rules are drop-in additions with zero engine changes.
3. **Generic agents** — Agent data structures must be flexible (dictionary-based traits and stats) to support future role additions without schema migrations.
4. **Deterministic testability** — Support RNG seeding throughout for reproducible integration tests and experiments.
5. **Minimal external dependencies (V1)** — No paid APIs, no network calls, no cloud services during V1 runs.
6. **Progress and auditability** — Every completed milestone must be committed, pushed, and recorded in `PROGRESS.md` before merging.

---

## 3. Technology Stack

> This section is authoritative. All choices below are mandatory for V1 unless explicitly marked as optional or future.

### 3.1 Language & Runtime

| Component | Choice | Version | Rationale |
|---|---|---|---|
| Language | Python | >= 3.11 | Dataclasses, typing improvements, tomllib built-in |
| Package manager | uv | Latest stable | 10-100x faster than pip; lock-file support; replaces pip+venv |
| Virtual env | managed by uv | — | `uv venv` created automatically via `uv sync` |
| Python version pin | `.python-version` file | 3.11.x | Ensures reproducibility across machines and CI |

### 3.2 Project Configuration & Packaging

Use `pyproject.toml` (PEP 621) as the single source of truth. Do **not** use `setup.py` or `setup.cfg`.

```toml
# pyproject.toml (required structure)
[project]
name = "aether-1"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "pygame>=2.5",
    "pyyaml>=6.0",
    "rich>=13.0",
    "click>=8.1",
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "ruff>=0.4",
    "mypy>=1.10",
]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
strict = true
python_version = "3.11"
```

### 3.3 Core Runtime Dependencies

| Package | Version | Usage |
|---|---|---|
| pygame | >=2.5 | Optional grid visualizer (V1). Toggle via `--viz` flag. |
| pyyaml | >=6.0 | YAML config support in addition to JSON |
| rich | >=13.0 | Console grid rendering, structured terminal output, progress bars |
| click | >=8.1 | CLI entrypoint with subcommands (`run`, `replay`, `validate-config`) |

### 3.4 Development & Tooling Dependencies

| Tool | Version | Purpose |
|---|---|---|
| pytest | >=8.0 | Unit and integration test runner |
| pytest-cov | >=5.0 | Coverage reports; enforce >= 80% coverage gate on CI |
| ruff | >=0.4 | Linter AND formatter (replaces flake8 + black + isort in one tool) |
| mypy | >=1.10 | Static type checking in strict mode |
| pre-commit | >=3.7 | Local hook runner: ruff, mypy, pytest on staged files |

> **Why ruff replaces flake8 + black + isort:** ruff is 10-100x faster than the legacy trio and handles linting, formatting, and import sorting in a single invocation. All new code must use `ruff check` (lint) and `ruff format` (format). Do **NOT** add flake8, black, or isort as dependencies.

### 3.5 Config Formats

| Format | Default | Notes |
|---|---|---|
| JSON | Yes (V1) | `world_v1.json` is the default config format |
| YAML | Supported | Loaded via pyyaml; preferred for human-authored configs |
| TOML | Future | May be added in V2 via `tomllib` (stdlib in 3.11+) |

### 3.6 Logging & Metrics

| Component | Choice | Notes |
|---|---|---|
| Structured event logs | JSONL | Newline-delimited JSON; one event per line |
| Metrics export | CSV | Per-tick metrics snapshot for downstream analysis |
| Console logging | rich + Python logging | `rich.logging.RichHandler`; INFO level default |
| Run metadata | JSON header file | Includes seed, config hash, git commit, timestamp |

### 3.7 Testing Stack

| Component | Choice | Notes |
|---|---|---|
| Framework | pytest >= 8.0 | Fixtures, parametrize, markers |
| Coverage | pytest-cov | Enforce >= 80% line coverage; fail CI if below |
| Test types | unit + integration | Unit per rule; integration = seeded full-run check |
| Determinism | RNG seed injection | All tests must pass `seed=42` via engine fixture |

### 3.8 CI/CD Pipeline

| Stage | Tool | Trigger | Action |
|---|---|---|---|
| Lint | `ruff check` | PR open | Fail if any lint errors |
| Format | `ruff format --check` | PR open | Fail if unformatted files |
| Type check | `mypy --strict` | PR open | Fail on type errors |
| Tests | `pytest --cov` | PR open | Fail if coverage < 80% |
| Integration | `pytest -m integration` | Merge to main | Full seeded run check |
| Build | `docker build` | Merge to main | Optional; produces `aether-1:latest` image |

```yaml
# .github/workflows/ci.yml (required structure)
name: CI
on: [pull_request]
jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync --frozen
      - run: uv run ruff check .
      - run: uv run ruff format --check .
      - run: uv run mypy aether/
      - run: uv run pytest --cov=aether --cov-fail-under=80
```

### 3.9 Containerisation (Optional, Milestone 8)

| Component | Choice | Notes |
|---|---|---|
| Base image | `python:3.11-slim` | Minimal footprint |
| Build tool | Docker / docker compose | Single-stage build for V1 |
| Entry | `python main.py run` | Accepts `--config`, `--seed`, `--ticks`, `--viz` flags |

### 3.10 Visualization

| Mode | Library | Toggle | Notes |
|---|---|---|---|
| Console grid | rich | Default | Rendered every N ticks; configurable interval |
| Pygame renderer | pygame >= 2.5 | `--viz pygame` | Color-coded cells; agent dots; resource heat map |
| Web UI (V3.5) | FastAPI + React/Vite | `uvicorn` + `npm run dev` | Live WebSocket streaming to HTML5 Canvas |
| 2D Pixel Art (V4) | React `Renderer.tsx` | UI toggle | 16×16 tile sprites; faction-colored agents; seasonal overlays |

> **Design rationale for 2D Pixel Art**: The pixel art renderer targets the existing React/Vite web client introduced in V3.5 — no Python changes required. The FastAPI WebSocket already streams full world-state JSON every tick; `Renderer.tsx` simply switches from solid-color rectangles to composited sprite tiles. This preserves decoupling between the Python engine and the frontend visualization layer.

## 4. Version Roadmap

| Version | Name | Key Deliverables | Status |
|---|---|---|---|
| V1 | Core Engine | Grid world, rule engine, agents, base rules, logging, console viz | ✅ Complete |
| V2 | Configurable Worlds & Tooling | Scenario library, parameter sweeps, experiment CLI tools, replay | ✅ Complete |
| V3 | Civilization & Economy | Factions, weather/seasons, memory inheritance, base building, pop cap 150 | ✅ Complete |
| V3.5 | Web Dashboard | FastAPI WebSocket backend, React/Vite frontend, HTML5 Canvas 60 FPS renderer, live charts | ✅ Complete |
| V4 | Learning Agents & Ecosystem | Animals (prey/predators), structure durability/siege, Q-Learning agents, policy training harness | 🔄 In Progress |
| V5 | Frontend Polish & LLM World Gen | 2D pixel art sprites, seasonal overlays, faction colors; LLM config generation from text prompts | 📋 Planned |
| V6 | LLM Agents & Narrative | Leader agents with LLM planning; narrative/description layer from event logs | 📋 Planned |
| V7 | Universe Engine | Plugin rule packs, multi-world orchestration, scalable experiments, research analytics | 📋 Planned |

---

## 5. High-Level Architecture

| Subsystem | Module / Folder | Responsibility |
|---|---|---|
| Engine | `aether/engine/` | Tick loop, rule runner, action dispatcher |
| World | `aether/world/` | Grid model, cell model, world loader |
| Agents | `aether/agents/` | Agent data structures, observe/decide API |
| Rules | `aether/rules/` | Modular rule classes (`apply(world, tick)`) |
| Actions | `aether/actions/` | Action objects and executor logic |
| Resources | `aether/resources/` | Generic resource models and type registry |
| Config | `config/` | JSON/YAML world definitions and rule parameter lists |
| Simulation | `aether/simulation/` | Orchestration scripts and experiment harness |
| Visualization | `aether/viz/` | Console (rich) and Pygame renderer |
| Logging | `aether/utils/` | JSONL logger, CSV exporter, run metadata writer |

### Data Flow

```
Config
  -> WorldLoader          (validates schema, instantiates World + Agents + Rules)
    -> Engine.tick_loop()
      -> for rule in rules_order:
           rule.apply(world, tick)   # mutates world state
      -> collect agent actions       # agents call observe() -> decide()
      -> validate actions
      -> execute actions (deterministic order: agent_id asc or seeded shuffle)
      -> post-tick: cleanup, logging, render
```

---

## 6. Folder Structure

```
aether-1/
  main.py                    # CLI entry (click)
  pyproject.toml             # PEP 621; single source of truth
  uv.lock                    # lock file; must be committed
  .python-version            # e.g. 3.11.9
  .pre-commit-config.yaml    # ruff + mypy + pytest hooks
  README.md
  PROGRESS.md
  Dockerfile                 # (Milestone 8)
  aether/
    engine/
      tick_engine.py
      rule_engine.py
    world/
      world.py
      cell.py
      world_loader.py
    agents/
      agent.py
      traits.py
      inventory.py
      decision.py
    rules/
      __init__.py
      base_rule.py           # ABC
      hunger_rule.py
      movement_rule.py
      resource_rule.py
      collect_rule.py
      combat_rule.py
      trade_rule.py
      reproduction_rule.py
      mutation_rule.py
      death_rule.py
    actions/
      action.py              # TypedDict + enums
      move_action.py
      collect_action.py
      attack_action.py
      trade_action.py
      reproduce_action.py
    resources/
      resource.py
      resource_types.py
    viz/
      console_viz.py         # rich renderer
      pygame_viz.py          # optional pygame
    utils/
      logger.py
      constants.py
      rng.py                 # centralised RNG factory
  config/
    world_v1.json
    rules_v1.json
    agents_v1.json
  experiments/
    run_experiment.py
    compare_runs.py
  tests/
    conftest.py              # shared fixtures (seeded engine, sample world)
    unit/
      test_engine.py
      test_world.py
      test_agent.py
      test_rules/
        test_hunger_rule.py
        test_movement_rule.py
        test_combat_rule.py
        test_trade_rule.py
        test_reproduction_rule.py
    integration/
      test_full_run.py       # seeded 500-tick smoke test
```

> **Notes:** Keep file responsibilities narrow. Each rule file contains a single Rule class. Keep the `aether` package importable so all tests can import modules directly.

---

## 7. World Model

### Grid Properties

| Property | Value |
|---|---|
| Type | 2D grid (list-of-lists) |
| Default size | 50 × 50 cells |
| Boundary | Wrap-around (torus) by default; configurable |
| Cell access | `world.get_cell(x, y)` — always use the accessor; never index directly |

### Cell Model

```python
@dataclass
class Cell:
    x: int
    y: int
    resources: dict[str, float] = field(default_factory=dict)
    agents: list[int] = field(default_factory=list)   # agent IDs
    terrain: str | None = None                        # future
```

### Resource System

- Resources are generic strings: `food`, `material`, `mana`, `gold`, ...
- Resource spawn rules are configurable: interval, probability, amount per spawn.
- Cells have an optional `max_capacity` per resource (config-driven).

---

## 8. Agent Model

```python
@dataclass
class Agent:
    id: int
    x: int
    y: int
    stats:     dict[str, float] = field(default_factory=dict)  # energy, health, hunger, age
    traits:    dict[str, float] = field(default_factory=dict)  # speed, strength, intelligence, aggression, greed, cooperation
    inventory: dict[str, float] = field(default_factory=dict)  # resource_name -> amount
    state:     str = 'idle'
    memory:    list = field(default_factory=list)               # empty in V1

    def observe(self, world: World) -> dict:    # returns local observation
        ...

    def decide(self, observation: dict, rng: RNG) -> Action:   # returns Action
        ...
```

> **Implementation rules:** `decide()` must be deterministic given a seeded RNG passed from the engine. Agents must **not** directly mutate the world — `decide()` returns an `Action`; the engine validates and executes it. Traits are numeric floats; decisions use trait-weighted heuristics.

---

## 9. Action System

```python
# aether/actions/action.py
from typing import TypedDict, Any
from enum import StrEnum

class ActionType(StrEnum):
    MOVE       = 'move'
    COLLECT    = 'collect'
    EAT        = 'eat'
    ATTACK     = 'attack'
    TRADE      = 'trade'
    REPRODUCE  = 'reproduce'
    IDLE       = 'idle'

class Action(TypedDict):
    type:     ActionType
    actor_id: int
    target:   int | tuple | None
    payload:  dict[str, Any]
```

### Execution Model

- Engine collects actions after rules that require agent decisions.
- Engine validates actions (boundary checks, target existence, energy cost).
- Actions execute in deterministic order: agent_id ascending, or seeded-shuffle if configured.
- All executed actions are logged as events to the JSONL log.

### Agent Priority Table

| Priority | Action | Trigger Condition |
|---|---|---|
| 1 (highest) | eat | `hunger > hunger_critical_threshold` |
| 2 | collect | nearby resource and inventory below capacity |
| 3 | attack | aggression trait check + target in range |
| 4 | trade | cooperation trait check + mutually beneficial neighbour |
| 5 | reproduce | `energy >= reproduction_threshold` |
| 6 | move | goal-directed or random walk |
| 7 (lowest) | idle | no other condition met |

---

## 10. Rule Engine

```python
# aether/rules/base_rule.py
from abc import ABC, abstractmethod
from aether.world.world import World

class Rule(ABC):
    name: str
    params: dict       # injected from config at load time

    def __init__(self, params: dict) -> None:
        self.params = params

    @abstractmethod
    def apply(self, world: World, tick: int) -> None: ...
```

### Engine Loop

```python
for tick in range(config.ticks):
    for rule_name in config.rules_order:
        rule = rule_registry[rule_name]
        rule.apply(world, tick)
    actions = engine.collect_actions(world.agents)
    valid_actions = engine.validate(actions, world)
    engine.execute(valid_actions, world)
    world.post_tick_cleanup(tick)
    logger.log_tick(tick, world)
    viz.render(world, tick)  # if enabled
```

### Rules Reference (V1)

| Rule | File | Key Config Params |
|---|---|---|
| hunger_rule | `hunger_rule.py` | `hunger.decay_rate`, `hunger.critical_threshold` |
| movement_rule | `movement_rule.py` | `movement.max_steps`, `movement.goal_bias` |
| resource_rule | `resource_rule.py` | `resource.spawn_interval`, `resource.spawn_prob`, `resource.amount` |
| collect_rule | `collect_rule.py` | `collect.max_per_tick`, `collect.capacity` |
| combat_rule | `combat_rule.py` | `combat.range`, `combat.damage_formula`, `combat.flee_threshold` |
| trade_rule | `trade_rule.py` | `trade.offer_threshold`, `trade.acceptance_prob_base` |
| reproduction_rule | `reproduction_rule.py` | `reproduction.energy_threshold`, `reproduction.child_cost` |
| mutation_rule | `mutation_rule.py` | `mutation.rate`, `mutation.max_delta`, trait bounds |
| death_rule | `death_rule.py` | `death.energy_floor`, `death.max_age` |

---

## 11. Config System

Configs are JSON (default) or YAML. All configs are validated on load against a schema. Missing keys raise `ConfigValidationError` with a clear message.

```json
// config/world_v1.json
{
  "world":   { "width": 50, "height": 50, "wrap": true },
  "initial": {
    "agents": 15,
    "resource_distribution": { "food": 0.01, "material": 0.005 }
  },
  "rules_order": [
    "hunger", "movement", "resource_spawn", "collect",
    "combat", "trade", "reproduction", "mutation", "death"
  ],
  "rule_params": {
    "hunger":       { "decay_rate": 1.0, "critical_threshold": 20.0 },
    "combat":       { "range": 1, "flee_threshold": 15.0 },
    "reproduction": { "energy_threshold": 80.0, "child_cost": 30.0 },
    "mutation":     { "rate": 0.05, "max_delta": 0.1 }
  },
  "ticks": 1000,
  "seed": 42
}
```

---

## 12. Logging & Metrics

### Event Log (JSONL)

One event per line. File: `logs/run_<timestamp>.jsonl`

```jsonl
{"timestamp":"2026-03-14T10:00:00Z","tick":1,"event":"spawn","payload":{"agent_id":3,"x":12,"y":7}}
{"timestamp":"2026-03-14T10:00:00Z","tick":1,"event":"trade","payload":{"a":3,"b":7,"resource":"food","amount":2.0}}
{"timestamp":"2026-03-14T10:00:00Z","tick":1,"event":"death","payload":{"agent_id":5,"cause":"starvation"}}
```

### Metrics CSV

File: `logs/metrics_<timestamp>.csv` — one row per tick.

```csv
tick,population,avg_energy,avg_strength,num_births,num_deaths,num_trades,num_combats
1,15,72.3,0.55,0,0,0,0
2,15,71.1,0.55,0,0,1,0
```

### Run Metadata

File: `logs/run_<timestamp>_meta.json` — written at start of each run.

```json
{
  "seed": 42,
  "config_hash": "sha256:...",
  "git_commit": "abc1234",
  "started_at": "2026-03-14T10:00:00Z",
  "python": "3.11.9",
  "aether_version": "0.1.0"
}
```

---

## 13. Visualization & Replay

### Console Renderer (default)

- Implemented with `rich`; prints colored grid every N ticks (configurable).
- Cells show: resource density (background color), agent count (dot), terrain (char).
- Summary panel: tick, population, avg energy, event counts.

### Pygame Renderer (optional)

- Toggle with `--viz pygame`.
- Color-coded cells for resource presence; agent dots sized by strength.
- Resource heat map overlay; optional agent trail rendering.

### Web Dashboard (V3.5+)

- **Backend:** FastAPI server (`aether/api/server.py`) with a `/api/simulate` WebSocket endpoint.
- **Frontend:** React + Vite SPA in `web/`, connects to the WebSocket and renders world state.
- **Canvas Engine:** `web/src/components/Renderer.tsx` — custom HTML5 Canvas loop at 60 FPS.
- **Charts:** `web/src/components/Charts.tsx` — Chart.js sparklines for population and faction pie charts.
- **Run:** `uvicorn aether.api.server:app --port 8000` (backend) + `cd web && npm run dev` (frontend).

### 2D Pixel Art Renderer (V5, frontend only)

> **Deferred from V4.** Will be implemented in V5 alongside LLM World Generation. The backend engine does not need to change — this is a pure `Renderer.tsx` upgrade once enough engine features (Animals, Q-Learning) exist to make the visualization meaningful.

- **Tileset:** 16×16 PNG sprite sheet (`web/public/tiles.png`) with tiles for `grass`, `dirt`, `wall`, `nest`, `berry_bush`, `rock`.
- **Agents:** 4-directional character sprites (`agent_N/S/E/W`), hue-shifted by faction ID using `OffscreenCanvas` for distinct clan colors.
- **Animals:** Separate `rabbit` and `wolf` sprite variants.
- **State Emotes:** Small icon bubble rendered above agents: `⚔️` (combat), `💰` (trade), `🏗️` (building), `🐺` (being chased).
- **Season Overlay:** Full-canvas composited tint layer — white snow in Winter, warm orange in Autumn, bright green in Spring.
- **Camera:** Optional pan-and-zoom (mouse wheel), centering on the highest-density faction cluster.

### Replay

- Replay engine reads JSONL event log and reconstructs world state per tick.
- CLI: `python main.py replay --log logs/latest_run.jsonl`
- Must be bit-for-bit identical to original run given the same seed.

---

## 14. Tests & Quality Gates

### Shared Fixtures (`tests/conftest.py`)

```python
import pytest
from aether.engine.tick_engine import TickEngine
from aether.world.world_loader import WorldLoader

@pytest.fixture
def seeded_engine():
    config = WorldLoader.load('config/world_v1.json')
    return TickEngine(config, seed=42)

@pytest.fixture
def small_world():
    config = WorldLoader.load('config/world_v1.json')
    config.world.width = 10
    config.world.height = 10
    config.initial.agents = 5
    return TickEngine(config, seed=0).world
```

### Quality Gates

| Gate | Tool | Threshold | Enforced In |
|---|---|---|---|
| Line coverage | pytest-cov | >= 80% | CI (every PR) |
| Lint errors | ruff check | 0 errors | CI + pre-commit |
| Format | ruff format | 0 diffs | CI + pre-commit |
| Type errors | mypy --strict | 0 errors | CI (every PR) |
| Integration run | pytest -m integration | Pass | CI (merge to main) |

---

## 15. Git & Workflow Rules

### Branch Strategy

| Branch | Purpose | Merge Target |
|---|---|---|
| `main` | Stable releases only; tagged | — |
| `develop` | Integration branch; always green | `main` (per release) |
| `feature/<desc>` | Feature work branches | `develop` via PR |
| `hotfix/<id>` | Urgent fixes off main | `main` + `develop` |

### Commit Message Format

```
<area>: <short description>

# Examples:
engine: add tick loop skeleton
rules: implement hunger_rule with configurable decay
ci: add mypy strict check to workflow
config: validate schema on load with ConfigValidationError
```

### PR Checklist (mandatory)

1. Tests added or updated for every changed module.
2. CI green: ruff, mypy, `pytest --cov` all passing.
3. `PROGRESS.md` updated with a new entry (see Section 16).
4. PR description: summary, files changed, tests added, screenshots if viz changed.
5. `README.md` updated if user-facing CLI or config changes.

---

## 16. PROGRESS.md Template

Every successful development step must **prepend** a new entry to `PROGRESS.md`. Required before opening any PR.

```
---
Date:     2026-03-14
Version:  v0.1.0
Feature:  world core (WorldLoader, Cell, Grid)
Branch:   feature/world-core
Files:    aether/world/world.py, aether/world/cell.py, aether/world/world_loader.py
Tests:    tests/unit/test_world.py (12 tests added)
Coverage: 84%
CI:       passing
Notes:    wrap-around boundary implemented; config validation raises ConfigValidationError
Commit:   abc1234
PR:       https://github.com/org/aether-1/pull/3
---
```

---

## 17. Milestones & Deliverables

| Milestone | Branch | Tag | Key Deliverables |
|---|---|---|---|
| M0 — Repo skeleton + CI | `feature/skeleton` | v0.1.0 | `pyproject.toml`, `uv.lock`, `.pre-commit`, GitHub Actions CI, placeholder tests passing |
| M1 — World core | `feature/world-core` | — | `World`, `Cell`, `WorldLoader`, config parsing, schema validation, unit tests |
| M2 — Agent core | `feature/agent-core` | — | Agent dataclass, traits, inventory, observe stub, decide stub, unit tests |
| M3 — Engine skeleton | `feature/engine-core` | — | `TickEngine`, `RuleEngine`, RNG factory, rule loading, tick progression tests |
| M4 — Basic rules | `feature/basic-rules` | — | hunger, movement, resource_spawn, collect; rich console viz; rule unit tests |
| M5 — Interactions | `feature/interactions` | — | `combat_rule`, `trade_rule`; action validation; interaction unit tests |
| M6 — Evolution | `feature/evolution` | — | `reproduction_rule`, `mutation_rule`; trait inheritance demo; mutation tests |
| M7 — Logging & experiments | `feature/logging` | — | JSONL logger, CSV metrics, run metadata, replay CLI, experiment scripts |
| M8 — Packaging & docs | `feature/docs` | v0.2.0 | README with run instructions, Dockerfile, sample configs, changelog |

---

## 18. Acceptance Criteria (V1)

### Minimum Demonstration

- Run a 500-tick simulation with 10–20 agents using `world_v1.json` and `seed=42`.
- Observe: agents moving, collecting, trading occasionally, reproducing, and dying within the run.
- Produce JSONL event log and CSV metrics file on completion.
- Automated unit tests for every rule (at least happy path + one edge case each).
- Seeded integration test that asserts `population > 0` at tick 100 and at least 1 reproduction event.
- Console or Pygame viz toggled by `--viz` flag (no viz by default).

### Per-Milestone PR Acceptance

- Code + tests added and passing.
- CI green (ruff, mypy, `pytest --cov >= 80%`).
- `PROGRESS.md` entry prepended.
- `README.md` updated if user-facing changes.

---

## 19. Future LLM Integration Plan

> **V1 Constraint:** No LLM integration in V1. All LLM-related code lives behind an optional flag or in a separate module. V1 runs must work with zero network calls.

### Design Principles

- LLM usage is optional and restricted to high-level tasks only; never per-agent-per-tick.
- LLM calls must be throttled and cached; prefer local open-source models (Ollama + Llama 3 / Mistral) for cost-free local runs.
- LLM integration is implemented as a rule module (`llm_decision_rule`) or a config generator script, not baked into the engine.

### Planned Use Cases

| Version | Use Case | Approach |
|---|---|---|
| V5 | World / config generation | User prompt → LLM → valid JSON config; validated before load |
| V5 | Role / character templates | LLM generates role descriptions and default trait ranges |
| V6 | Leader agent decisions | One LLM call per leader per 100 ticks; cached; fallback to heuristic |
| V6 | Narrative summaries | LLM post-processes JSONL event log into human-readable story |

### Preferred Local Model Stack (V5+)

- **Runtime:** Ollama (local inference server; zero cost; no API key required)
- **Models:** Llama 3.1 8B for config generation; Mistral 7B for narrative summaries
- **Fallback:** HuggingFace transformers + GGUF quantized models if Ollama unavailable
- **Cloud fallback (opt-in only):** Anthropic Claude API via `ANTHROPIC_API_KEY` env var

---

## 20. Instructions for Coding Agents

> These instructions must be followed **exactly**. Any deviation requires an RFC file in the repo (`rfc/<date>-<topic>.md`) documenting the proposed change before implementation.

### Setup

1. Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Clone repo and run: `uv sync --frozen` (installs all deps including dev tools)
3. Install pre-commit hooks: `uv run pre-commit install`
4. Verify: `uv run pytest --cov=aether` (should pass with skeleton stubs)

### Daily Workflow

1. Always run tests locally before opening PRs: `uv run pytest`
2. Always run linting before commit: `uv run ruff check . && uv run ruff format .`
3. Update `PROGRESS.md` with a complete entry before PR creation.
4. Commit small, atomic changes (single responsibility per PR).
5. Use RNG seed propagation for all tests; never call `random.random()` directly — always use the engine RNG factory.
6. After PR merge to develop, run integration tests: `uv run pytest -m integration`
7. For each successful PR, append a short changelog entry to `README.md` under "Recent Changes".
8. When adding a new rule file: include example config snippet, unit tests, and update rules_order docs.
9. If switching IDEs or agents: resume by reading `PROGRESS.md`, then run the last successful scenario with the recorded seed.

### Code Style (enforced by ruff)

- Line length: 100 characters
- Imports: sorted and grouped by ruff (isort-compatible)
- Types: all public functions must have type annotations (`mypy --strict`)
- `@dataclass` preferred over plain dicts for domain objects (Agent, Cell, Config)
- No bare `except` clauses; always catch specific exception types

---

## 21. Key Code Snippets

### Rule Base Class

```python
# aether/rules/base_rule.py
from abc import ABC, abstractmethod
from aether.world.world import World

class Rule(ABC):
    name: str
    params: dict

    def __init__(self, params: dict) -> None:
        self.params = params

    @abstractmethod
    def apply(self, world: World, tick: int) -> None: ...
```

### Agent Skeleton

```python
# aether/agents/agent.py
from dataclasses import dataclass, field
from aether.actions.action import Action, ActionType

@dataclass
class Agent:
    id: int
    x: int
    y: int
    stats:     dict[str, float] = field(default_factory=dict)
    traits:    dict[str, float] = field(default_factory=dict)
    inventory: dict[str, float] = field(default_factory=dict)
    state:     str = 'idle'
    memory:    list = field(default_factory=list)

    def observe(self, world) -> dict:
        raise NotImplementedError

    def decide(self, observation: dict, rng) -> Action:
        raise NotImplementedError
```

### CLI Entry (click)

```python
# main.py
import click

@click.group()
def cli(): ...

@cli.command()
@click.option('--config', default='config/world_v1.json')
@click.option('--seed',   default=42,    type=int)
@click.option('--ticks',  default=1000,  type=int)
@click.option('--viz',    default='none', type=click.Choice(['none', 'console', 'pygame']))
def run(config, seed, ticks, viz):
    from aether.simulation.simulation import Simulation
    Simulation(config, seed=seed, ticks=ticks, viz=viz).run()

@cli.command()
@click.option('--log', required=True)
def replay(log):
    from aether.simulation.replay import ReplayEngine
    ReplayEngine(log).run()

if __name__ == '__main__':
    cli()
```

---

## 22. Future Guidance & Research Ideas

- Experiment with mixed agent populations: rule-based vs learned policies side by side in the same world.
- Add environmental dynamics: seasons, resource cycles, natural disasters, terrain changes.
- Create scenario templates for reproducible research experiments with parameterized configs.
- Add an automated experiment comparison harness that runs N configs and exports a comparison chart.
- Consider cloud execution (modal.com or AWS Batch) for large-scale experiments with local LLMs.
- Explore agent communication channels: shared memory cells, signaling, coalition formation.

---

## 23. Conclusion & Immediate Next Actions

> **This document is the authoritative prompt.** All implementation must follow this spec. If any deviation is necessary, create an RFC file in the repo root (`rfc/<date>-<topic>.md`) documenting the proposed change before implementing it.

### Immediate Next Actions

1. Initialize repo: `uv init`, add `pyproject.toml`, `uv.lock`, `.pre-commit-config.yaml`, GitHub Actions workflow **(Milestone 0)**.
2. Implement `WorldLoader`, `Cell`, `World` with config validation and push `feature/world-core` for review **(Milestone 1)**.
3. Implement `Agent` dataclass, observe/decide stubs, and RNG factory **(Milestone 2)**.
4. Implement `TickEngine`, `RuleEngine`, and basic rules **(Milestones 3 & 4)**.
5. Maintain `PROGRESS.md` and ensure all tests are seeded and deterministic throughout.

"""FastAPI server for the Aether-1 Web Dashboard.

Provides routes for listing scenarios and a WebSocket for live simulation streaming.
"""

import asyncio
import contextlib
import json
import logging
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from aether.api.ws_viz import WSRenderer
from aether.engine.rule_engine import RuleEngine, register_all_rules
from aether.engine.tick_engine import TickEngine
from aether.world.world_loader import WorldLoader

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aether.api")

app = FastAPI(title="Aether-1 Web Dashboard API")

# Allow React app to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev. Restrict in prod.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScenarioListResponse(BaseModel):
    scenarios: list[str]


@app.get("/api/scenarios", response_model=ScenarioListResponse)
async def list_scenarios() -> ScenarioListResponse:
    """List all available JSON scenario configs in the config directory."""
    config_dir = Path(__file__).parent.parent.parent / "config"
    scenarios = [f.name for f in config_dir.glob("*.json")]
    return ScenarioListResponse(scenarios=sorted(scenarios))


@app.websocket("/api/simulate")
async def websocket_simulate(websocket: WebSocket, config: str = "world_v1.json") -> None:
    """WebSocket endpoint to run and stream a simulation.

    The client can send JSON messages to control playback:
    {"action": "pause"}, {"action": "play"}, {"action": "step"}
    """
    await websocket.accept()
    logger.info(f"WebSocket connected. Requested config: {config}")

    config_path = Path(__file__).parent.parent.parent / "config" / config
    if not config_path.exists():
        await websocket.send_json({"type": "error", "message": f"Config not found: {config}"})
        await websocket.close()
        return

    # Initialize simulation components
    try:
        register_all_rules()
        cfg_data = WorldLoader.load(str(config_path))
        world = WorldLoader.build_world(cfg_data)
        
        # Inject generated RL Policy
        policy = None
        policy_path = Path(__file__).parent.parent.parent / "models" / "policy_v4.json"
        if policy_path.exists():
            with open(policy_path, "r") as f:
                policy = json.load(f)
            import copy
            for agent in world.agents.values():
                agent.q_table = copy.deepcopy(policy)
        rule_engine = RuleEngine()
        rule_params = WorldLoader.get_rule_params(cfg_data)
        rule_engine.load_rules(cfg_data["rules_order"], rule_params)
        max_ticks = cfg_data.get("ticks", 1000)
        tick_engine = TickEngine(world, rule_engine, max_ticks=max_ticks)
        renderer = WSRenderer(world)
    except Exception as e:
        logger.error(f"Failed to init simulation: {e}")
        await websocket.send_json({"type": "error", "message": f"Init failed: {e}"})
        await websocket.close()
        return

    # Simulation control state
    state = {"paused": False, "step": False, "delay": 0.05}

    # Background task to listen for control messages from the client
    async def listen_for_commands() -> None:
        try:
            while True:
                data = await websocket.receive_text()
                msg = json.loads(data)
                cmd = msg.get("action")
                if cmd == "pause":
                    state["paused"] = True
                elif cmd == "play":
                    state["paused"] = False
                elif cmd == "step":
                    state["paused"] = True
                    state["step"] = True
                elif cmd == "speed":
                    # e.g. {"action": "speed", "delay": 0.01}
                    state["delay"] = float(msg.get("delay", 0.05))
        except WebSocketDisconnect:
            pass
        except Exception as e:
            logger.error(f"WebSocket listen error: {e}")

    listener_task = asyncio.create_task(listen_for_commands())

    try:
        # Send initial full state
        initial_payload = renderer.render_full_state()
        initial_payload["type"] = "init"
        initial_payload["config"] = cfg_data
        await websocket.send_json(initial_payload)

        # Main simulation loop
        while world.tick < max_ticks:
            if state["paused"] and not state["step"]:
                await asyncio.sleep(0.1)
                continue

            if state["step"]:
                state["step"] = False

            # Run one tick
            tick_engine.run_tick(world.tick)
            world.tick += 1

            # Broadcast state
            payload = renderer.render_diff_state()
            payload["type"] = "tick"

            try:
                await websocket.send_json(payload)
            except RuntimeError:
                break  # Client disconnected (RuntimeError ASGI message)
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Failed to send websocket payload: {e}")
                break

            await asyncio.sleep(state["delay"])

        # End of simulation
        await websocket.send_json({"type": "end", "message": "Simulation complete."})

    except WebSocketDisconnect:
        logger.info("Client disconnected.")
    except Exception as e:
        logger.error(f"Simulation error: {e}")
    finally:
        listener_task.cancel()
        with contextlib.suppress(RuntimeError):
            await websocket.close()

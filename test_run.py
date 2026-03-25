import json
import traceback

from aether.api.ws_viz import WSRenderer
from aether.engine.rule_engine import RuleEngine, register_all_rules
from aether.engine.tick_engine import TickEngine
from aether.world.world_loader import WorldLoader

register_all_rules()
config_path = "config/colony_v4.json"
cfg_data = WorldLoader.load(config_path)
world = WorldLoader.build_world(cfg_data)
rule_engine = RuleEngine()
rule_params = WorldLoader.get_rule_params(cfg_data)
rule_engine.load_rules(cfg_data["rules_order"], rule_params)
tick_engine = TickEngine(world, rule_engine, max_ticks=cfg_data.get("ticks", 1000))
renderer = WSRenderer(world)

try:
    for _i in range(100):
        tick_engine.run_tick(world.tick)
        world.tick += 1

        payload = renderer.render_diff_state()
        try:
            s = json.dumps(payload)
        except Exception as e:
            print(f"CRASH AT TICK {world.tick}:", e)
            traceback.print_exc()
            break

    print("Test finished natively.")
except Exception as e:
    print("FATAL:", e)
    traceback.print_exc()

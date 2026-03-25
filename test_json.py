import json
from aether.world.world_loader import WorldLoader
from aether.engine.rule_engine import register_all_rules
from aether.api.ws_viz import WSRenderer
import traceback

register_all_rules()
config_path = "config/colony_v4.json"
cfg_data = WorldLoader.load(config_path)
world = WorldLoader.build_world(cfg_data)

renderer = WSRenderer(world)
payload = renderer.render_full_state()

try:
    s = json.dumps(payload)
    print("Success!")
except Exception as e:
    print("CRASH:", e)
    traceback.print_exc()

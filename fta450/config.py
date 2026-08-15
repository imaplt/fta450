import json
import yaml
from pathlib import Path

def load_config(path):
    print("Loading config from:", path)
    if path.endswith(".json"):
        with open(path) as f:
            return json.load(f)
    if path.endswith(".yaml") or path.endswith(".yml"):
        with open(path) as f:
            return yaml.safe_load(f)
    raise ValueError("Unsupported config format")

def load_defaults():
    cfg_path = Path(__file__).parent / "config.yaml"
    print("Loading config from:", cfg_path)
    try:
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f)
            return cfg.get("defaults", {})
    except FileNotFoundError:
        return {}


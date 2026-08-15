import json
import yaml

def load_config(path):
    if path.endswith(".json"):
        with open(path) as f:
            return json.load(f)
    if path.endswith(".yaml") or path.endswith(".yml"):
        with open(path) as f:
            return yaml.safe_load(f)
    raise ValueError("Unsupported config format")

def load_defaults():
    try:
        with open("config.yaml") as f:
            cfg = yaml.safe_load(f)
            return cfg.get("defaults", {})
    except FileNotFoundError:
        return {}

# utils/yaml_loader.py

import os
import yaml
import base64
import logging

DEFAULTS = {
    "config.yaml": {
        "dashboard_port": 5000,
        "c2_enabled": True,
        "stealth_mode": False,
        "log_level": "INFO"
    },
    "targets.yaml": [],
    "agent_profiles.yaml": [],
}

def auto_generate_yaml(path):
    name = os.path.basename(path)
    default_data = DEFAULTS.get(name, {})
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(default_data, f)
    return default_data

def load_yaml(path, allow_base64=True):
    name = os.path.basename(path)

    if not os.path.exists(path):
        logging.warning(f"[YAML] {name} not found. Auto-generating with defaults.")
        return auto_generate_yaml(path)

    try:
        with open(path, "r") as f:
            raw = f.read()
            if allow_base64:
                try:
                    raw = base64.b64decode(raw).decode()
                except Exception:
                    pass  # Not base64, continue with raw

        data = yaml.safe_load(raw)
        if data is None:
            logging.warning(f"[YAML] {name} was empty. Using defaults.")
            return auto_generate_yaml(path)

        return data

    except Exception as e:
        logging.error(f"[YAML] Error loading {name}: {e}. Reverting to defaults.")
        return auto_generate_yaml(path)

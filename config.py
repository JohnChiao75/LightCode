import json
import os
from pathlib import Path

DEFAULT_CONFIG = {
    "theme": "light",
    "font_size": 12,
    "debugger": {
        "python": "python3"
    }
}

CONFIG_PATH = Path.home() / ".lightcode" / "config.json"

def ensure_config_dir():
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

def load_config():
    ensure_config_dir()
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
            # 确保所有默认字段都存在
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            return config
    return DEFAULT_CONFIG.copy()

def save_config(config):
    ensure_config_dir()
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)
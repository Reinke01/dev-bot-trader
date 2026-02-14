import json
import os
from typing import Dict, Any

CONFIG_FILE = "settings.json"

class ConfigManager:
    def __init__(self):
        self.config: Dict[str, Any] = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_config(self, new_config: Dict[str, Any]):
        self.config.update(new_config)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=4)

    def get_config(self) -> Dict[str, Any]:
        return self.config

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

_config_instance = None

def get_config_manager() -> ConfigManager:
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager()
    return _config_instance

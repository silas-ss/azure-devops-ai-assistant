import yaml
from pathlib import Path

class ConfigManager:
    def __init__(self, config_path: str = "config/app_config.yaml"):
        self.config_path = config_path

    def load_config(self):
        try:
            path = Path(self.config_path)
            if not path.exists():
                return {}
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Erro ao carregar configuração: {e}")
            return {}

    def save_config(self, config: dict):
        try:
            path = Path(self.config_path)
            path.parent.mkdir(exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                yaml.safe_dump(config, f, allow_unicode=True)
        except Exception as e:
            print(f"Erro ao salvar configuração: {e}") 
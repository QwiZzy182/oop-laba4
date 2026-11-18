import json
import os
class SettingsManager:
    def __init__(self, filename: str = "app_settings.json"):
        self.filename = filename
        self.default_settings = {
            "limit": 10,
            "country": "RU",
            "last_query": "Linkin Park"
        }
        self.config = self.load()

    def load(self) -> dict:
        if not os.path.exists(self.filename):
            return self.default_settings.copy()
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k, v in self.default_settings.items():
                    data.setdefault(k, v)
                return data
        except Exception:
            return self.default_settings.copy()

    def save(self):
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")

    def get(self, key: str):
        return self.config.get(key, self.default_settings.get(key))

    def set(self, key: str, value):
        self.config[key] = value
        self.save()

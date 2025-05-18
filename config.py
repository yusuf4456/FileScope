import os
import json
import tkinter as tk
from constants import LIGHT_THEME, DARK_THEME


class AppConfig:

    def __init__(self):
        self.config_dir = os.path.join(os.path.expanduser("~"), ".metadata_finder")
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.default_config = {
            "theme": "light",
            "last_directory": os.path.expanduser("~"),
            "export_format": "json",
            "default_batch_limit": 50,
            "show_preview": True,
            "max_recent_files": 10,
            "recent_files": [],
            "preferred_hash": "md5",
            "window_size": "1000x800",
            "advanced_mode": False,
            "auto_check": True,
        }
        self.config = self.default_config.copy()
        self.load_config()

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    for key in self.default_config:
                        if key in loaded_config:
                            self.config[key] = loaded_config[key]
            else:
                self.save_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = self.default_config.copy()

    def save_config(self):
        try:
            if not os.path.exists(self.config_dir):
                os.makedirs(self.config_dir)

            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()

    def add_recent_file(self, file_path):
        recent_files = self.config.get("recent_files", [])

        if file_path in recent_files:
            recent_files.remove(file_path)

        recent_files.insert(0, file_path)

        max_files = self.config.get("max_recent_files", 10)
        self.config["recent_files"] = recent_files[:max_files]

        self.save_config()

    def clear_recent_files(self):
        self.config["recent_files"] = []
        self.save_config()

    def get_theme_colors(self):
        if self.config.get("theme") == "dark":
            return DARK_THEME
        return LIGHT_THEME

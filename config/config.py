# config/config.py
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass(frozen=True)
class GraphicsConfig:
    width: int = 800
    height: int = 480
    resizable: bool = False
    borderless: bool = True
    multisamples: int = 0
    maxfps: int = 60

@dataclass(frozen=True)
class AppConfig:
    graphics: GraphicsConfig = GraphicsConfig()
    assets_path: Path = Path("assets")
    debug: bool = False

    def apply(self):
        """Aplica la configuración a Kivy"""
        from kivy.config import Config
        
        for key, value in vars(self.graphics).items():
            Config.set('graphics', key, str(value))

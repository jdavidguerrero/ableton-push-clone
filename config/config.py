# config/config.py
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class GraphicsConfig:
    """Graphics configuration settings"""
    width: int = 400    
    height: int = 240
    resizable: bool = False
    borderless: bool = True
    multisamples: int = 0
    maxfps: int = 60
    fullscreen: bool = False  # Add fullscreen option

@dataclass(frozen=True)
class AppConfig:
    """Main application configuration"""
    graphics: GraphicsConfig = GraphicsConfig()
    assets_path: Path = Path("assets")
    debug: bool = False

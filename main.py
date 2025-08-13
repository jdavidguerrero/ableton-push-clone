import os
import platform
import logging
from pathlib import Path
from typing import Optional

# Early configuration before importing Kivy
if platform.system() == "Darwin":
    os.environ["KIVY_METRICS_DENSITY"] = "1"

from kivy.config import Config
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from kivy.resources import resource_add_path
from kivy.core.window import Window

# Centralized configuration
from config.config import AppConfig
from logic.state.app_state import AppState
from logic.clip_manager import ClipManager

from ui.screens.clip_view import ClipViewScreen
from ui.screens.devices_view import DevicesViewScreen
from ui.screens.note_view import NoteViewScreen
from ui.screens.settings_view import SettingsViewScreen
from ui.screens.mixer_view import MixerViewScreen

# IMPORTANT: Import ALL widget classes BEFORE loading KV files
from ui.widgets.clip_grid import ClipGrid
from ui.widgets.track_volume import TrackVolume
from ui.widgets.screen_header import ScreenHeader
from ui.widgets.status_bar import StatusBar
from ui.widgets.navigation_bar import NavigationBar
from ui.widgets.nav_button import NavButton
from ui.widgets.clip_slot import ClipSlot
from ui.widgets.track_header import TrackHeader
from ui.widgets.track_channel import TrackChannel
from ui.widgets.icon_button import IconButton



class PushControllerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config_app = AppConfig()
        self.state: Optional[AppState] = None
        self.clip_manager: Optional[ClipManager] = None
        
    def build(self):
        # 1. Apply configuration
        self._apply_config()
        
        # 2. Setup logging
        self._setup_logging()
        
        # 3. Load resources
        self._load_resources()
        
        # 4. Load KV files (AFTER importing classes)
        self._load_kv_files()
        
        # 5. Initialize business logic
        self._init_business_logic()
        
        # 6. Setup window events
        self._setup_window()
        
        # 7. Create UI
        return self._create_ui()
    
    def _apply_config(self):
        """Apply Kivy configuration"""
        graphics = self.config_app.graphics
        Config.set('graphics', 'width', str(graphics.width))
        Config.set('graphics', 'height', str(graphics.height))
        Config.set('graphics', 'resizable', str(int(graphics.resizable)))
        Config.set('graphics', 'borderless', str(int(graphics.borderless)))
        Config.set('graphics', 'multisamples', str(graphics.multisamples))
        Config.set('graphics', 'maxfps', str(graphics.maxfps))
        Config.set('graphics', 'fullscreen', str(int(graphics.fullscreen)))  # Add fullscreen
    
    def _setup_logging(self):
        """Setup logging system"""
        level = logging.DEBUG if self.config_app.debug else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Push Controller App starting...")
    
    def _load_resources(self):
        """Load asset resources"""
        assets_path = Path(__file__).parent / self.config_app.assets_path
        resource_add_path(str(assets_path / "icons"))
    
    def _load_kv_files(self):
        """Load KV files automatically"""
        kv_dirs = [
            Path(__file__).parent / "ui" / "widgets",
            Path(__file__).parent / "ui" / "screens"
        ]
        
        for kv_dir in kv_dirs:
            if kv_dir.exists():
                for kv_file in kv_dir.glob("*.kv"):
                    try:
                        Builder.load_file(str(kv_file))
                        self.logger.debug(f"Loaded KV: {kv_file}")
                    except Exception as e:
                        self.logger.error(f"Error loading {kv_file}: {e}")
    
    def _init_business_logic(self):
        """Initialize state and business logic"""
        self.state = AppState()
        self.state.init_project(tracks=8, scenes=12)
        
        self.clip_manager = ClipManager(self.state)
    
    def _setup_window(self):
        """Setup window events and properties"""
        # Bind escape key to exit (useful for development)
        Window.bind(on_key_down=self._on_key_down)
        
        # Set fullscreen if configured
        if self.config_app.graphics.fullscreen:
            Window.fullscreen = 'auto'
    
    def _on_key_down(self, window, key, scancode, codepoint, modifier):
        """Handle key press events"""
        # ESC key to exit fullscreen or close app
        if key == 27:  # ESC key
            if Window.fullscreen:
                Window.fullscreen = False
            else:
                self.stop()
            return True
        return False
    
    def close_app(self):
        """Close the application"""
        self.logger.info("Application closing...")
        self.stop()
    
    def _create_ui(self):
        """Create user interface"""
        sm = ScreenManager()
        
        # Clip View (default)
        clip_view = ClipViewScreen(
            name='clip_view',
            app_state=self.state,
            clip_manager=self.clip_manager
        )
        sm.add_widget(clip_view)
        
        # NEW: Mixer View
        mixer_view = MixerViewScreen(
            name='mixer_view',
            app_state=self.state
        )
        sm.add_widget(mixer_view)
        
        # Devices View (updated index)
        devices_view = DevicesViewScreen(
            name='devices_view',
            app_state=self.state
        )
        sm.add_widget(devices_view)
        
        # Note View (updated index)
        note_view = NoteViewScreen(name='note_view')
        sm.add_widget(note_view)
        
        # Settings View (updated index)
        settings_view = SettingsViewScreen(name='settings_view')
        sm.add_widget(settings_view)
        
        # Set initial screen
        sm.current = 'clip_view'
        
        return sm

def main():
    """Main entry point"""
    try:
        PushControllerApp().run()
    except KeyboardInterrupt:
        logging.info("Application closed by user")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    main()

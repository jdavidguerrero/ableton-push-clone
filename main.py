# --- arriba del todo, igual que ya tienes ---
import os, platform
if platform.system() == "Darwin":
    os.environ["KIVY_METRICS_DENSITY"] = "1"

from kivy.config import Config
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'borderless', '1')   # opcional en Pi
Config.set('graphics', 'multisamples', '0') # perf
Config.set('graphics', 'maxfps', '60')

from kivy.core.window import Window
Window.size = (800, 480)

# --- Kivy / App ---
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from kivy.resources import resource_add_path
from pathlib import Path
from screens.clip_view import ClipViewScreen

# --- Estado & Mock ---
from logic.state.app_state import AppState
from logic.mocks.mock_live import MockLive

# --- MUY IMPORTANTE: importar clases Python usadas como tags KV ANTES de cargar KV ---
from widgets.clip_grid import ClipGrid   # ← asegura que <ClipGrid> exista al parsear KV
from widgets.track_volume import TrackVolume
from widgets.screen_header import ScreenHeader
from widgets.status_bar import StatusBar
from widgets.navigation_bar import NavigationBar
from widgets.nav_button import NavButton
from widgets.clip_slot import ClipSlot
from widgets.track_header import TrackHeader
from widgets.track_channel import TrackChannel

# --- UIController ---
from logic.utils.UIController import UIController

# Rutas de recursos
resource_add_path(str(Path(__file__).parent / "assets" / "icons"))


Builder.load_file('widgets/StatusBar.kv')
Builder.load_file('widgets/ScreenHeader.kv')
Builder.load_file('widgets/NavigationBar.kv')
Builder.load_file('widgets/NavButton.kv')
Builder.load_file('widgets/ClipSlot.kv')
Builder.load_file('widgets/TrackHeader.kv')
Builder.load_file('widgets/TrackChannel.kv')
Builder.load_file('widgets/TrackVolume.kv')


Builder.load_file('screens/clipView.kv')


class PushControllerApp(App):
     def build(self):
        root = FloatLayout()
        sm = ScreenManager()
        sm.add_widget(ClipViewScreen(name='clipView')) 
        root.add_widget(sm)
        
        self.state = AppState()
        self.state.init_project(8, 12) 
        
        self.ui = UIController(root)
        
        return root


if __name__ == "__main__":
    PushControllerApp().run()
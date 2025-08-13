from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty
from kivy.app import App
from logic.bus import bus

class NavigationBar(BoxLayout):
    selected_index = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Listen for screen changes to update active state
        bus.on("screen:changed", self._on_screen_changed)
    
    def _on_screen_changed(self, **kwargs):
        """Update active state when screen changes externally"""
        screen_name = kwargs.get('screen', '')
        screen_map = {
            'clip_view': 0,
            'mixer_view': 1,      # NEW MIXER VIEW
            'devices_view': 2,    # Updated indices
            'note_view': 3,
            'settings_view': 4
        }
        
        if screen_name in screen_map:
            new_index = screen_map[screen_name]
            if new_index != self.selected_index:
                self.selected_index = new_index
                self._update_button_states()

    def set_active(self, idx):
        self.selected_index = idx
        self._update_button_states()
        self._navigate_to_screen(idx)
    
    def _update_button_states(self):
        """Update visual states of all buttons"""
        for i, child in enumerate(self.children[::-1]):  # children reversed
            if hasattr(child, 'active'):
                child.active = (i == self.selected_index)
    
    def _navigate_to_screen(self, screen_index):
        """Navigate to screen based on button index"""
        app = App.get_running_app()
        if not app or not hasattr(app, 'root'):
            return
        
        screen_manager = app.root
        if not hasattr(screen_manager, 'current'):
            return
        
        # Updated screen map for 5 screens
        screen_map = {
            0: 'clip_view',
            1: 'mixer_view',      # NEW MIXER VIEW
            2: 'devices_view',    # Updated indices
            3: 'note_view',
            4: 'settings_view'
        }
        
        screen_name = screen_map.get(screen_index)
        if screen_name and hasattr(screen_manager, 'has_screen'):
            if screen_manager.has_screen(screen_name):
                screen_manager.current = screen_name
                # Emit event so all NavigationBars update
                bus.emit("screen:changed", screen=screen_name)
            else:
                print(f"Screen '{screen_name}' not found in ScreenManager")

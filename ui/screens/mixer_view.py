from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty, StringProperty, ListProperty
from logic.bus import bus
from typing import Optional
import logging
from kivy.metrics import dp

class MixerViewScreen(Screen):
    """Dedicated mixer view for all tracks with enhanced controls"""
    
    # Master controls
    master_volume = NumericProperty(0.8)
    master_bpm = NumericProperty(120.0)
    
    # Track data
    tracks_data = ListProperty([])
    
    def __init__(self, app_state=None, live_integration=None, **kwargs):
        super().__init__(**kwargs)
        self.app_state = app_state
        self.live_integration = live_integration  # AGREGAR ESTO
        self.logger = logging.getLogger(__name__)
        
        # Create demo tracks data (same as ClipView)
        self.demo_tracks = self._create_demo_tracks()
        
        # Setup event listeners
        self._setup_events()
    
    def _setup_events(self):
        """Setup event bus listeners"""
        bus.on("track:volume", self._on_track_volume_changed)
        bus.on("track:pan", self._on_track_pan_changed)
        bus.on("track:mute", self._on_track_mute_changed)
        bus.on("track:solo", self._on_track_solo_changed)
        bus.on("track:arm", self._on_track_arm_changed)
        bus.on("track:send", self._on_track_send_changed)
        bus.on("live:track_names", self._on_live_track_names)  # NUEVO

    def on_enter(self):
        """Called when screen becomes active"""
        self.logger.info("Entering Mixer View")
        self._populate_mixers()
    
    def _create_demo_tracks(self):
        """Create demo track data (same as ClipView)"""
        return [
            {"name": "Kick", "color": (0, 0.016, 1, 1)},
            {"name": "Hats", "color": (0, 1, 0.05, 1)},
            {"name": "Bass", "color": (1, 0.6, 0, 1)},
            {"name": "Tom", "color": (1, 0.85, 0, 1)},
            {"name": "FX", "color": (1, 0, 0.48, 1)},
            {"name": "Pad", "color": (0, 1, 0.97, 1)},
            {"name": "Lead", "color": (1, 0.57, 0, 1)},
            {"name": "Keys", "color": (0, 0.016, 1, 1)},
            {"name": "Perc", "color": (0.8, 0.2, 0.8, 1)},
            {"name": "Vocal", "color": (0.2, 0.8, 0.2, 1)},
        ]
    
    def _populate_mixers(self):
        """Create mixer widgets for all tracks - ENHANCED VERSION"""
        from ui.widgets.track_volume import TrackVolume
        
        if hasattr(self.ids, 'mixers_container'):
            mixers_container = self.ids.mixers_container
            mixers_container.clear_widgets()
            
            for track_idx, track in enumerate(self.demo_tracks):
                # Enhanced mixer widget with better sizing for full screen
                mixer = TrackVolume(
                    track_index=track_idx,
                    track_name=track["name"],  # PASS REAL TRACK NAME
                    size_hint_x=None,
                    width=dp(85),  # Reduced width to fit more tracks on screen
                )
                
                # Update mixer with track state if available
                if self.app_state and track_idx in self.app_state.m.tracks:
                    track_state = self.app_state.m.tracks[track_idx]
                    mixer.volume = track_state.volume
                    mixer.pan = track_state.pan
                    mixer.is_mute = track_state.mute
                    mixer.is_solo = track_state.solo
                    mixer.is_arm = track_state.arm
                
                mixers_container.add_widget(mixer)
            
            # Set container width for scrolling
            mixers_container.width = len(self.demo_tracks) * 88  # 85 + 3 spacing
    
    # Event Handlers
    def _on_track_volume_changed(self, **kwargs):
        """Handle track volume changes from mixer widgets"""
        track = kwargs.get('track', 0)
        value = kwargs.get('value', 0.0)
        self.logger.debug(f"Track {track} volume: {value:.2f}")
        
        # Update app state if available
        if self.app_state:
            self.app_state.set_track_volume(track, value)
    
    def _on_track_pan_changed(self, **kwargs):
        """Handle track pan changes"""
        track = kwargs.get('track', 0)
        value = kwargs.get('value', 0.0)
        self.logger.debug(f"Track {track} pan: {value:.2f}")
        
        if self.app_state:
            self.app_state.set_track_pan(track, value)
    
    def _on_track_mute_changed(self, **kwargs):
        """Handle track mute changes"""
        track = kwargs.get('track', 0)
        value = kwargs.get('value', False)
        self.logger.debug(f"Track {track} mute: {value}")
        
        if self.app_state:
            self.app_state.set_track_mute(track, int(value))
    
    def _on_track_solo_changed(self, **kwargs):
        """Handle track solo changes"""
        track = kwargs.get('track', 0)
        value = kwargs.get('value', False)
        self.logger.debug(f"Track {track} solo: {value}")
        
        if self.app_state:
            self.app_state.set_track_solo(track, int(value))
    
    def _on_track_arm_changed(self, **kwargs):
        """Handle track arm changes"""
        track = kwargs.get('track', 0)
        value = kwargs.get('value', False)
        self.logger.debug(f"Track {track} arm: {value}")
        
        if self.app_state:
            self.app_state.set_track_arm(track, int(value))
    
    def _on_track_send_changed(self, **kwargs):
        """Handle track send changes"""
        track = kwargs.get('track', 0)
        send = kwargs.get('send', 'A')
        value = kwargs.get('value', 0.0)
        self.logger.debug(f"Track {track} send {send}: {value:.2f}")
        
        if self.app_state:
            self.app_state.set_track_send(track, send, value)

def _on_live_track_names(self, **kwargs):
    """Update mixer with real Live tracks"""
    names = kwargs.get('names', [])
    self.logger.info(f"🎚️ Mixer updated with {len(names)} tracks from Live")
    
    # Update demo tracks with real names
    self.demo_tracks = []
    for i, name in enumerate(names):
        track = {
            "name": name,
            "color": self._get_track_color(i)
        }
        self.demo_tracks.append(track)
    
    # Refresh UI if screen is active
    if hasattr(self, 'ids') and hasattr(self.ids, 'mixers_container'):
        self._populate_mixers()

def _get_track_color(self, track_index):
    """Get default color for track"""
    colors = [
        (0, 0.016, 1, 1),      # Azul
        (0, 1, 0.05, 1),       # Verde
        (1, 0.6, 0, 1),        # Naranja
        (1, 0.85, 0, 1),       # Amarillo
        (1, 0, 0.48, 1),       # Rosa
        (0, 1, 0.97, 1),       # Cyan
        (1, 0.57, 0, 1),       # Naranja claro
        (0.8, 0.2, 0.8, 1),    # Morado
    ]
    return colors[track_index % len(colors)]
from kivy.uix.screenmanager import Screen
from kivy.properties import BooleanProperty, StringProperty, NumericProperty
from logic.bus import bus
from typing import Optional
import logging

class ClipViewScreen(Screen):
    """Main clip view screen with session grid and focused track mixer"""
    
    # Mixer state
    mixer_visible = BooleanProperty(False)
    focused_track = NumericProperty(0)
    current_track_text = StringProperty("Kick")
    
    def __init__(self, app_state=None, clip_manager=None, **kwargs):
        super().__init__(**kwargs)
        self.app_state = app_state
        self.clip_manager = clip_manager
        self.logger = logging.getLogger(__name__)
        
        # Initialize demo data
        self.demo_tracks = self._create_demo_tracks()
        
        # Setup event listeners
        self._setup_events()
    
    def _setup_events(self):
        """Setup event bus listeners"""
        bus.on("track:focus", self._on_track_focus)
        bus.on("clip:changed", self._on_clip_changed)
        bus.on("track:mixer_toggle", self._on_mixer_toggle)
    
    def on_enter(self):
        """Called when screen becomes active"""
        self.logger.info("Entering Clip View")
        
        # Load demo data into grid
        if hasattr(self.ids, 'clip_grid'):
            self.ids.clip_grid.populate_from_ableton(self.demo_tracks)
        
        # Focus first track by default
        self._focus_track(0)
    
    def _create_demo_tracks(self):
        """Create demo track data with consistent naming"""
        tracks = [
            {"name": "Kick", "color": (0, 0.016, 1, 1)},
            {"name": "Hats", "color": (0, 1, 0.05, 1)},
            {"name": "Bass", "color": (1, 0.6, 0, 1)},
            {"name": "Tom", "color": (1, 0.85, 0, 1)},
            {"name": "FX", "color": (1, 0, 0.48, 1)},
            {"name": "Pad", "color": (0, 1, 0.97, 1)},
            {"name": "Lead", "color": (1, 0.57, 0, 1)},
            {"name": "Keys", "color": (0, 0.016, 1, 1)},
            {"name": "Perc", "color": (0.8, 0.2, 0.8, 1)},  # Purple
            {"name": "Vocal", "color": (0.2, 0.8, 0.2, 1)}, # Green
        ]
        
        # Add clips to each track (consistent naming: "status" not "state")
        for track in tracks:
            track["clips"] = [{"status": "empty", "name": ""} for _ in range(12)]
        
        # Add some demo clips with different states
        tracks[0]["clips"][0] = {"status": "playing", "name": "Kick Loop"}
        tracks[1]["clips"][1] = {"status": "queued", "name": "Hats Pattern"}
        tracks[2]["clips"][2] = {"status": "empty", "name": "Bass Line"}
        tracks[3]["clips"][0] = {"status": "playing", "name": "Tom Beat"}
        tracks[4]["clips"][1] = {"status": "queued", "name": "FX Sweep"}
        tracks[8]["clips"][0] = {"status": "playing", "name": "Perc Loop"}
        tracks[9]["clips"][1] = {"status": "queued", "name": "Vocal Chop"}
        
        return tracks
    
    def _focus_track(self, track_id: int):
        """Focus on a specific track"""
        if 0 <= track_id < len(self.demo_tracks):
            self.focused_track = track_id
            self.current_track_text = self.demo_tracks[track_id]["name"]
            
            # Update mixer to show focused track
            self._update_mixer(track_id)
            
            # Emit focus event
            bus.emit("track:focus", track=track_id)
    
    def _update_mixer(self, track_id: int):
        """Update mixer to show focused track parameters"""
        if hasattr(self.ids, 'track_mixer'):
            mixer = self.ids.track_mixer
            mixer.track_index = track_id
            
            # Update mixer parameters from app_state if available
            if self.app_state and track_id in self.app_state.m.tracks:
                track_state = self.app_state.m.tracks[track_id]
                mixer.volume = track_state.volume
                mixer.pan = track_state.pan
                # Update sends, mute, solo, arm states...
                mixer.is_mute = track_state.mute
                mixer.is_solo = track_state.solo
                mixer.is_arm = track_state.arm
    
    def toggle_mixer(self):
        """Toggle mixer visibility"""
        self.mixer_visible = not self.mixer_visible
        self.logger.debug(f"Mixer visibility: {self.mixer_visible}")
    
    # Event Handlers
    def _on_track_focus(self, **kwargs):
        """Handle track focus events from other components"""
        track_id = kwargs.get('track', 0)
        self._focus_track(track_id)
    
    def _on_clip_changed(self, **kwargs):
        """Handle clip state changes"""
        track = kwargs.get('track', 0)
        scene = kwargs.get('scene', 0)
        status = kwargs.get('status', 'empty')
        
        # Update demo data to reflect changes
        if 0 <= track < len(self.demo_tracks) and 0 <= scene < len(self.demo_tracks[track]["clips"]):
            self.demo_tracks[track]["clips"][scene]["status"] = status
            self.logger.debug(f"Clip changed: T{track}S{scene} -> {status}")
    
    def _on_mixer_toggle(self, **kwargs):
        """Handle mixer toggle events"""
        track = kwargs.get('track', -1)
        if track == self.focused_track:
            self.mixer_visible = kwargs.get('visible', False)
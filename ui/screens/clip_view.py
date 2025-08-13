from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import BooleanProperty, StringProperty, NumericProperty
from logic.bus import bus
from typing import Optional
import logging

class ClipViewScreen(Screen):
    """Main clip view screen with session grid and multiple track mixers"""
    
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
        
        # Populate components separately
        self._populate_headers()
        self._populate_clips()
        self._populate_mixers()
        
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
            # Add 2 more tracks to test scrolling (10 total)
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
        # Add clips to the new tracks
        tracks[8]["clips"][0] = {"status": "playing", "name": "Perc Loop"}
        tracks[9]["clips"][1] = {"status": "queued", "name": "Vocal Chop"}
        
        return tracks
    
    def _populate_headers(self):
        """Create track headers separately"""
        from ui.widgets.track_header import TrackHeader
        
        if hasattr(self.ids, 'track_headers_container'):
            headers_container = self.ids.track_headers_container
            headers_container.clear_widgets()
            
            for track_idx, track in enumerate(self.demo_tracks):
                header = TrackHeader(
                    track_index=track_idx,
                    track_name=track["name"],
                    color_rgba=track["color"]
                )
                headers_container.add_widget(header)
            
            headers_container.width = len(self.demo_tracks) * 88
    
    def _populate_clips(self):
        """Create clips grid without headers"""
        from ui.widgets.clip_slot import ClipSlot
        
        if hasattr(self.ids, 'clips_container'):
            clips_container = self.ids.clips_container
            clips_container.clear_widgets()
            
            for track_idx, track in enumerate(self.demo_tracks):
                # Create clips column for this track
                clips_column = BoxLayout(
                    orientation='vertical',
                    size_hint_x=None,
                    width=88,
                    spacing=0
                )
                
                # Add clip slots (12 scenes)
                for scene_idx in range(12):
                    clip_info = track["clips"][scene_idx] if scene_idx < len(track["clips"]) else {}
                    
                    slot = ClipSlot(
                        track_index=track_idx,
                        scene_index=scene_idx,
                        status=clip_info.get("status", "empty"),
                    )
                    slot.label_text = clip_info.get("name", "")
                    clips_column.add_widget(slot)
                
                clips_container.add_widget(clips_column)
            
            clips_container.width = len(self.demo_tracks) * 88
    
    def _populate_mixers(self):
        """Create mixer widgets for all tracks"""
        from ui.widgets.track_volume import TrackVolume
        
        if hasattr(self.ids, 'mixers_container'):
            mixers_container = self.ids.mixers_container
            mixers_container.clear_widgets()
            
            for track_idx, track in enumerate(self.demo_tracks):
                mixer = TrackVolume(
                    track_index=track_idx,
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
            
            mixers_container.width = len(self.demo_tracks) * 88
    
    def _sync_header_scroll(self, scroll_x):
        """Sync header scroll with content scroll"""
        if hasattr(self.ids, 'headers_scroll'):
            self.ids.headers_scroll.scroll_x = scroll_x
    
    def _scroll_to_mixers(self):
        """Auto-scroll to show mixers when they appear"""
        from kivy.clock import Clock
        
        def scroll_down(dt):
            if hasattr(self.ids, 'content_scroll'):
                self.ids.content_scroll.scroll_y = 0.0  # Scroll to bottom
        
        # Schedule scroll after a short delay
        Clock.schedule_once(scroll_down, 0.2)
    
    def _focus_track(self, track_id: int):
        """Focus on a specific track"""
        if 0 <= track_id < len(self.demo_tracks):
            self.focused_track = track_id
            self.current_track_text = self.demo_tracks[track_id]["name"]
            
            # Emit focus event
            bus.emit("track:focus", track=track_id)
    
    def toggle_mixer(self):
        """Toggle mixer visibility"""
        self.mixer_visible = not self.mixer_visible
        self.logger.debug(f"Mixer visibility: {self.mixer_visible}")
        
        # Populate mixers when showing for the first time
        if self.mixer_visible:
            self._populate_mixers()
            # Auto-scroll to bottom to show mixers
            self._scroll_to_mixers()
    
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
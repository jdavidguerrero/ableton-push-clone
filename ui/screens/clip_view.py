from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty
from logic.bus import bus
from typing import Optional
import logging

class ClipViewScreen(Screen):
    """Main clip view screen - SIMPLIFIED, NO MIXER"""
    
    # Track state
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
    
    def on_enter(self):
        """Called when screen becomes active"""
        self.logger.info("Entering Clip View")
        
        # Populate components
        self._populate_headers()
        self._populate_clips()
        
        # Focus first track by default
        self._focus_track(0)
    
    def _create_demo_tracks(self):
        """Create demo track data"""
        tracks = [
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
        
        # Add clips to each track
        for track in tracks:
            track["clips"] = [{"status": "empty", "name": ""} for _ in range(12)]
        
        # Add some demo clips
        tracks[0]["clips"][0] = {"status": "playing", "name": "Kick Loop"}
        tracks[1]["clips"][1] = {"status": "queued", "name": "Hats Pattern"}
        tracks[2]["clips"][2] = {"status": "empty", "name": "Bass Line"}
        tracks[3]["clips"][0] = {"status": "playing", "name": "Tom Beat"}
        tracks[8]["clips"][0] = {"status": "playing", "name": "Perc Loop"}
        tracks[9]["clips"][1] = {"status": "queued", "name": "Vocal Chop"}
        
        return tracks
    
    def _populate_headers(self):
        """Create track headers"""
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
        """Create clips grid"""
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
    
    def _sync_header_scroll(self, scroll_x):
        """Sync header scroll with content scroll"""
        if hasattr(self.ids, 'headers_scroll'):
            self.ids.headers_scroll.scroll_x = scroll_x
    
    def _focus_track(self, track_id: int):
        """Focus on a specific track"""
        if 0 <= track_id < len(self.demo_tracks):
            self.focused_track = track_id
            self.current_track_text = self.demo_tracks[track_id]["name"]
            
            # Emit focus event
            bus.emit("track:focus", track=track_id)
    
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
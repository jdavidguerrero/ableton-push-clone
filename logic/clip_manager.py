from typing import Dict, Optional
from logic.bus import bus
from kivy.clock import Clock
import logging

class ClipManager:
    """Manages clip triggering logic and track exclusivity"""
    
    def __init__(self, app_state):
        self.app_state = app_state
        self.playing_clips: Dict[int, int] = {}  # {track_id: scene_id}
        self.logger = logging.getLogger(__name__)
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Setup event bus handlers"""
        bus.on("clip:trigger", self.handle_clip_trigger)
        bus.on("track:stop", self.handle_track_stop)  # This method needs to exist
    
    def handle_clip_trigger(self, **kwargs):
        """Handle clip trigger events with track exclusivity"""
        track = kwargs['track']
        scene = kwargs['scene']
        current_status = kwargs.get('current_status', 'empty')
        
        # If clip is playing, stop the track
        if current_status == "playing":
            self.stop_track(track)
        else:
            # Stop current clip on track and start new one
            self.trigger_clip(track, scene)
    
    def handle_track_stop(self, **kwargs):
        """Handle track stop events - ADD THIS METHOD"""
        track_id = kwargs.get('track', -1)
        if track_id >= 0:
            self.stop_track(track_id)
    
    def trigger_clip(self, track_id: int, scene_id: int):
        """Handle track exclusivity logic"""
        # Stop current clip if exists
        if track_id in self.playing_clips:
            old_scene = self.playing_clips[track_id]
            self.app_state.set_clip_status(track_id, old_scene, "empty")
        
        # Queue new clip
        self.app_state.set_clip_status(track_id, scene_id, "queued")
        
        # Simulate quantization (later: real quantization)
        Clock.schedule_once(
            lambda dt: self._start_clip(track_id, scene_id),
            0.5  # Fake quantization delay
        )
    
    def _start_clip(self, track_id: int, scene_id: int):
        """Start clip after quantization"""
        self.app_state.set_clip_status(track_id, scene_id, "playing")
        self.playing_clips[track_id] = scene_id
        self.logger.debug(f"Started clip {scene_id} on track {track_id}")
    
    def stop_track(self, track_id: int):
        """Stop all clips on a track"""
        if track_id in self.playing_clips:
            scene_id = self.playing_clips[track_id]
            self.app_state.set_clip_status(track_id, scene_id, "empty")
            del self.playing_clips[track_id]
            self.logger.debug(f"Stopped track {track_id}")


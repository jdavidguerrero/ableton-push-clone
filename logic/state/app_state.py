from .models import AppStateModel, TrackState, ClipSlotState, ClipStatus
from ..bus import bus
from dataclasses import dataclass, field
from typing import Dict, Optional
from enum import Enum

class ClipStatus(Enum):
    EMPTY = "empty"
    PLAYING = "playing"
    QUEUED = "queued"
    RECORDING = "recording"

class AppState:
    def __init__(self):
        self.m = AppStateModel()

    def _emit(self, key, **data):
        """Proxy event emission through the global bus.

        The previous implementation forwarded the ``data`` dictionary as a single
        positional argument which meant subscribers received a dict instead of
        the expected keyword arguments.  This made handlers such as
        ``on_volume(track, value)`` fail with ``TypeError``.  Expanding ``data``
        fixes the issue so callbacks receive named arguments.
        """
        bus.emit(f"state:{key}", **data)

    def init_project(self, tracks=8, scenes=8):
        """Initialize project with tracks and scenes"""
        self.m.scenes_count = scenes
        self.m.tracks = {}
        
        for t in range(tracks):
            # Create clips for this track
            clips_dict = {s: ClipSlotState() for s in range(scenes)}
            
            # Create track with all data
            tr = TrackState(
                id=t,
                name=f"Track {t+1}",
                clips=clips_dict
            )
            self.m.tracks[t] = tr
            
        self._emit("tracks_changed", tracks=self.m.tracks)

    def init_project_from_live(self, track_names: list, scenes=12):
        """Initialize project dynamically from Live track data"""
        self.m.scenes_count = scenes
        self.m.tracks = {}
        
        for track_id, track_name in enumerate(track_names):
            # Create clips for this track
            clips_dict = {s: ClipSlotState() for s in range(scenes)}
            
            # Create track with Live data
            tr = TrackState(
                id=track_id,
                name=track_name,  # Real name from Live
                clips=clips_dict
            )
            self.m.tracks[track_id] = tr
            
        self._emit("tracks_changed", tracks=self.m.tracks)
        self.logger.info(f"✅ App state initialized with {len(track_names)} tracks from Live")

    def set_clip_status(self, track_id: int, scene_id: int, status: str):
        """Update clip status creating new immutable objects"""
        if track_id in self.m.tracks:
            old_track = self.m.tracks[track_id]
            old_clip = old_track.clips.get(scene_id, ClipSlotState())
            
            # Create new clip with updated status
            new_clip = ClipSlotState(
                status=ClipStatus(status),
                name=old_clip.name,
                color=old_clip.color
            )
            
            # Create new clips dict
            new_clips = old_track.clips.copy()
            new_clips[scene_id] = new_clip
            
            # Create new track
            new_track = TrackState(
                id=old_track.id,
                name=old_track.name,
                clips=new_clips,
                volume=old_track.volume,
                pan=old_track.pan,
                sends=old_track.sends,
                mute=old_track.mute,
                solo=old_track.solo,
                arm=old_track.arm
            )
            
            # Update state
            self.m.tracks[track_id] = new_track
            self._emit("clip_changed", track=track_id, scene=scene_id, status=status)

    # mixer
    def set_volume(self, t:int, v:float):
        v = max(0.0, min(1.0, v))
        self.m.tracks[t].volume = v
        self._emit("track_volume", track=t, value=v)
    
    def set_track_volume(self, track_index: int, value: float):
        if track_index in self.m.tracks:
            self.m.tracks[track_index].volume = value
            self._emit("track_volume", track=track_index, value=value)
    
    def set_track_pan(self, track_index: int, value: float):
        if track_index in self.m.tracks:
            self.m.tracks[track_index].pan = value
            self._emit("track_pan", track=track_index, value=value)
    
    def set_track_send(self, track_index: int, send: str, value: float):
        if track_index in self.m.tracks:
            send_map = {"A": 0, "B": 1, "C": 2}
            if send in send_map:
                self.m.tracks[track_index].sends[send_map[send]] = value
                self._emit("track_send", track=track_index, send=send, value=value)
    
    def set_track_mute(self, track_index: int, value: int):
        if track_index in self.m.tracks:
            self.m.tracks[track_index].mute = bool(value)
            self._emit("track_mute", track=track_index, value=value)
    
    def set_track_solo(self, track_index: int, value: int):
        if track_index in self.m.tracks:
            self.m.tracks[track_index].solo = bool(value)
            self._emit("track_solo", track=track_index, value=value)
    
    def set_track_arm(self, track_index: int, value: int):
        if track_index in self.m.tracks:
            self.m.tracks[track_index].arm = bool(value)
            self._emit("track_arm", track=track_index, value=value)
    
    def trigger_clip(self, track_index: int, scene_index: int):
        """Handle clip triggering"""
        if track_index in self.m.tracks and scene_index < self.m.scenes_count:
            self._emit("clip_triggered", track=track_index, scene=scene_index)
    
    def focus_track(self, track_index: int):
        """Focus on a specific track"""
        self.m.current_track = track_index
        self._emit("track_focused", track=track_index)

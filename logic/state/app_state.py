from .models import AppStateModel, TrackState, ClipSlotState
from ..bus import bus

class AppState:
    def __init__(self): self.m = AppStateModel()
    def _emit(self, key, **data): bus.emit(f"state:{key}", data)

    def init_project(self, tracks=8, scenes=8):
        self.m.scenes_count = scenes
        self.m.tracks = {}
        for t in range(tracks):
            tr = TrackState(name=f"Track {t+1}")
            tr.clips = {s: ClipSlotState() for s in range(scenes)}
            self.m.tracks[t] = tr
        self._emit("tracks_changed", tracks=self.m.tracks)

    def set_clip_status(self, t:int, s:int, status:str):
        self.m.tracks[t].clips[s].status = status
        self._emit("clip_changed", track=t, scene=s, status=status)

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
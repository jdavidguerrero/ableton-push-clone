from dataclasses import dataclass, field
from typing import Dict, List, Tuple
Color = Tuple[float,float,float,float]

@dataclass
class ClipSlotState:
    status: str = "empty"  # empty|playing|queued|recording|selected
    color: Color = (0.25,0.25,0.25,1.0)

@dataclass
class TrackState:
    name: str = "Track"
    color: Color = (0.0,0.4,1.0,1.0)
    volume: float = 0.8
    pan: float = 0.0
    sends: List[float] = field(default_factory=lambda:[0.0,0.0,0.0])
    mute: bool = False
    solo: bool = False
    arm: bool = False
    clips: Dict[int, ClipSlotState] = field(default_factory=dict)

@dataclass
class TransportState:
    playing: bool = False
    recording: bool = False
    loop: bool = False
    tempo: float = 120.0

@dataclass
class AppStateModel:
    tracks: Dict[int, TrackState] = field(default_factory=dict)
    scenes_count: int = 8
    current_track: int = 0
    transport: TransportState = field(default_factory=TransportState)
from dataclasses import dataclass, field
from typing import Dict, Optional
from enum import Enum

class ClipStatus(Enum):
    EMPTY = "empty"
    PLAYING = "playing"
    QUEUED = "queued"
    RECORDING = "recording"

@dataclass(frozen=True)
class ClipSlotState:
    status: ClipStatus = ClipStatus.EMPTY
    name: str = ""
    color: tuple[float, float, float, float] = (0.25, 0.25, 0.25, 1.0)

    @property
    def is_playing(self) -> bool:
        return self.status == ClipStatus.PLAYING

@dataclass(frozen=True)
class TrackState:
    id: int
    name: str
    clips: Dict[int, ClipSlotState] = field(default_factory=dict)
    volume: float = field(default=0.8)
    pan: float = field(default=0.0)
    sends: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    mute: bool = False
    solo: bool = False
    arm: bool = False

    def __post_init__(self):
        if not 0 <= self.volume <= 1:
            raise ValueError("Volume must be between 0 and 1")

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
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.clock import Clock
from logic.bus import bus
from typing import Dict, List
import logging

class NoteViewScreen(Screen):
    """Note view with mocked Live integration"""
    
    # Live sync properties (mocked)
    current_mode = StringProperty("melodic")
    active_track_id = NumericProperty(1)  # Bass track (instrument)
    active_device_name = StringProperty("Operator")
    device_type = StringProperty("instrument")  # instrument | drum_rack
    
    # Musical state
    current_scale = StringProperty("Minor")
    current_root = StringProperty("C#")
    current_octave = NumericProperty(4)
    playing_pads = ListProperty([])
    
    def __init__(self, app_state=None, **kwargs):
        super().__init__(**kwargs)
        self.app_state = app_state
        self.logger = logging.getLogger(__name__)
        
        # Mock Live data (simulate what we'd get from Live)
        self.mock_live_tracks = {
            0: {"name": "Bass", "device": "Operator", "device_type": "instrument"},  # Melódico
            1: {"name": "Lead", "device": "Serum", "device_type": "instrument"},     # Melódico  
            2: {"name": "Kick", "device": "Drum Rack", "device_type": "drum_rack"},  # Drum
            3: {"name": "Drums", "device": "Drum Rack", "device_type": "drum_rack"}, # Drum
        }
        
        # Static scales (as fallback/mock)
        self.scales = {
            "Major": [0, 2, 4, 5, 7, 9, 11],
            "Minor": [0, 2, 3, 5, 7, 8, 10],
            "Dorian": [0, 2, 3, 5, 7, 9, 10],
            "Phrygian": [0, 1, 3, 5, 7, 8, 10],
            "Lydian": [0, 2, 4, 6, 7, 9, 11],
            "Mixolydian": [0, 2, 4, 5, 7, 9, 10],
            "Blues": [0, 3, 5, 6, 7, 10],
            "Pentatonic": [0, 2, 4, 7, 9]
        }
        
        self.notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        
        # Static drum kit (mock what Live would send)
        self.drum_kit = {
            (0, 0): {"name": "Kick", "note": 36, "color": (0.8, 0.2, 0.2, 1)},
            (0, 1): {"name": "Snare", "note": 38, "color": (1.0, 0.6, 0.0, 1)},
            (0, 2): {"name": "Hi-Hat", "note": 42, "color": (1.0, 1.0, 0.2, 1)},
            (0, 3): {"name": "Open-Hat", "note": 46, "color": (0.6, 1.0, 0.2, 1)},
            (0, 4): {"name": "Crash", "note": 49, "color": (0.2, 0.6, 1.0, 1)},
            (0, 5): {"name": "Ride", "note": 51, "color": (0.6, 0.2, 1.0, 1)},
            (0, 6): {"name": "Clap", "note": 39, "color": (1.0, 0.4, 0.8, 1)},
            (0, 7): {"name": "Perc 1", "note": 60, "color": (0.4, 0.8, 0.8, 1)},
            
            (1, 0): {"name": "Tom Hi", "note": 50, "color": (0.9, 0.3, 0.3, 1)},
            (1, 1): {"name": "Tom Mid", "note": 47, "color": (0.9, 0.5, 0.1, 1)},
            (1, 2): {"name": "Tom Lo", "note": 43, "color": (0.9, 0.7, 0.1, 1)},
            (1, 3): {"name": "Shaker", "note": 70, "color": (0.5, 0.9, 0.1, 1)},
            (1, 4): {"name": "Tamb", "note": 54, "color": (0.1, 0.5, 0.9, 1)},
            (1, 5): {"name": "Cowbell", "note": 56, "color": (0.5, 0.1, 0.9, 1)},
            (1, 6): {"name": "Perc 2", "note": 61, "color": (0.9, 0.3, 0.7, 1)},
            (1, 7): {"name": "Perc 3", "note": 62, "color": (0.3, 0.7, 0.9, 1)},
        }
        
        self._setup_events()
        
        # Mock: Auto-switch mode based on track (simulate Live behavior)
        self._setup_mock_live_behavior()
    
    def _setup_events(self):
        """Setup event handlers (including mock Live events)"""
        # Mock Live events (simulate what OSC/MIDI would send)
        bus.on("mock_live:track_changed", self._on_mock_track_changed)
        bus.on("track:focus", self._on_track_focus_from_clip_view)  # From ClipView
    
    def _setup_mock_live_behavior(self):
        """Setup mock Live behavior for testing"""
        # Simulate Live sending device info when tracks change
        pass
    
    def _on_track_focus_from_clip_view(self, **kwargs):
        """Handle track focus change from Clip View (mock Live integration)"""
        track_id = kwargs.get('track', 0)
        
        # Mock: Change device based on track
        if track_id in self.mock_live_tracks:
            track_info = self.mock_live_tracks[track_id]
            
            self.active_track_id = track_id
            self.active_device_name = track_info["device"]
            self.device_type = track_info["device_type"]
            
            # Auto-switch mode based on device type (mock Live behavior)
            if self.device_type == "drum_rack":
                self.current_mode = "drum"
            else:
                self.current_mode = "melodic"
            
            self._update_pad_grid()
            
            self.logger.info(f"Mock Live: Track {track_id} focused -> {track_info['device']} ({self.current_mode} mode)")
    
    def _on_mock_track_changed(self, **kwargs):
        """Mock handler for Live track changes"""
        track_id = kwargs.get('track_id', 0)
        device_name = kwargs.get('device_name', 'Operator')
        device_type = kwargs.get('device_type', 'instrument')
        
        self.active_track_id = track_id
        self.active_device_name = device_name
        self.device_type = device_type
        
        # Auto-switch mode
        self.current_mode = "drum" if device_type == "drum_rack" else "melodic"
        self._update_pad_grid()
    
    def on_enter(self):
        """Called when screen becomes active"""
        self.logger.info("Entering Note View")
        self._update_pad_grid()
        
        # Mock: Simulate getting current track info from Live
        current_track = self.app_state.m.current_track if self.app_state else 0
        self._on_track_focus_from_clip_view(track=current_track)
    
    def toggle_mode(self):
        """Manual mode toggle (for testing, in real Live this would be automatic)"""
        self.current_mode = "drum" if self.current_mode == "melodic" else "melodic"
        
        # Mock: Update device type accordingly
        self.device_type = "drum_rack" if self.current_mode == "drum" else "instrument"
        self.active_device_name = "Drum Rack" if self.current_mode == "drum" else "Operator"
        
        self._update_pad_grid()
        self.logger.info(f"Manual mode switch: {self.current_mode}")
    
    def cycle_scale(self):
        """Cycle through available scales"""
        scale_names = list(self.scales.keys())
        current_index = scale_names.index(self.current_scale)
        next_index = (current_index + 1) % len(scale_names)
        self.current_scale = scale_names[next_index]
        
        if self.current_mode == "melodic":
            self._update_pad_grid()
    
    def cycle_root(self):
        """Cycle through available root notes"""
        current_index = self.notes.index(self.current_root)
        next_index = (current_index + 1) % len(self.notes)
        self.current_root = self.notes[next_index]
        
        if self.current_mode == "melodic":
            self._update_pad_grid()
    
    def increase_octave(self):
        """Increase octave (max 8)"""
        if self.current_octave < 8:
            self.current_octave += 1
            if self.current_mode == "melodic":
                self._update_pad_grid()
    
    def decrease_octave(self):
        """Decrease octave (min 0)"""
        if self.current_octave > 0:
            self.current_octave -= 1
            if self.current_mode == "melodic":
                self._update_pad_grid()
    
    def _update_pad_grid(self):
        """Update pad grid based on current mode"""
        if self.current_mode == "melodic":
            self._update_melodic_pads()
        elif self.current_mode == "drum":
            self._update_drum_pads()
    
    def _update_melodic_pads(self):
        """Update pads for melodic mode"""
        if not hasattr(self.ids, 'pad_grid'):
            Clock.schedule_once(lambda dt: self._update_pad_grid(), 0.1)
            return
        
        # Get scale notes
        scale_intervals = self.scales.get(self.current_scale, self.scales["Minor"])
        root_note_index = self.notes.index(self.current_root)
        
        # Calculate scale notes in MIDI
        base_midi = (self.current_octave * 12) + root_note_index
        scale_notes = [(base_midi + interval) for interval in scale_intervals]
        
        # Update pads (8x4 grid)
        for row in range(4):
            for col in range(8):
                pad_id = f"pad_{row}_{col}"
                if hasattr(self.ids, pad_id):
                    pad = getattr(self.ids, pad_id)
                    
                    # Calculate note for this pad (chromatic layout)
                    pad_note = base_midi + (row * 8) + col
                    
                    # Check if note is in scale
                    note_in_scale = (pad_note % 12) in [note % 12 for note in scale_notes]
                    
                    # Set pad properties
                    note_name = self.notes[pad_note % 12]
                    octave = pad_note // 12
                    pad.text = f"{note_name}{octave}"
                    
                    # Color based on scale and playing state
                    if pad_note in self.playing_pads:
                        # Bright green when playing
                        pad.background_color = (0.36, 0.89, 0.51, 1)
                    elif note_in_scale:
                        # Gray when in scale
                        pad.background_color = (0.27, 0.27, 0.27, 1)
                    else:
                        # Dark when not in scale
                        pad.background_color = (0.13, 0.13, 0.13, 1)
    
    def _update_drum_pads(self):
        """Update pads for drum mode"""
        if not hasattr(self.ids, 'pad_grid'):
            Clock.schedule_once(lambda dt: self._update_pad_grid(), 0.1)
            return
        
        for row in range(4):
            for col in range(8):
                pad_id = f"pad_{row}_{col}"
                if hasattr(self.ids, pad_id):
                    pad = getattr(self.ids, pad_id)
                    
                    drum_info = self.drum_kit.get((row, col))
                    if drum_info:
                        pad.text = drum_info["name"]
                        
                        if drum_info["note"] in self.playing_pads:
                            # Brighter when playing
                            r, g, b, a = drum_info["color"]
                            pad.background_color = (min(1.0, r + 0.3), min(1.0, g + 0.3), min(1.0, b + 0.3), a)
                        else:
                            pad.background_color = drum_info["color"]
                    else:
                        pad.text = ""
                        pad.background_color = (0.1, 0.1, 0.1, 1)
    
    def on_pad_press(self, row: int, col: int, pad_widget):
        """Handle pad press"""
        if self.current_mode == "melodic":
            self._on_melodic_pad_press(row, col, pad_widget)
        elif self.current_mode == "drum":
            self._on_drum_pad_press(row, col, pad_widget)
    
    def on_pad_release(self, row: int, col: int, pad_widget):
        """Handle pad release"""
        if self.current_mode == "melodic":
            self._on_melodic_pad_release(row, col, pad_widget)
        elif self.current_mode == "drum":
            self._on_drum_pad_release(row, col, pad_widget)
    
    def _on_melodic_pad_press(self, row: int, col: int, pad_widget):
        """Handle melodic pad press"""
        # Calculate MIDI note
        root_note_index = self.notes.index(self.current_root)
        base_midi = (self.current_octave * 12) + root_note_index
        midi_note = base_midi + (row * 8) + col
        
        self.play_note(midi_note)
        
        # Update visual feedback immediately
        pad_widget.background_color = (0.36, 0.89, 0.51, 1)  # Bright green
    
    def _on_melodic_pad_release(self, row: int, col: int, pad_widget):
        """Handle melodic pad release"""
        # Calculate MIDI note
        root_note_index = self.notes.index(self.current_root)
        base_midi = (self.current_octave * 12) + root_note_index
        midi_note = base_midi + (row * 8) + col
        
        self.stop_note(midi_note)
        
        # Update visual feedback
        self._update_pad_grid()
    
    def _on_drum_pad_press(self, row: int, col: int, pad_widget):
        """Handle drum pad press"""
        drum_info = self.drum_kit.get((row, col))
        if drum_info:
            midi_note = drum_info["note"]
            self.play_note(midi_note)
            
            # Bright color when pressed
            r, g, b, a = drum_info["color"]
            pad_widget.background_color = (min(1.0, r + 0.3), min(1.0, g + 0.3), min(1.0, b + 0.3), a)
    
    def _on_drum_pad_release(self, row: int, col: int, pad_widget):
        """Handle drum pad release"""
        drum_info = self.drum_kit.get((row, col))
        if drum_info:
            midi_note = drum_info["note"]
            self.stop_note(midi_note)
            
            # Reset to normal color
            pad_widget.background_color = drum_info["color"]
    
    def play_note(self, midi_note: int, velocity: int = 100):
        """Play note (mock Live integration)"""
        if midi_note not in self.playing_pads:
            self.playing_pads.append(midi_note)
            
            # Mock: Log what would be sent to Live
            self.logger.debug(f"Mock Live: Send Note ON - Track {self.active_track_id}, Note {midi_note}, Vel {velocity}")
            
            # Emit for any other components listening
            bus.emit("note:on", note=midi_note, velocity=velocity, track=self.active_track_id)
    
    def stop_note(self, midi_note: int):
        """Stop note (mock Live integration)"""
        if midi_note in self.playing_pads:
            self.playing_pads.remove(midi_note)
            
            # Mock: Log what would be sent to Live  
            self.logger.debug(f"Mock Live: Send Note OFF - Track {self.active_track_id}, Note {midi_note}")
            
            bus.emit("note:off", note=midi_note, track=self.active_track_id)
    
    # Simulate Live track switching for testing
    def simulate_track_change(self, track_id: int):
        """Simulate Live track change (for testing)"""
        if track_id in self.mock_live_tracks:
            bus.emit("mock_live:track_changed", 
                    track_id=track_id,
                    device_name=self.mock_live_tracks[track_id]["device"],
                    device_type=self.mock_live_tracks[track_id]["device_type"])

from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
from logic.bus import bus
from typing import Optional, Dict, List
import logging

class DevicesViewScreen(Screen):
    """Device control screen with track and device navigation"""
    
    # Track state
    current_track = NumericProperty(0)
    current_track_name = StringProperty("Kick")
    total_tracks = NumericProperty(8)
    
    # Device state
    current_device_name = StringProperty("Kick")
    current_page = NumericProperty(1)
    total_pages = NumericProperty(2)
    auto_switch = BooleanProperty(True)
    active_encoder = NumericProperty(0)
    
    # Device parameters (8 per page)
    device_params = ListProperty([])
    
    def __init__(self, app_state=None, live_integration=None, **kwargs):
        super().__init__(**kwargs)
        self.app_state = app_state
        self.live_integration = live_integration  # AGREGAR ESTO
        self.logger = logging.getLogger(__name__)
        
        # Track names (same as ClipView demo tracks)
        self.track_names = [
            "Kick", "Hats", "Bass", "Tom", "FX", 
            "Pad", "Lead", "Keys", "Perc", "Vocal"
        ]
        
        # Track -> Devices mapping (each track can have multiple devices)
        self.track_devices = {
            0: {  # Kick track
                "Kick": {"pages": 2, "params": [
                    # Page 1
                    {"name": "Pitch", "value": 0.6, "display": "60 Hz", "min": 20, "max": 200, "unit": "Hz"},
                    {"name": "Decay", "value": 0.4, "display": "400ms", "min": 0, "max": 2000, "unit": "ms"},
                    {"name": "Punch", "value": 0.7, "display": "70%", "min": 0, "max": 100, "unit": "%"},
                    {"name": "Drive", "value": 0.3, "display": "30%", "min": 0, "max": 100, "unit": "%"},
                    {"name": "Filter", "value": 0.8, "display": "8kHz", "min": 100, "max": 12000, "unit": "Hz"},
                    {"name": "Res", "value": 0.2, "display": "20%", "min": 0, "max": 100, "unit": "%"},
                    {"name": "Volume", "value": 0.75, "display": "-3dB", "min": -60, "max": 6, "unit": "dB"},
                    {"name": "Pan", "value": 0.5, "display": "C", "min": -100, "max": 100, "unit": ""},
                    # Page 2  
                    {"name": "Attack", "value": 0.1, "display": "1ms", "min": 0, "max": 100, "unit": "ms"},
                    {"name": "Hold", "value": 0.0, "display": "0ms", "min": 0, "max": 500, "unit": "ms"},
                    {"name": "Release", "value": 0.6, "display": "600ms", "min": 0, "max": 2000, "unit": "ms"},
                    {"name": "Vel Sens", "value": 0.8, "display": "80%", "min": 0, "max": 100, "unit": "%"},
                    {"name": "Tube", "value": 0.4, "display": "40%", "min": 0, "max": 100, "unit": "%"},
                    {"name": "Tone", "value": 0.5, "display": "50%", "min": 0, "max": 100, "unit": "%"},
                    {"name": "Send A", "value": 0.2, "display": "20%", "min": 0, "max": 100, "unit": "%"},
                    {"name": "Send B", "value": 0.0, "display": "0%", "min": 0, "max": 100, "unit": "%"},
                ]},
                "EQ": {"pages": 1, "params": [
                    {"name": "Low", "value": 0.5, "display": "0dB", "min": -15, "max": 15, "unit": "dB"},
                    {"name": "Low Mid", "value": 0.5, "display": "0dB", "min": -15, "max": 15, "unit": "dB"},
                    {"name": "Hi Mid", "value": 0.5, "display": "0dB", "min": -15, "max": 15, "unit": "dB"},
                    {"name": "High", "value": 0.5, "display": "0dB", "min": -15, "max": 15, "unit": "dB"},
                    {"name": "Lo Cut", "value": 0.1, "display": "80Hz", "min": 20, "max": 500, "unit": "Hz"},
                    {"name": "Hi Cut", "value": 0.9, "display": "12kHz", "min": 1000, "max": 20000, "unit": "Hz"},
                    {"name": "Gain", "value": 0.6, "display": "3dB", "min": -12, "max": 12, "unit": "dB"},
                    {"name": "Mix", "value": 1.0, "display": "100%", "min": 0, "max": 100, "unit": "%"},
                ]}
            },
            1: {  # Hats track
                "Serum": {"pages": 3, "params": [
                    # Page 1 - Oscillators
                    {"name": "Osc A", "value": 0.8, "display": "Saw", "min": 0, "max": 127, "unit": ""},
                    {"name": "Osc B", "value": 0.3, "display": "Square", "min": 0, "max": 127, "unit": ""},
                    {"name": "Sub", "value": 0.6, "display": "-1 Oct", "min": -24, "max": 24, "unit": "semi"},
                    {"name": "Noise", "value": 0.1, "display": "10%", "min": 0, "max": 100, "unit": "%"},
                    {"name": "Unison", "value": 0.4, "display": "4 Voice", "min": 1, "max": 16, "unit": ""},
                    {"name": "Detune", "value": 0.2, "display": "20¢", "min": 0, "max": 100, "unit": "¢"},
                    {"name": "Phase", "value": 0.0, "display": "0°", "min": 0, "max": 360, "unit": "°"},
                    {"name": "Mix", "value": 0.5, "display": "A=B", "min": 0, "max": 100, "unit": "%"},
                    # Page 2 - Filter
                    {"name": "Cutoff", "value": 0.7, "display": "7kHz", "min": 20, "max": 20000, "unit": "Hz"},
                    {"name": "Reso", "value": 0.3, "display": "30%", "min": 0, "max": 100, "unit": "%"},
                    {"name": "Filter Type", "value": 0.2, "display": "LP24", "min": 0, "max": 10, "unit": ""},
                    {"name": "Env Amt", "value": 0.6, "display": "60%", "min": -100, "max": 100, "unit": "%"},
                    {"name": "Key Track", "value": 0.5, "display": "50%", "min": 0, "max": 100, "unit": "%"},
                    {"name": "Drive", "value": 0.4, "display": "40%", "min": 0, "max": 100, "unit": "%"},
                    {"name": "Fat", "value": 0.3, "display": "30%", "min": 0, "max": 100, "unit": "%"},
                    {"name": "HP", "value": 0.1, "display": "100Hz", "min": 20, "max": 1000, "unit": "Hz"},
                    # Page 3 - Effects & LFO
                    {"name": "LFO Rate", "value": 0.4, "display": "1/4", "min": 0, "max": 100, "unit": ""},
                    {"name": "LFO Amt", "value": 0.6, "display": "60%", "min": 0, "max": 100, "unit": "%"},
                    {"name": "Chorus", "value": 0.2, "display": "20%", "min": 0, "max": 100, "unit": "%"},
                    {"name": "Delay", "value": 0.3, "display": "1/8", "min": 0, "max": 100, "unit": ""},
                    {"name": "Reverb", "value": 0.4, "display": "40%", "min": 0, "max": 100, "unit": "%"},
                    {"name": "Distort", "value": 0.1, "display": "10%", "min": 0, "max": 100, "unit": "%"},
                    {"name": "Master", "value": 0.8, "display": "-2dB", "min": -60, "max": 6, "unit": "dB"},
                    {"name": "Velocity", "value": 0.7, "display": "70%", "min": 0, "max": 100, "unit": "%"},
                ]},
                "Compressor": {"pages": 1, "params": [
                    {"name": "Thresh", "value": 0.3, "display": "-12dB", "min": -40, "max": 0, "unit": "dB"},
                    {"name": "Ratio", "value": 0.6, "display": "4:1", "min": 1, "max": 20, "unit": ":1"},
                    {"name": "Attack", "value": 0.2, "display": "5ms", "min": 0.1, "max": 100, "unit": "ms"},
                    {"name": "Release", "value": 0.4, "display": "100ms", "min": 1, "max": 1000, "unit": "ms"},
                    {"name": "Knee", "value": 0.5, "display": "2dB", "min": 0, "max": 10, "unit": "dB"},
                    {"name": "Makeup", "value": 0.4, "display": "3dB", "min": 0, "max": 20, "unit": "dB"},
                    {"name": "Mix", "value": 1.0, "display": "100%", "min": 0, "max": 100, "unit": "%"},
                    {"name": "Lookahead", "value": 0.3, "display": "3ms", "min": 0, "max": 10, "unit": "ms"},
                ]}
            },
            # Add more tracks...
        }
        
        self._setup_events()
        self._update_track_info()
    
    def _setup_events(self):
        """Setup event handlers for hardware integration"""
        bus.on("encoder:turn", self._on_encoder_turn)
        bus.on("encoder:push", self._on_encoder_push)
        bus.on("device:change", self._on_device_change)
        bus.on("track:focus", self._on_track_focus)
        bus.on("live:track_names", self._on_live_track_names)  # NUEVO
        bus.on("live:devices", self._on_live_devices)  # NUEVO
    
    def on_enter(self):
        """Called when screen becomes active"""
        self._update_current_page_params()
        
        # Auto-focus first encoder
        if hasattr(self.ids, 'knob_grid'):
            self._set_active_encoder(0)
    
    def _update_track_info(self):
        """Update track information and reset to first device"""
        if self.current_track < len(self.track_names):
            self.current_track_name = self.track_names[self.current_track]
        
        # Get devices for current track
        track_devices = self.track_devices.get(self.current_track, {})
        if track_devices:
            # Set first device as current
            first_device = list(track_devices.keys())[0]
            self.current_device_name = first_device
            self.current_page = 1
            self._update_device_info()
            self._update_current_page_params()
    
    def _update_device_info(self):
        """Update device information and pagination"""
        track_devices = self.track_devices.get(self.current_track, {})
        device = track_devices.get(self.current_device_name, {"pages": 1})
        self.total_pages = device["pages"]
        
        # Ensure current page is valid
        if self.current_page > self.total_pages:
            self.current_page = 1
    
    def _update_current_page_params(self):
        """Update parameters for current page"""
        track_devices = self.track_devices.get(self.current_track, {})
        device = track_devices.get(self.current_device_name, {"params": []})
        
        params_per_page = 8
        start_idx = (self.current_page - 1) * params_per_page
        end_idx = start_idx + params_per_page
        
        current_params = device["params"][start_idx:end_idx]
        
        # Update knob widgets
        if hasattr(self, 'ids') and hasattr(self.ids, 'knob_grid'):
            knob_containers = [
                self.ids.knob_row_1.children[::-1],  # Reverse because Kivy adds in reverse
                self.ids.knob_row_2.children[::-1]
            ]
            
            for row_idx, row in enumerate(knob_containers):
                for knob_idx, knob in enumerate(row):
                    param_idx = row_idx * 4 + knob_idx
                    if param_idx < len(current_params):
                        param = current_params[param_idx]
                        knob.param_name = param["name"]
                        knob.display_value = param["display"]
                        knob.knob_value = param["value"]
                        knob.encoder_id = param_idx
    
    def _set_active_encoder(self, encoder_id: int):
        """Set which encoder is currently active (highlighted)"""
        self.active_encoder = encoder_id
        self._update_current_page_params()
    
    def _on_encoder_turn(self, **kwargs):
        """Handle physical encoder rotation"""
        encoder_id = kwargs.get('encoder_id', 0)
        direction = kwargs.get('direction', 0)  # -1 or 1
        
        if 0 <= encoder_id < 8:
            # Auto-switch to this encoder
            if self.auto_switch:
                self._set_active_encoder(encoder_id)
            
            # Update parameter value
            self._adjust_parameter(encoder_id, direction * 0.01)  # 1% increments
    
    def _on_encoder_push(self, **kwargs):
        """Handle encoder push (reset to default or fine adjust mode)"""
        encoder_id = kwargs.get('encoder_id', 0)
        self._set_active_encoder(encoder_id)
        
        # TODO: Implement reset to default or fine adjust mode
        self.logger.info(f"Encoder {encoder_id} pushed - reset parameter")
    
    def _adjust_parameter(self, encoder_id: int, delta: float):
        """Adjust parameter value with bounds checking"""
        track_devices = self.track_devices.get(self.current_track, {})
        device = track_devices.get(self.current_device_name, {"params": []})
        params_per_page = 8
        param_idx = (self.current_page - 1) * params_per_page + encoder_id
        
        if param_idx < len(device["params"]):
            param = device["params"][param_idx]
            new_value = max(0.0, min(1.0, param["value"] + delta))
            param["value"] = new_value
            
            # Update display value
            param["display"] = self._format_parameter_value(param, new_value)
            
            # Update UI
            self._update_current_page_params()
            
            # Emit parameter change event for hardware/DAW sync
            bus.emit("parameter:change", 
                    device=self.current_device_name,
                    param=param["name"],
                    value=new_value,
                    display=param["display"])
    
    def _format_parameter_value(self, param: dict, value: float) -> str:
        """Format parameter value for display"""
        min_val = param["min"]
        max_val = param["max"]
        unit = param["unit"]
        
        # Linear interpolation
        actual_value = min_val + (max_val - min_val) * value
        
        if unit == "Hz":
            if actual_value >= 1000:
                return f"{actual_value/1000:.1f}kHz"
            else:
                return f"{int(actual_value)}Hz"
        elif unit == "ms":
            return f"{int(actual_value)}ms"
        elif unit == "dB":
            if actual_value >= 0:
                return f"+{actual_value:.1f}dB"
            else:
                return f"{actual_value:.1f}dB"
        elif unit == "%":
            return f"{int(actual_value)}%"
        elif unit == "":
            # Special formatting for different parameter types
            if "Pan" in param["name"] and actual_value == 0:
                return "C"
            elif "Pan" in param["name"]:
                side = "L" if actual_value < 0 else "R"
                return f"{int(abs(actual_value))}{side}"
            else:
                return f"{int(actual_value)}"
        else:
            return f"{actual_value:.1f}{unit}"
    
    def previous_device(self):
        """Navigate to previous device IN CURRENT TRACK"""
        track_devices = self.track_devices.get(self.current_track, {})
        device_names = list(track_devices.keys())
        
        if device_names and self.current_device_name in device_names:
            current_idx = device_names.index(self.current_device_name)
            new_idx = (current_idx - 1) % len(device_names)
            self.current_device_name = device_names[new_idx]
            self.current_page = 1  # Reset to first page
            self._update_device_info()
            self._update_current_page_params()
            
            bus.emit("device:change", device=self.current_device_name, track=self.current_track)
    
    def next_device(self):
        """Navigate to next device IN CURRENT TRACK"""
        track_devices = self.track_devices.get(self.current_track, {})
        device_names = list(track_devices.keys())
        
        if device_names and self.current_device_name in device_names:
            current_idx = device_names.index(self.current_device_name)
            new_idx = (current_idx + 1) % len(device_names)
            self.current_device_name = device_names[new_idx]
            self.current_page = 1  # Reset to first page
            self._update_device_info()
            self._update_current_page_params()
            
            bus.emit("device:change", device=self.current_device_name, track=self.current_track)
    
    def previous_page(self):
        """Navigate to previous parameter page"""
        if self.current_page > 1:
            self.current_page -= 1
            self._update_current_page_params()
            self._set_active_encoder(0)  # Reset to first encoder
    
    def next_page(self):
        """Navigate to next parameter page"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._update_current_page_params()
            self._set_active_encoder(0)  # Reset to first encoder
    
    def toggle_auto_switch(self):
        """Toggle auto-switch mode for encoder focus"""
        self.auto_switch = not self.auto_switch
    
    def _on_device_change(self, **kwargs):
        """Handle device change from external source"""
        new_device = kwargs.get('device')
        if new_device and new_device in self.track_devices.get(self.current_track, {}):
            self.current_device_name = new_device
            self.current_page = 1  # Reset to first page
            self._update_device_info()
            self._update_current_page_params()
    
    def _on_track_focus(self, **kwargs):
        """Handle track focus change (auto-load track's main device)"""
        track_id = kwargs.get('track', 0)
        
        # Auto-load device based on track (simplified mapping)
        # This logic needs to be updated to reflect the new track_devices structure
        # For now, it will just set the current_track and update the track name
        self.current_track = track_id
        self._update_track_info()

    def _on_live_track_names(self, **kwargs):
        """Update track names from Live"""
        names = kwargs.get('names', [])
        self.track_names = names[:16]  # Máximo 16 tracks para mostrar
        self.total_tracks = len(self.track_names)
        self.logger.info(f"🎛️ Devices View updated with {len(names)} tracks from Live")
        self._update_track_info()

    def _on_live_devices(self, **kwargs):
        """Update device data from Live"""
        track_id = kwargs.get('track', 0)
        devices = kwargs.get('devices', [])
        
        self.logger.info(f"🎚️ Received devices for track {track_id}: {devices}")
        
        # Update device mapping with real Live data
        if track_id not in self.track_devices:
            self.track_devices[track_id] = {}
        
        for device in devices:
            device_name = device.get('name', 'Unknown Device')
            params = device.get('parameters', [])
            
            # Convert Live device data to our format
            self.track_devices[track_id][device_name] = {
                "pages": max(1, len(params) // 8),
                "params": self._convert_live_params(params)
            }
        
        # Update UI if we're viewing this track
        if self.current_track == track_id:
            self._update_device_info()
            self._update_current_page_params()

    def _convert_live_params(self, live_params):
        """Convert Live parameter format to our internal format"""
        converted = []
        for i, param in enumerate(live_params):
            converted.append({
                "name": param.get('name', f'Param {i+1}'),
                "value": param.get('value', 0.5),
                "display": param.get('display_value', '50%'),
                "min": param.get('min', 0),
                "max": param.get('max', 127),
                "unit": param.get('unit', '')
            })
        return converted

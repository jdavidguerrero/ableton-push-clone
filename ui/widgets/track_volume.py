from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.clock import Clock
from logic.bus import bus  # AGREGAR ESTO
import math

class TrackVolume(BoxLayout):
    track_index = NumericProperty(0)
    track_name  = StringProperty("")  # ADD THIS for real names
    title       = StringProperty("Vol")

    # Estado
    volume  = NumericProperty(0.75)  # 0..1
    pan     = NumericProperty(0.0)   # -1..1
    send_a  = NumericProperty(0.0)   # 0..1
    send_b  = NumericProperty(0.0)
    send_c  = NumericProperty(0.0)

    is_mute = BooleanProperty(False)     # 0/1
    is_solo = BooleanProperty(False)
    is_arm  = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._knob_touch_start_y = 0
        self._knob_start_value = 0
        self._current_knob = None

    def _notify(self, what, value):
        """Emit state changes to bus"""
        bus.emit(f"track:{what}", track=self.track_index, value=value)
        
        # TAMBIÉN enviar directamente a Live si está conectado
        bus.emit(f"mixer:{what}", track=self.track_index, value=value)

    # TOGGLE METHODS for SMA buttons
    def toggle_solo(self):
        """Toggle solo state"""
        self.is_solo = not self.is_solo
        self._notify("solo", self.is_solo)

    def toggle_mute(self):
        """Toggle mute state"""
        self.is_mute = not self.is_mute
        self._notify("mute", self.is_mute)

    def toggle_arm(self):
        """Toggle arm state"""
        self.is_arm = not self.is_arm
        self._notify("arm", self.is_arm)

    # Pan Knob Touch Handlers
    def _on_pan_knob_touch_down(self, touch):
        """Start pan knob interaction"""
        self._knob_touch_start_y = touch.y
        self._knob_start_value = self.pan
        self._current_knob = 'pan'
        return True

    def _on_pan_knob_touch_move(self, touch):
        """Handle pan knob drag"""
        if self._current_knob != 'pan':
            return False
        
        # Calculate change based on vertical movement
        delta_y = touch.y - self._knob_touch_start_y
        sensitivity = 0.005  # Adjust sensitivity
        
        new_value = self._knob_start_value + (delta_y * sensitivity)
        new_value = max(-1.0, min(1.0, new_value))  # Clamp to range
        
        self.pan = new_value
        self._notify("pan", new_value)
        return True

    # Send Knob Touch Handlers
    def _on_send_knob_touch_down(self, touch, send_name):
        """Start send knob interaction"""
        self._knob_touch_start_y = touch.y
        self._current_knob = f'send_{send_name.lower()}'
        
        if send_name == 'A':
            self._knob_start_value = self.send_a
        elif send_name == 'B':
            self._knob_start_value = self.send_b
        elif send_name == 'C':
            self._knob_start_value = self.send_c
        
        return True

    def _on_send_knob_touch_move(self, touch, send_name):
        """Handle send knob drag"""
        if self._current_knob != f'send_{send_name.lower()}':
            return False
        
        # Calculate change based on vertical movement
        delta_y = touch.y - self._knob_touch_start_y
        sensitivity = 0.003  # Slightly less sensitive for sends
        
        new_value = self._knob_start_value + (delta_y * sensitivity)
        new_value = max(0.0, min(1.0, new_value))  # Clamp to 0-1 range
        
        if send_name == 'A':
            self.send_a = new_value
            self._notify("send_a", new_value)
        elif send_name == 'B':
            self.send_b = new_value
            self._notify("send_b", new_value)
        elif send_name == 'C':
            self.send_c = new_value
            self._notify("send_c", new_value)
        
        return True

    # Callbacks simples para KV
    def on_volume(self, *_): self._notify("volume", self.volume)
    def on_pan(self, *_):    self._notify("pan", self.pan)
    def on_send_a(self, *_): self._notify("send_a", self.send_a)
    def on_send_b(self, *_): self._notify("send_b", self.send_b)
    def on_send_c(self, *_): self._notify("send_c", self.send_c)
    def on_is_mute(self, *_): self._notify("mute", self.is_mute)
    def on_is_solo(self, *_): self._notify("solo", self.is_solo)
    def on_is_arm(self, *_):  self._notify("arm", self.is_arm)
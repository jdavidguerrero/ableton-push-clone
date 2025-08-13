


from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty
from logic.bus import bus
import logging
import re

class SettingsViewScreen(Screen):
    """Settings screen for MIDI and OSC configuration"""
    
    # MIDI settings
    midi_channel = NumericProperty(1)  # 1-16
    
    # OSC settings  
    osc_ip = StringProperty("192.168.0.25")
    osc_port = NumericProperty(11000)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(__name__)
    
    def on_enter(self):
        """Called when screen becomes active"""
        self.logger.info("Entering Settings View")
    
    def previous_midi_channel(self):
        """Decrease MIDI channel (1-16)"""
        if self.midi_channel > 1:
            self.midi_channel -= 1
            self.logger.debug(f"MIDI Channel: {self.midi_channel}")
    
    def next_midi_channel(self):
        """Increase MIDI channel (1-16)"""
        if self.midi_channel < 16:
            self.midi_channel += 1
            self.logger.debug(f"MIDI Channel: {self.midi_channel}")
    
    def on_osc_ip_change(self, text_input, text):
        """Handle OSC IP address changes"""
        # Validate IP format (basic validation)
        if self._is_valid_ip(text):
            self.osc_ip = text
            text_input.foreground_color = (0.9, 0.9, 0.9, 1)  # Normal color
            self.logger.debug(f"OSC IP updated: {text}")
        else:
            text_input.foreground_color = (1, 0.4, 0.4, 1)  # Red for invalid
    
    def on_osc_port_change(self, text_input, text):
        """Handle OSC port changes"""
        try:
            port = int(text)
            if 1024 <= port <= 65535:  # Valid port range
                self.osc_port = port
                text_input.foreground_color = (0.9, 0.9, 0.9, 1)  # Normal color
                self.logger.debug(f"OSC Port updated: {port}")
            else:
                text_input.foreground_color = (1, 0.4, 0.4, 1)  # Red for invalid
        except ValueError:
            text_input.foreground_color = (1, 0.4, 0.4, 1)  # Red for invalid
    
    def _is_valid_ip(self, ip):
        """Basic IP address validation"""
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if re.match(pattern, ip):
            parts = ip.split('.')
            return all(0 <= int(part) <= 255 for part in parts)
        return False
    
    def save_settings(self):
        """Save all settings"""
        settings = {
            'midi_channel': self.midi_channel,
            'osc_ip': self.osc_ip,
            'osc_port': self.osc_port
        }
        
        # Emit settings change event
        bus.emit("settings:changed", **settings)
        
        self.logger.info(f"Settings saved: {settings}")
        
        # TODO: Save to config file
        # TODO: Show confirmation message
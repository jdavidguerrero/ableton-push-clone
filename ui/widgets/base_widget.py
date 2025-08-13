# ui/widgets/base_widget.py
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from typing import Optional, Callable
import logging

class BaseWidget(Widget):
    state_manager = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._cleanup_callbacks: list[Callable] = []
        self._setup()
    
    def _setup(self):
        """Override para inicialización específica"""
        pass
    
    def cleanup(self):
        """Limpia recursos y suscripciones"""
        for callback in self._cleanup_callbacks:
            callback()
        self._cleanup_callbacks.clear()

# Ejemplo de uso en TrackVolume
""" class TrackVolume(BaseWidget):
    def __init__(self, track_id: int, **kwargs):
        self.track_id = track_id
        super().__init__(**kwargs)
    
    def _setup(self):
        # Suscribirse a cambios
        unsub = self.state_manager.subscribe(
            'track_volume',
            self._on_volume_change
        )
        self._cleanup_callbacks.append(unsub)
    
    def _on_volume_change(self, data: dict):
        if data['track'] == self.track_id:
            self.volume = data['volume']
 """
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.clock import Clock
from logic.bus import bus
import logging

class ClipSlot(BoxLayout):
    track_index = NumericProperty(0)
    scene_index = NumericProperty(0)
    status      = StringProperty("empty")  # empty|stopped|queued|playing
    label_text  = StringProperty("")
    has_content = BooleanProperty(False)  # NUEVO: indica si el clip tiene contenido

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(__name__)
        # peq. auto-anim/refresh si cambian estados
        Clock.schedule_once(lambda *_: self._apply_status())

    def on_status(self, *_):
        self._apply_status()

    def _apply_status(self):
        # Aquí podrías animar colores o bordes según estado
        pass

    def trigger(self):
        """Trigger this clip slot"""
        # Determinar acción basada en estado actual
        if self.status == "empty":
            # No hacer nada si está vacío
            return
        elif self.status == "playing":
            # Si está reproduciéndose, detenerlo
            bus.emit("clip:stop", track=self.track_index, scene=self.scene_index)
        else:
            # Si está detenido o en queue, reproducirlo
            bus.emit("clip:trigger", track=self.track_index, scene=self.scene_index)
        
        self.logger.debug(f"Clip slot triggered: T{self.track_index}S{self.scene_index}")
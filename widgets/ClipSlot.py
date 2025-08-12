from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock

class ClipSlot(BoxLayout):
    track_index = NumericProperty(0)
    scene_index = NumericProperty(0)
    status      = StringProperty("empty")  # empty|stopped|queued|playing
    label_text  = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # peq. auto-anim/refresh si cambian estados
        Clock.schedule_once(lambda *_: self._apply_status())

    def on_status(self, *_):
        self._apply_status()

    def _apply_status(self):
        # Aquí podrías animar colores o bordes según estado
        pass

    def trigger(self):
        """Lanzar el clip con touch/click."""
        app = None
        try:
            from kivy.app import App
            app = App.get_running_app()
        except Exception:
            pass
        
        # Hook opcional: notificar a tu capa Ableton
        if app and hasattr(app, "state"):
            # Implementa en tu app: app.state.trigger_clip(track, scene)
            try:
                # Change status to show it's been triggered
                self.status = "queued"
                app.state.trigger_clip(self.track_index, self.scene_index)
            except Exception:
                pass
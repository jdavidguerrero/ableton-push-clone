from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.uix.behaviors import ButtonBehavior

class TrackHeader(ButtonBehavior, BoxLayout):
    track_index = NumericProperty(0)
    track_name  = StringProperty("")
    color_rgba  = ListProperty([0.0, 0.016, 1.0, 1.0])

    def on_release(self):
        """Útil para abrir/cambiar la vista de mixer del track."""
        app = None
        try:
            from kivy.app import App
            app = App.get_running_app()
        except Exception:
            pass
        if app and hasattr(app, "state"):
            try:
                app.state.focus_track(self.track_index)
            except Exception:
                pass
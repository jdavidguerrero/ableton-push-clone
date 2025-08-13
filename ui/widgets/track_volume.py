from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.clock import Clock

class TrackVolume(BoxLayout):
    track_index = NumericProperty(0)
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

    def _notify(self, what, value):
        app = None
        try:
            from kivy.app import App
            app = App.get_running_app()
        except Exception:
            return
        if app and hasattr(app, "state"):
            # Implementa estos métodos en tu capa Ableton si quieres control bidireccional
            try:
                if what == "volume":
                    app.state.set_track_volume(self.track_index, float(value))
                elif what == "pan":
                    app.state.set_track_pan(self.track_index, float(value))
                elif what == "send_a":
                    app.state.set_track_send(self.track_index, "A", float(value))
                elif what == "send_b":
                    app.state.set_track_send(self.track_index, "B", float(value))
                elif what == "send_c":
                    app.state.set_track_send(self.track_index, "C", float(value))
                elif what == "mute":
                    app.state.set_track_mute(self.track_index, int(value))
                elif what == "solo":
                    app.state.set_track_solo(self.track_index, int(value))
                elif what == "arm":
                    app.state.set_track_arm(self.track_index, int(value))
            except Exception:
                pass

    # Callbacks simples para KV
    def on_volume(self, *_): self._notify("volume", self.volume)
    def on_pan(self, *_):    self._notify("pan", self.pan)
    def on_send_a(self, *_): self._notify("send_a", self.send_a)
    def on_send_b(self, *_): self._notify("send_b", self.send_b)
    def on_send_c(self, *_): self._notify("send_c", self.send_c)
    def on_is_mute(self, *_): self._notify("mute", self.is_mute)
    def on_is_solo(self, *_): self._notify("solo", self.is_solo)
    def on_is_arm(self, *_):  self._notify("arm", self.is_arm)
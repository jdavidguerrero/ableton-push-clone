from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from widgets.track_channel import TrackChannel

class ClipGrid(BoxLayout):
    """
    Contenedor horizontal de columnas (TrackChannel).
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (None, None)
        self.width = dp(704)  # 8 tracks * 88px each
        self.height = dp(270)
        self.spacing = 0

    def open_mixer_for(self, track_index):
        """Hook opcional si quieres abrir el mixer al tocar un header."""
        app = None
        try:
            from kivy.app import App
            app = App.get_running_app()
        except Exception:
            return
        if app and hasattr(app, "state"):
            try:
                app.state.focus_track(track_index)
            except Exception:
                pass

    def populate_from_ableton(self, tracks):
        self.clear_widgets()
        for t_idx, t in enumerate(tracks):
            # en vez de Factory.TrackChannel(...)
            col = TrackChannel(
                track_index=t_idx,
                track_name=t["name"],
                color_rgba=t["color"],
            )
            # pasa clips al canal para que cree los slots
            col.set_clip_states(t["clips"][:12])
            self.add_widget(col)

        # Calculate width based on number of tracks
        self.width = dp(88) * len(tracks)
        self.height = dp(270)
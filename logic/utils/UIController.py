from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from widgets.track_volume import TrackVolume

class UIController:
    def __init__(self, root_floatlayout):
        self.root = root_floatlayout
        self.current_mixer = None

    def toggle_track_mixer(self, header_widget):
        # Cerrar si ya está abierto para ese track
        if self.current_mixer and self.current_mixer.track_index == header_widget.track_index:
            self.root.remove_widget(self.current_mixer)
            self.current_mixer = None
            return

        # Cerrar el anterior si existe
        if self.current_mixer:
            self.root.remove_widget(self.current_mixer)
            self.current_mixer = None

        # Crear mixer
        m = TrackVolume(track_index=header_widget.track_index,
                        track_name=header_widget.title)
        # Colocar al lado del header (coordenadas absolutas)
        hx, hy = header_widget.to_window(header_widget.x, header_widget.y)
        # Convertir a coords del root
        rx, ry = self.root.to_widget(hx, hy)
        # Posicionar arriba del grid (ajusta offsets según tu layout)
        m.pos = (rx, ry + header_widget.height)
        self.root.add_widget(m)
        self.current_mixer = m
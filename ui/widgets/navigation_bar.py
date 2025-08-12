from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty

class NavigationBar(BoxLayout):
    selected_index = NumericProperty(0)

    def set_active(self, idx):
        self.selected_index = idx
        # activar/desactivar visualmente
        for i, child in enumerate(self.children[::-1]):  # children está invertido
            if hasattr(child, 'active'):
                child.active = (i == idx)

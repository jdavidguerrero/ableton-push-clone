from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import BooleanProperty, ListProperty

class IconButton(ButtonBehavior, Image):
    active = BooleanProperty(False)
    tint_active = ListProperty([1, 1, 1, 1])
    tint_inactive = ListProperty([0.53, 0.53, 0.53, 1])

    # Image.color multiplica la textura → sirve para “tinte”
    def on_active(self, *_):
        pass

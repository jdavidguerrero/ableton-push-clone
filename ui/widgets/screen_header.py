from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty

class ScreenHeader(BoxLayout):
    title = StringProperty("Clip View")
    info  = StringProperty("Scene 1 / Track 1")

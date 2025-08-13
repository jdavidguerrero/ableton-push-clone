from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import StringProperty, ListProperty, BooleanProperty

class NavButton(ButtonBehavior, BoxLayout):
    icon_source = StringProperty("")
    text = StringProperty("")
    active = BooleanProperty(False)

    # More visible colors
    bg_color_active = ListProperty([0.22, 0.84, 0.43, 1])      # Green when active
    bg_color_inactive = ListProperty([0.25, 0.25, 0.25, 1])   # LIGHTER gray when inactive
    text_color_active = ListProperty([1, 1, 1, 1])            # White when active
    text_color_inactive = ListProperty([0.8, 0.8, 0.8, 1])    # LIGHTER gray text when inactive
    icon_tint_active = ListProperty([1, 1, 1, 1])             # White when active
    icon_tint_inactive = ListProperty([0.8, 0.8, 0.8, 1])     # LIGHTER gray when inactive

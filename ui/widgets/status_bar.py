from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty

class StatusBar(BoxLayout):
    bpm_text = StringProperty("BPM: 120")
    track_text = StringProperty("Track 2 - Bass")
    scene_text = StringProperty("Scene 1")

    def on_action(self, action_id):
        print(f"StatusBar action: {action_id}")

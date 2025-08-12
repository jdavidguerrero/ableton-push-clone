from kivy.uix.screenmanager import Screen
from kivy.factory import Factory
from widgets.track_volume import TrackVolume
from kivy.properties import BooleanProperty, StringProperty

class ClipViewScreen(Screen):
    mixer_visible = BooleanProperty(False)
    current_track_text = StringProperty("Track 1 - Kick")
    
    def on_enter(self):
        # Set header info
        header = self.ids.get('screen_header')
        if header:
            header.title = "Clip View"
            header.info = "Scene 1 / Track 1"
        
        demo_tracks = [
            {"name":"Kick", "color":(0,0.016,1,1), "clips":[{"state":"empty", "name":""} for _ in range(12)]},
            {"name":"Hats", "color":(0,1,0.05,1),  "clips":[{"state":"empty", "name":""} for _ in range(12)]},
            {"name":"Bass", "color":(1,0.6,0,1),   "clips":[{"state":"empty", "name":""} for _ in range(12)]},
            {"name":"Tom",  "color":(1,0.85,0,1),  "clips":[{"state":"empty", "name":""} for _ in range(12)]},
            {"name":"FX",   "color":(1,0,0.48,1),  "clips":[{"state":"empty", "name":""} for _ in range(12)]},
            {"name":"Pad",  "color":(0,1,0.97,1),  "clips":[{"state":"empty", "name":""} for _ in range(12)]},
            {"name":"Lead", "color":(1,0.57,0,1),  "clips":[{"state":"empty", "name":""} for _ in range(12)]},
            {"name":"Keys", "color":(0,0.016,1,1), "clips":[{"state":"empty", "name":""} for _ in range(12)]},
        ]
        
        # Add some demo clips with different states to match the image
        demo_tracks[0]["clips"][0] = {"state": "playing", "name": "Kick Loop"}
        demo_tracks[1]["clips"][1] = {"state": "queued", "name": "Hats Pattern"}
        demo_tracks[2]["clips"][2] = {"state": "stopped", "name": "Bass Line"}
        demo_tracks[3]["clips"][0] = {"state": "playing", "name": "Tom Beat"}
        demo_tracks[4]["clips"][1] = {"state": "queued", "name": "FX Sweep"}
        
        self.ids.clip_grid.populate_from_ableton(demo_tracks)

        # Create mixer row with TrackVolume widgets
        mr = self.ids.mixer_row
        mr.clear_widgets()
        for idx, t in enumerate(demo_tracks):
            tv = TrackVolume(
                track_index=idx,
                volume=0.8,
                pan=0.0,
                send_a=0.0,
                send_b=0.0,
                send_c=0.0,
                is_mute=0,
                is_solo=0,
                is_arm=0,
            )
            mr.add_widget(tv)
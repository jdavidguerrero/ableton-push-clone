from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.clock import Clock
from widgets.ClipSlot import ClipSlot

class TrackChannel(BoxLayout):
    track_index = NumericProperty(0)
    track_name  = StringProperty("")
    color_rgba  = ListProperty([0.2, 0.2, 0.2, 1])
    num_scenes  = NumericProperty(12)

    def set_clip_states(self, clips):
        """Rellena/actualiza los ClipSlot con estados de Ableton."""
        self.num_scenes = min(len(clips), 12)

        def _apply(*_):
            slots_box = self.ids.get('slots_box')
            if not slots_box:
                return
            slots_box.clear_widgets()
            for i in range(self.num_scenes):
                info = clips[i] if i < len(clips) else {}
                slot = ClipSlot(
                    track_index=self.track_index,
                    scene_index=i,
                    status=info.get("state", "empty"),
                )
                slot.label_text = info.get("name", f"Clip {i+1}")
                slots_box.add_widget(slot)
        Clock.schedule_once(_apply, 0)
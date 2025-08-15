from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.clock import Clock
from .clip_slot import ClipSlot

class TrackChannel(BoxLayout):
    track_index = NumericProperty(0)
    track_name = StringProperty("")
    color_rgba = ListProperty([0.2, 0.2, 0.2, 1])
    num_scenes = NumericProperty(12)

    def set_clip_states(self, clips):
        """Update clip slots with Ableton states - OPTIMIZED"""
        self.num_scenes = min(len(clips), 12)

        def _apply(*_):
            slots_box = self.ids.get('slots_box')
            if not slots_box:
                return
            
            # OPTIMIZATION: Clear widgets more efficiently
            slots_box.clear_widgets()
            
            # OPTIMIZATION: Create all slots in batch
            new_slots = []
            for i in range(self.num_scenes):
                info = clips[i] if i < len(clips) else {}
                
                slot = ClipSlot(
                    track_index=self.track_index,
                    scene_index=i,
                    status=info.get("state", "empty"),
                    has_content=info.get("has_content", False)
                )
                # Note: No label_text for performance (removed from minimal version)
                new_slots.append(slot)
            
            # Add all slots at once
            for slot in new_slots:
                slots_box.add_widget(slot)
                
        # Use direct call instead of Clock for better performance
        _apply()
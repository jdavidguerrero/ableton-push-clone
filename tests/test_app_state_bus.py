import os
import sys
import pytest
from kivy.clock import Clock

# Ensure project root is on the import path for test execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from logic.state.app_state import AppState
from logic.bus import bus


def test_set_track_volume_emits_named_arguments():
    """AppState should emit track and value as keyword arguments."""
    received = []

    def handler(track, value):
        received.append((track, value))

    bus._subs.clear()
    bus.on("state:track_volume", handler)

    state = AppState()
    state.init_project(tracks=1, scenes=1)
    state.set_track_volume(0, 0.5)

    # Process scheduled bus event
    Clock.tick()

    assert received == [(0, 0.5)]

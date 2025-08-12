from kivy.clock import Clock
class Bus:
    def __init__(self): self._subs = {}
    def on(self, topic, fn): self._subs.setdefault(topic, []).append(fn)
    def emit(self, topic, *args, **kw):
        for fn in self._subs.get(topic, []):
            Clock.schedule_once(lambda dt, fn=fn: fn(*args, **kw), 0)
bus = Bus()
from kivy.clock import Clock
from typing import Dict, List, Callable, Any
from collections import defaultdict
import time

class Bus:
    def __init__(self): self._subs = {}
    def on(self, topic, fn): self._subs.setdefault(topic, []).append(fn)
    def emit(self, topic, *args, **kw):
        for fn in self._subs.get(topic, []):
            Clock.schedule_once(lambda dt, fn=fn: fn(*args, **kw), 0)
bus = Bus()

# logic/fast_bus.py - REEMPLAZO DIRECTO
class FastBus:
    """Ultra-fast event bus without Clock.schedule_once overhead"""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._event_stats = defaultdict(int)
        
    def on(self, event: str, callback: Callable):
        """Subscribe to event - NO Clock scheduling"""
        self._subscribers[event].append(callback)
    
    def emit(self, event: str, **kwargs):
        """Emit event IMMEDIATELY - no scheduling delay"""
        start_time = time.perf_counter()
        
        for callback in self._subscribers[event]:
            try:
                callback(**kwargs)
            except Exception as e:
                print(f"FastBus error in {callback.__name__}: {e}")
        
        # Track performance
        duration = (time.perf_counter() - start_time) * 1000
        self._event_stats[event] += 1
        
        # Log if event takes too long (>5ms is bad for controller)
        if duration > 5.0:
            print(f"⚠️ Slow event {event}: {duration:.2f}ms")
    
    def get_stats(self) -> Dict[str, int]:
        """Get event statistics for monitoring"""
        return dict(self._event_stats)

# Replace global bus
fast_bus = FastBus()
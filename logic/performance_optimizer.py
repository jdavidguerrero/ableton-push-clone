# logic/performance_optimizer.py
import time
from collections import defaultdict
from kivy.clock import Clock
from typing import Dict, Any, List, Callable
import logging

class PerformanceOptimizer:
    """Optimiza el rendimiento de la GUI mediante batching y throttling"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Batching para actualizaciones UI
        self._pending_ui_updates: Dict[str, Any] = {}
        self._ui_update_scheduled = False
        self._batch_delay = 0.05  # 50ms batch window
        
        # Throttling para eventos rápidos
        self._last_event_times: Dict[str, float] = {}
        self._throttle_intervals = {
            'clip_status': 0.1,    # Max 10 updates/sec per clip
            'track_volume': 0.05,  # Max 20 updates/sec per track
            'track_pan': 0.05,
            'clip_name': 0.2,      # Max 5 updates/sec per clip name
        }
        
        # Lazy loading para datos pesados
        self._clip_data_cache: Dict[tuple, Dict] = {}
        self._cache_expiry = 30.0  # Cache expires after 30 seconds
        
    def should_throttle(self, event_type: str, identifier: str) -> bool:
        """Check if event should be throttled"""
        key = f"{event_type}:{identifier}"
        current_time = time.time()
        
        if key in self._last_event_times:
            elapsed = current_time - self._last_event_times[key]
            interval = self._throttle_intervals.get(event_type, 0.1)
            
            if elapsed < interval:
                return True  # Should throttle
        
        self._last_event_times[key] = current_time
        return False
    
    def batch_ui_update(self, update_type: str, data: Dict[str, Any]):
        """Add UI update to batch"""
        self._pending_ui_updates[update_type] = data
        
        if not self._ui_update_scheduled:
            self._ui_update_scheduled = True
            Clock.schedule_once(self._process_batched_updates, self._batch_delay)
    
    def _process_batched_updates(self, dt):
        """Process all batched UI updates at once"""
        if not self._pending_ui_updates:
            self._ui_update_scheduled = False
            return
        
        start_time = time.time()
        updates_processed = 0
        
        # Group similar updates
        clip_updates = []
        track_updates = []
        
        for update_type, data in self._pending_ui_updates.items():
            if 'clip' in update_type:
                clip_updates.append((update_type, data))
            elif 'track' in update_type:
                track_updates.append((update_type, data))
            updates_processed += 1
        
        # Process in batches
        if clip_updates:
            self._process_clip_batch(clip_updates)
        if track_updates:
            self._process_track_batch(track_updates)
        
        # Clear batch
        self._pending_ui_updates.clear()
        self._ui_update_scheduled = False
        
        elapsed = (time.time() - start_time) * 1000
        self.logger.debug(f"⚡ Processed {updates_processed} UI updates in {elapsed:.1f}ms")
    
    def _process_clip_batch(self, clip_updates: List[tuple]):
        """Process batched clip updates efficiently"""
        from logic.bus import bus
        
        # Group by track to minimize widget lookups
        by_track = defaultdict(list)
        for update_type, data in clip_updates:
            track = data.get('track', 0)
            by_track[track].append((update_type, data))
        
        # Emit single batch event per track
        for track, updates in by_track.items():
            bus.emit("ui:clip_batch_update", track=track, updates=updates)
    
    def _process_track_batch(self, track_updates: List[tuple]):
        """Process batched track updates efficiently"""
        from logic.bus import bus
        
        # Merge track data
        merged_data = {}
        for update_type, data in track_updates:
            track = data.get('track', 0)
            if track not in merged_data:
                merged_data[track] = {}
            merged_data[track].update(data)
        
        # Emit single event per track
        for track, data in merged_data.items():
            bus.emit("ui:track_batch_update", track=track, **data)
    
    def cache_clip_data(self, track: int, scene: int, data: Dict):
        """Cache clip data to avoid redundant updates"""
        key = (track, scene)
        current_time = time.time()
        
        self._clip_data_cache[key] = {
            'data': data,
            'timestamp': current_time
        }
    
    def get_cached_clip_data(self, track: int, scene: int) -> Dict:
        """Get cached clip data if still valid"""
        key = (track, scene)
        cached = self._clip_data_cache.get(key)
        
        if cached:
            age = time.time() - cached['timestamp']
            if age < self._cache_expiry:
                return cached['data']
            else:
                # Remove expired cache
                del self._clip_data_cache[key]
        
        return {}
    
    def clear_cache(self):
        """Clear all cached data"""
        self._clip_data_cache.clear()
        self._last_event_times.clear()

# Global instance
performance_optimizer = PerformanceOptimizer()

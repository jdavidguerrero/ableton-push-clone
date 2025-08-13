from typing import Optional
import logging
from .osc_client import OSCClient
from .bus import bus

class LiveIntegration:
    """Integrates OSC communication with the application event bus"""
    
    def __init__(self, app_state=None):
        self.app_state = app_state
        self.osc_client: Optional[OSCClient] = None
        self.logger = logging.getLogger(__name__)
        self.is_syncing = False
        
        self._setup_bus_listeners()
    
    def _setup_bus_listeners(self):
        """Setup event bus listeners for outgoing messages"""
        # Track control
        bus.on("track:volume", self._on_track_volume)
        bus.on("track:pan", self._on_track_pan)
        bus.on("track:mute", self._on_track_mute)
        bus.on("track:solo", self._on_track_solo)
        bus.on("track:arm", self._on_track_arm)
        bus.on("track:send", self._on_track_send)
        
        # Clip control
        bus.on("clip:trigger", self._on_clip_trigger)
        bus.on("clip:stop", self._on_clip_stop)
        bus.on("track:stop", self._on_track_stop)
        
        # Settings changes
        bus.on("settings:changed", self._on_settings_changed)
    
    def connect(self, host: str = "127.0.0.1", send_port: int = 11000, 
                receive_port: int = 11001) -> bool:
        """Connect to Live via OSC"""
        try:
            self.osc_client = OSCClient(host, send_port, receive_port)
            
            # Register handlers for incoming messages
            self._setup_osc_handlers()
            
            # Attempt connection
            if self.osc_client.connect():
                self.logger.info("Connected to Ableton Live")
                
                # Request initial sync
                self._request_initial_sync()
                return True
            else:
                self.logger.error("Failed to connect to Ableton Live")
                return False
                
        except Exception as e:
            self.logger.error(f"Live integration error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Live"""
        if self.osc_client:
            self.osc_client.disconnect()
            self.osc_client = None
        self.logger.info("Disconnected from Ableton Live")
    
    def _setup_osc_handlers(self):
        """Setup OSC message handlers for incoming Live data"""
        if not self.osc_client:
            return
        
        # Track updates from Live
        self.osc_client.register_handler("/push/track/*/volume", self._handle_track_volume)
        self.osc_client.register_handler("/push/track/*/pan", self._handle_track_pan)
        self.osc_client.register_handler("/push/track/*/mute", self._handle_track_mute)
        self.osc_client.register_handler("/push/track/*/solo", self._handle_track_solo)
        self.osc_client.register_handler("/push/track/*/arm", self._handle_track_arm)
        self.osc_client.register_handler("/push/track/*/name", self._handle_track_name)
        
        # Clip updates from Live
        self.osc_client.register_handler("/push/clip/*/*/status", self._handle_clip_status)
        self.osc_client.register_handler("/push/clip/*/*/name", self._handle_clip_name)
        
        # Project info
        self.osc_client.register_handler("/push/tempo", self._handle_tempo)
        self.osc_client.register_handler("/push/sync/complete", self._handle_sync_complete)
    
    def _request_initial_sync(self):
        """Request all data from Live on connection"""
        if self.osc_client:
            self.is_syncing = True
            self.osc_client.request_sync()
            self.logger.info("Requesting initial sync from Live")
    
    # === OUTGOING (Push → Live) ===
    
    def _on_track_volume(self, **kwargs):
        """Handle track volume changes from UI"""
        if self.osc_client and not self.is_syncing:
            track = kwargs.get('track', 0)
            value = kwargs.get('value', 0.0)
            self.osc_client.set_track_volume(track, value)
    
    def _on_track_pan(self, **kwargs):
        """Handle track pan changes from UI"""
        if self.osc_client and not self.is_syncing:
            track = kwargs.get('track', 0)
            value = kwargs.get('value', 0.0)
            self.osc_client.set_track_pan(track, value)
    
    def _on_track_mute(self, **kwargs):
        """Handle track mute changes from UI"""
        if self.osc_client and not self.is_syncing:
            track = kwargs.get('track', 0)
            value = kwargs.get('value', False)
            self.osc_client.set_track_mute(track, bool(value))
    
    def _on_track_solo(self, **kwargs):
        """Handle track solo changes from UI"""
        if self.osc_client and not self.is_syncing:
            track = kwargs.get('track', 0)
            value = kwargs.get('value', False)
            self.osc_client.set_track_solo(track, bool(value))
    
    def _on_track_arm(self, **kwargs):
        """Handle track arm changes from UI"""
        if self.osc_client and not self.is_syncing:
            track = kwargs.get('track', 0)
            value = kwargs.get('value', False)
            self.osc_client.set_track_arm(track, bool(value))
    
    def _on_track_send(self, **kwargs):
        """Handle track send changes from UI"""
        if self.osc_client and not self.is_syncing:
            track = kwargs.get('track', 0)
            send = kwargs.get('send', 'A')
            value = kwargs.get('value', 0.0)
            self.osc_client.set_track_send(track, send, value)
    
    def _on_clip_trigger(self, **kwargs):
        """Handle clip trigger from UI"""
        if self.osc_client:
            track = kwargs.get('track', 0)
            scene = kwargs.get('scene', 0)
            self.osc_client.trigger_clip(track, scene)
    
    def _on_clip_stop(self, **kwargs):
        """Handle clip stop from UI"""
        if self.osc_client:
            track = kwargs.get('track', 0)
            scene = kwargs.get('scene', 0)
            self.osc_client.stop_clip(track, scene)
    
    def _on_track_stop(self, **kwargs):
        """Handle track stop from UI"""
        if self.osc_client:
            track = kwargs.get('track', 0)
            self.osc_client.stop_track(track)
    
    def _on_settings_changed(self, **kwargs):
        """Handle settings changes from UI"""
        # Reconnect with new settings if needed
        osc_ip = kwargs.get('osc_ip')
        osc_port = kwargs.get('osc_port')
        
        if osc_ip and osc_port and self.osc_client:
            self.logger.info(f"Reconnecting to {osc_ip}:{osc_port}")
            self.disconnect()
            self.connect(osc_ip, osc_port, osc_port + 1)
    
    # === INCOMING (Live → Push) ===
    
    def _handle_track_volume(self, address: str, *args):
        """Handle track volume update from Live"""
        parts = address.split('/')
        if len(parts) >= 4 and len(args) > 0:
            track_id = int(parts[3])
            value = float(args[0])
            
            # Update app state without triggering outgoing message
            self.is_syncing = True
            if self.app_state:
                self.app_state.set_track_volume(track_id, value)
            bus.emit("live:track_volume", track=track_id, value=value)
            self.is_syncing = False
    
    def _handle_track_pan(self, address: str, *args):
        """Handle track pan update from Live"""
        parts = address.split('/')
        if len(parts) >= 4 and len(args) > 0:
            track_id = int(parts[3])
            value = float(args[0])
            
            self.is_syncing = True
            if self.app_state:
                self.app_state.set_track_pan(track_id, value)
            bus.emit("live:track_pan", track=track_id, value=value)
            self.is_syncing = False
    
    def _handle_track_mute(self, address: str, *args):
        """Handle track mute update from Live"""
        parts = address.split('/')
        if len(parts) >= 4 and len(args) > 0:
            track_id = int(parts[3])
            value = bool(args[0])
            
            self.is_syncing = True
            if self.app_state:
                self.app_state.set_track_mute(track_id, int(value))
            bus.emit("live:track_mute", track=track_id, value=value)
            self.is_syncing = False
    
    def _handle_track_solo(self, address: str, *args):
        """Handle track solo update from Live"""
        parts = address.split('/')
        if len(parts) >= 4 and len(args) > 0:
            track_id = int(parts[3])
            value = bool(args[0])
            
            self.is_syncing = True
            if self.app_state:
                self.app_state.set_track_solo(track_id, int(value))
            bus.emit("live:track_solo", track=track_id, value=value)
            self.is_syncing = False
    
    def _handle_track_arm(self, address: str, *args):
        """Handle track arm update from Live"""
        parts = address.split('/')
        if len(parts) >= 4 and len(args) > 0:
            track_id = int(parts[3])
            value = bool(args[0])
            
            self.is_syncing = True
            if self.app_state:
                self.app_state.set_track_arm(track_id, int(value))
            bus.emit("live:track_arm", track=track_id, value=value)
            self.is_syncing = False
    
    def _handle_track_name(self, address: str, *args):
        """Handle track name update from Live"""
        parts = address.split('/')
        if len(parts) >= 4 and len(args) > 0:
            track_id = int(parts[3])
            name = str(args[0])
            bus.emit("live:track_name", track=track_id, name=name)
    
    def _handle_clip_status(self, address: str, *args):
        """Handle clip status update from Live"""
        parts = address.split('/')
        if len(parts) >= 5 and len(args) > 0:
            track_id = int(parts[3])
            scene_id = int(parts[4])
            status = str(args[0])
            
            self.is_syncing = True
            if self.app_state:
                self.app_state.set_clip_status(track_id, scene_id, status)
            bus.emit("live:clip_status", track=track_id, scene=scene_id, status=status)
            self.is_syncing = False
    
    def _handle_clip_name(self, address: str, *args):
        """Handle clip name update from Live"""
        parts = address.split('/')
        if len(parts) >= 5 and len(args) > 0:
            track_id = int(parts[3])
            scene_id = int(parts[4])
            name = str(args[0])
            bus.emit("live:clip_name", track=track_id, scene=scene_id, name=name)
    
    def _handle_tempo(self, address: str, *args):
        """Handle tempo update from Live"""
        if len(args) > 0:
            bpm = float(args[0])
            bus.emit("live:tempo", bpm=bpm)
    
    def _handle_sync_complete(self, address: str, *args):
        """Handle sync completion from Live"""
        self.is_syncing = False
        self.logger.info("Live sync completed")
        bus.emit("live:sync_complete")
    
    def get_status(self) -> dict:
        """Get integration status"""
        return {
            "connected": self.osc_client is not None and self.osc_client.is_connected,
            "syncing": self.is_syncing,
            "osc_info": self.osc_client.get_connection_info() if self.osc_client else {}
        }
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
        self.polling_enabled = True  # NUEVO
        
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
        
        # NEW: Mixer control directo
        bus.on("mixer:volume", self._on_mixer_volume)
        bus.on("mixer:pan", self._on_mixer_pan)
        bus.on("mixer:mute", self._on_mixer_mute)
        bus.on("mixer:solo", self._on_mixer_solo)
    
    def connect(self, host: str = "192.168.80.33", send_port: int = 11000, 
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
                
                # Start periodic polling
                self._start_polling()
                
                return True
            else:
                self.logger.error("Failed to connect to Ableton Live")
                return False
                
        except Exception as e:
            self.logger.error(f"Live integration error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Live"""
        self.polling_enabled = False  # Stop polling
        if self.osc_client:
            self.osc_client.disconnect()
            self.osc_client = None
        self.logger.info("Disconnected from Ableton Live")
    
    def _setup_osc_handlers(self):
        """Setup OSC message handlers for incoming Live data"""
        if not self.osc_client:
            return
        
        # Track updates from Live (AbletonOSC format)
        self.osc_client.register_handler("/live/track/get/volume", self._handle_track_volume_response)
        self.osc_client.register_handler("/live/track/get/pan", self._handle_track_pan_response)
        self.osc_client.register_handler("/live/track/get/mute", self._handle_track_mute_response)
        self.osc_client.register_handler("/live/track/get/solo", self._handle_track_solo_response)
        self.osc_client.register_handler("/live/track/get/arm", self._handle_track_arm_response)
        self.osc_client.register_handler("/live/track/get/name", self._handle_track_name_response)
        
        # Clip updates from Live
        self.osc_client.register_handler("/live/clip/get/playing_status", self._handle_clip_status_response)
        self.osc_client.register_handler("/live/clip/get/name", self._handle_clip_name_response)
        self.osc_client.register_handler("/live/clip/get/length", self._handle_clip_length_response)
        self.osc_client.register_handler("/live/clip/get/has_audio_output", self._handle_clip_has_content_response)
        
        # Song-level info
        self.osc_client.register_handler("/live/song/get/tempo", self._handle_tempo_response)
        self.osc_client.register_handler("/live/song/get/track_names", self._handle_track_names_response)
        
        # Live responses
        self.osc_client.register_handler("/live/test", self._handle_live_test)

        # NEW: Listeners para cambios en tiempo real
        self.osc_client.register_handler("/live/song/track_added", self._handle_track_added)
        self.osc_client.register_handler("/live/song/track_removed", self._handle_track_removed)
        self.osc_client.register_handler("/live/song/changed", self._handle_song_changed)

    def _request_initial_sync(self):
        """Request all data from Live on connection"""
        if self.osc_client:
            self.is_syncing = True
            
            # First: Get track names to determine how many tracks exist
            self.osc_client.get_track_names()
            self.osc_client.send_message("/live/song/get/tempo")
            
            # NOTE: Don't request individual track data here
            # We'll do it in _handle_track_names_response once we know the count
            
            self.logger.info("Requesting initial sync from AbletonOSC")

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
            self.logger.info(f"🎵 Triggering clip T{track}S{scene}")
            self.osc_client.trigger_clip(track, scene)
    
    def _on_clip_stop(self, **kwargs):
        """Handle clip stop from UI"""
        if self.osc_client:
            track = kwargs.get('track', 0)
            scene = kwargs.get('scene', 0)
            self.logger.info(f"⏹️ Stopping clip T{track}S{scene}")
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
    
    def _handle_track_names_response(self, address: str, *args):
        """Handle track names response from AbletonOSC"""
        if args:
            track_names = list(args)
            self.logger.info(f"📋 Live has {len(track_names)} tracks: {track_names}")
            bus.emit("live:track_names", names=track_names)
            
            # Initialize app state with real Live tracks
            if self.app_state:
                self.app_state.init_project_from_live(track_names)
            
            # Request data for ALL tracks
            num_tracks = len(track_names)
            for track_id in range(num_tracks):
                # Track data
                self.osc_client.start_listen_track_volume(track_id)
                self.osc_client.send_message(f"/live/track/get/volume", track_id)
                self.osc_client.send_message(f"/live/track/get/name", track_id)
                self.osc_client.send_message(f"/live/track/get/pan", track_id)
                self.osc_client.send_message(f"/live/track/get/mute", track_id)
                self.osc_client.send_message(f"/live/track/get/solo", track_id)
                self.osc_client.send_message(f"/live/track/get/arm", track_id)
                
                # Comentar línea 334:
                # self.osc_client.send_message(f"/live/track/get/color", track_id)
                
                # Devices data
                self.osc_client.send_message(f"/live/track/get/devices", track_id)
                
            self.logger.info(f"✅ Sync complete for {num_tracks} tracks")

    def _handle_live_test(self, address: str, *args):
        """Handle test response from Live"""
        self.logger.info(f"Live test response: {args}")
        bus.emit("live:connection_confirmed")
    
    # === ABLETONOSC RESPONSE HANDLERS ===
    
    def _handle_track_volume_response(self, address: str, *args):
        """Handle track volume response from AbletonOSC"""
        if len(args) >= 2:
            track_id = int(args[0])
            value = float(args[1])
            
            self.is_syncing = True
            if self.app_state:
                self.app_state.set_track_volume(track_id, value)
            bus.emit("live:track_volume", track=track_id, value=value)
            self.is_syncing = False
            self.logger.debug(f"Live volume: Track {track_id} = {value:.2f}")
    
    def _handle_track_pan_response(self, address: str, *args):
        """Handle track pan response from AbletonOSC"""
        if len(args) >= 2:
            track_id = int(args[0])
            value = float(args[1])
            
            self.is_syncing = True
            if self.app_state:
                self.app_state.set_track_pan(track_id, value)
            bus.emit("live:track_pan", track=track_id, value=value)
            self.is_syncing = False
    
    def _handle_track_mute_response(self, address: str, *args):
        """Handle track mute response from AbletonOSC"""
        if len(args) >= 2:
            track_id = int(args[0])
            value = bool(args[1])
            
            self.is_syncing = True
            if self.app_state:
                self.app_state.set_track_mute(track_id, int(value))
            bus.emit("live:track_mute", track=track_id, value=value)
            self.is_syncing = False
    
    def _handle_track_solo_response(self, address: str, *args):
        """Handle track solo response from AbletonOSC"""
        if len(args) >= 2:
            track_id = int(args[0])
            value = bool(args[1])
            
            self.is_syncing = True
            if self.app_state:
                self.app_state.set_track_solo(track_id, int(value))
            bus.emit("live:track_solo", track=track_id, value=value)
            self.is_syncing = False
    
    def _handle_track_arm_response(self, address: str, *args):
        """Handle track arm response from AbletonOSC"""
        if len(args) >= 2:
            track_id = int(args[0])
            value = bool(args[1])
            
            self.is_syncing = True
            if self.app_state:
                self.app_state.set_track_arm(track_id, int(value))
            bus.emit("live:track_arm", track=track_id, value=value)
            self.is_syncing = False
    
    def _handle_track_name_response(self, address: str, *args):
        """Handle track name response from AbletonOSC"""
        if len(args) >= 2:
            track_id = int(args[0])
            name = str(args[1])
            bus.emit("live:track_name", track=track_id, name=name)
            self.logger.debug(f"Live track name: Track {track_id} = '{name}'")
    
    def _handle_clip_status_response(self, address: str, *args):
        """Handle clip status response from AbletonOSC"""
        if len(args) >= 3:
            track_id = int(args[0])
            scene_id = int(args[1])
            status = str(args[2])
            
            self.is_syncing = True
            if self.app_state:
                self.app_state.set_clip_status(track_id, scene_id, status)
            bus.emit("live:clip_status", track=track_id, scene=scene_id, status=status)
            self.is_syncing = False
    
    def _handle_clip_name_response(self, address: str, *args):
        """Handle clip name response from AbletonOSC"""
        if len(args) >= 3:
            track_id = int(args[0])
            scene_id = int(args[1])
            name = str(args[2])
            bus.emit("live:clip_name", track=track_id, scene=scene_id, name=name)
    
    def _handle_clip_length_response(self, address: str, *args):
        """Handle clip length response from AbletonOSC"""
        if len(args) >= 3:
            track_id = int(args[0])
            scene_id = int(args[1])
            length = float(args[2]) if args[2] != -1 else 0  # -1 means no clip
            
            has_content = length > 0
            bus.emit("live:clip_has_content", track=track_id, scene=scene_id, has_content=has_content, length=length)

    def _handle_clip_has_content_response(self, address: str, *args):
        """Handle clip has_audio_output response from AbletonOSC"""
        if len(args) >= 3:
            track_id = int(args[0])
            scene_id = int(args[1])
            has_content = bool(args[2])
            
            bus.emit("live:clip_has_content", track=track_id, scene=scene_id, has_content=has_content)
    
    def _handle_tempo_response(self, address: str, *args):
        """Handle tempo response from AbletonOSC"""
        if len(args) > 0:
            bpm = float(args[0])
            bus.emit("live:tempo", bpm=bpm)
            self.logger.debug(f"Live tempo: {bpm} BPM")
    
    def _handle_track_names_response(self, address: str, *args):
        """Handle track names response from AbletonOSC"""
        if args:
            track_names = list(args)
            self.logger.info(f"Live track names: {track_names}")
            bus.emit("live:track_names", names=track_names)
    
    def _handle_live_test(self, address: str, *args):
        """Handle test response from Live"""
        self.logger.info(f"✅ Live test response: {args}")
        bus.emit("live:connection_confirmed")
    
    def _handle_track_color_response(self, address: str, *args):
        """Handle track color response from AbletonOSC"""
        if len(args) >= 2:
            track_id = int(args[0])
            color_value = args[1]  # Puede ser RGB o índice de color
            
            # Convertir color de Live a RGBA
            rgba_color = self._convert_live_color(color_value)
            
            bus.emit("live:track_color", track=track_id, color=rgba_color)
            self.logger.debug(f"Live track color: Track {track_id} = {rgba_color}")

    def _handle_track_added(self, address: str, *args):
        """Handle when a track is added in Live"""
        self.logger.info("🆕 Track added in Live - refreshing...")
        self._request_full_resync()

    def _handle_track_removed(self, address: str, *args):
        """Handle when a track is removed in Live"""
        self.logger.info("🗑️ Track removed in Live - refreshing...")
        self._request_full_resync()

    def _handle_song_changed(self, address: str, *args):
        """Handle general song structure changes"""
        self.logger.info("🔄 Song structure changed in Live - refreshing...")
        self._request_full_resync()

    def _request_full_resync(self):
        """Request a complete resync from Live"""
        if self.osc_client:
            self.logger.info("📡 Requesting full resync...")
            self.is_syncing = True
            
            # Re-request track names (will trigger UI update)
            self.osc_client.get_track_names()
            
            # Emit event so UI screens can refresh
            bus.emit("live:structure_changed")
    
    def get_status(self) -> dict:
        """Get integration status"""
        return {
            "connected": self.osc_client is not None and self.osc_client.is_connected,
            "syncing": self.is_syncing,
            "osc_info": self.osc_client.get_connection_info() if self.osc_client else {}
        }

    def _start_polling(self):
        """Start periodic polling for changes"""
        import threading
        import time
        
        def poll_loop():
            while self.polling_enabled and self.osc_client and self.osc_client.is_connected:
                try:
                    # Poll track names every 5 seconds
                    self.osc_client.get_track_names()
                    time.sleep(5.0)
                except Exception as e:
                    self.logger.error(f"Polling error: {e}")
                    break
        
        polling_thread = threading.Thread(target=poll_loop, daemon=True)
        polling_thread.start()

    def _convert_live_color(self, live_color):
        """Convert Live color format to RGBA"""
        if isinstance(live_color, (list, tuple)) and len(live_color) >= 3:
            # Si Live envía RGB directamente
            r, g, b = live_color[:3]
            return (r/255.0, g/255.0, b/255.0, 1.0)
        elif isinstance(live_color, int):
            # Si Live envía índice de color, usar paleta de colores
            live_colors = [
                (1.0, 0.3, 0.3, 1.0),    # Rojo
                (1.0, 0.6, 0.0, 1.0),    # Naranja
                (1.0, 1.0, 0.0, 1.0),    # Amarillo
                (0.5, 1.0, 0.0, 1.0),    # Verde claro
                (0.0, 1.0, 0.0, 1.0),    # Verde
                (0.0, 1.0, 0.5, 1.0),    # Verde agua
                (0.0, 1.0, 1.0, 1.0),    # Cyan
                (0.0, 0.5, 1.0, 1.0),    # Azul claro
                (0.0, 0.0, 1.0, 1.0),    # Azul
                (0.5, 0.0, 1.0, 1.0),    # Púrpura
                (1.0, 0.0, 1.0, 1.0),    # Magenta
                (1.0, 0.0, 0.5, 1.0),    # Rosa
            ]
            return live_colors[live_color % len(live_colors)]
        else:
            # Color por defecto
            return (0.5, 0.5, 0.5, 1.0)

    def _on_mixer_volume(self, **kwargs):
        """Handle mixer volume changes (same as track volume)"""
        self._on_track_volume(**kwargs)

    def _on_mixer_pan(self, **kwargs):
        """Handle mixer pan changes (same as track pan)"""
        self._on_track_pan(**kwargs)

    def _on_mixer_mute(self, **kwargs):
        """Handle mixer mute changes (same as track mute)"""
        self._on_track_mute(**kwargs)

    def _on_mixer_solo(self, **kwargs):
        """Handle mixer solo changes (same as track solo)"""
        self._on_track_solo(**kwargs)
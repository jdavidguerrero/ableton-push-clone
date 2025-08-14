import threading
import logging
from typing import Callable, Dict, Any, Optional, Tuple
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import time
import socket

class OSCClient:
    """OSC Client for bidirectional communication with Ableton Live"""
    
    def __init__(self, send_host: str = "192.168.80.33", send_port: int = 11000, 
                 receive_port: int = 11001):
        self.send_host = send_host
        self.send_port = send_port
        self.receive_port = receive_port
        
        self.logger = logging.getLogger(__name__)
        
        # OSC Client for sending messages (Push → Live)
        self.client: Optional[SimpleUDPClient] = None
        
        # OSC Server for receiving messages (Live → Push)  
        self.server: Optional[BlockingOSCUDPServer] = None
        self.server_thread: Optional[threading.Thread] = None
        self.dispatcher = Dispatcher()
        
        # Connection state
        self.is_connected = False
        self.is_server_running = False
        self._shutdown_event = threading.Event()  # MEJORADO: Para shutdown limpio
        
        # Message handlers
        self.handlers: Dict[str, Callable] = {}
        
        # Statistics
        self.messages_sent = 0
        self.messages_received = 0
        self.last_message_time = 0
        self.connection_attempts = 0  # NUEVO: Track intentos de conexión
        
        # NUEVO: Connection monitoring
        self.last_ping_time = 0
        self.ping_interval = 5.0  # Ping cada 5 segundos
        self.ping_timeout = 10.0  # Timeout si no hay respuesta en 10s
        
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Setup default OSC message handlers"""
        # Heartbeat/connection monitoring
        self.register_handler("/push/pong", self._handle_pong)  # CORREGIDO: Era /live/ping
        self.register_handler("/push/status", self._handle_status)  # CORREGIDO: Era /live/status
        
        # Error handling
        self.dispatcher.set_default_handler(self._handle_unknown_message)
    
    def connect(self) -> bool:
        """Establish connection to Live"""
        self.connection_attempts += 1
        
        try:
            # MEJORADO: Verificar si el puerto está disponible antes de crear el servidor
            if not self._is_port_available(self.receive_port):
                raise Exception(f"Port {self.receive_port} is already in use")
            
            # Create UDP client for sending
            self.client = SimpleUDPClient(self.send_host, self.send_port)
            
            # Start server for receiving
            self._start_server()
            
            # Wait a bit for server to start
            time.sleep(0.1)
            
            # Test connection with ping
            self.send_message("/live/ping", "hello")
            
            self.is_connected = True
            self.last_ping_time = time.time()
            self.logger.info(f"OSC Client connected: {self.send_host}:{self.send_port} → {self.receive_port}")
            
            # NUEVO: Start connection monitoring
            self._start_ping_monitor()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect OSC Client (attempt {self.connection_attempts}): {e}")
            self.is_connected = False
            self._cleanup()
            return False
    
    def _is_port_available(self, port: int) -> bool:
        """Check if a port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.bind(('127.0.0.1', port))
                return True
        except OSError:
            return False
    
    def disconnect(self):
        """Close OSC connection"""
        self.logger.info("Disconnecting OSC Client...")
        self.is_connected = False
        self._shutdown_event.set()
        
        self._cleanup()
        
        self.logger.info("OSC Client disconnected")
    
    def _cleanup(self):
        """Clean up resources"""
        # Stop server
        if self.server:
            try:
                self.server.shutdown()
            except:
                pass
            self.is_server_running = False
        
        # Wait for thread to finish
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=2.0)
            if self.server_thread.is_alive():
                self.logger.warning("OSC server thread did not shutdown cleanly")
        
        # Reset state
        self.client = None
        self.server = None
        self.server_thread = None
    
    def _start_server(self):
        """Start OSC server in background thread"""
        try:
            self.server = BlockingOSCUDPServer(("0.0.0.0", self.receive_port), self.dispatcher)
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            self.is_server_running = True
            self.logger.info(f"OSC Server listening on all interfaces, port {self.receive_port}")
        except Exception as e:
            self.logger.error(f"Failed to start OSC server: {e}")
            raise
    
    def _run_server(self):
        """Server main loop (runs in background thread)"""
        try:
            # MEJORADO: Server loop con shutdown event
            while not self._shutdown_event.is_set() and self.is_server_running:
                try:
                    self.server.handle_request()  # Non-blocking con timeout
                except OSError as e:
                    if self.is_server_running:  # Solo log si no es shutdown intencional
                        self.logger.debug(f"OSC Server handle_request error: {e}")
                        break
        except Exception as e:
            if self.is_server_running:  # Only log if unexpected shutdown
                self.logger.error(f"OSC Server error: {e}")
        finally:
            self.logger.debug("OSC Server thread exiting")
    
    def _start_ping_monitor(self):
        """Start background ping monitoring"""
        def ping_monitor():
            while self.is_connected and not self._shutdown_event.is_set():
                current_time = time.time()
                
                # Send ping every ping_interval seconds
                if current_time - self.last_ping_time > self.ping_interval:
                    self.send_message("/live/ping", "heartbeat")
                    self.last_ping_time = current_time
                
                # Check for ping timeout
                if current_time - self.last_ping_time > self.ping_timeout:
                    self.logger.warning("OSC connection timeout - no ping response")
                    # Optionally auto-reconnect here
                
                time.sleep(1.0)  # Check every second
        
        ping_thread = threading.Thread(target=ping_monitor, daemon=True)
        ping_thread.start()
    
    def send_message(self, address: str, *args) -> bool:
        """Send OSC message to Live"""
        if not self.is_connected or not self.client:
            self.logger.warning(f"Cannot send OSC message - not connected: {address}")
            return False
        
        try:
            # MEJORADO: Handle single args vs multiple args correctly
            if len(args) == 1 and not isinstance(args[0], (list, tuple)):
                self.client.send_message(address, args[0])
            else:
                self.client.send_message(address, list(args) if args else [])
            
            self.messages_sent += 1
            self.last_message_time = time.time()
            
            self.logger.debug(f"OSC Sent: {address} {args}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send OSC message {address}: {e}")
            return False
    
    def register_handler(self, pattern: str, handler: Callable):
        """Register handler for incoming OSC messages"""
        self.handlers[pattern] = handler
        self.dispatcher.map(pattern, self._wrap_handler(pattern, handler))
        self.logger.debug(f"Registered OSC handler: {pattern}")
    
    def _wrap_handler(self, pattern: str, handler: Callable):
        """Wrap handler with error handling and logging"""
        def wrapped_handler(address: str, *args):
            try:
                self.messages_received += 1
                self.logger.debug(f"OSC Received: {address} {args}")
                handler(address, *args)
            except Exception as e:
                self.logger.error(f"Error in OSC handler {pattern}: {e}")
        return wrapped_handler
    
    def _handle_pong(self, address: str, *args):
        """Handle pong messages (connection test)"""
        self.last_ping_time = time.time()  # NUEVO: Update ping time
        self.logger.debug(f"Received pong: {args}")
    
    def _handle_status(self, address: str, *args):
        """Handle status messages from Live"""
        if args:
            status = args[0]
            self.logger.info(f"Live status: {status}")
    
    def _handle_unknown_message(self, address: str, *args):
        """Handle unknown/unmapped OSC messages"""
        self.logger.debug(f"Unknown OSC message: {address} {args}")
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection status and statistics"""
        current_time = time.time()
        return {
            "connected": self.is_connected,
            "server_running": self.is_server_running,
            "send_endpoint": f"{self.send_host}:{self.send_port}",
            "receive_port": self.receive_port,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "last_message_time": self.last_message_time,
            "last_ping_time": self.last_ping_time,
            "ping_age": current_time - self.last_ping_time if self.last_ping_time > 0 else 0,
            "connection_attempts": self.connection_attempts,
            "handlers_count": len(self.handlers)
        }
    
    def is_alive(self) -> bool:
        """Check if connection is alive based on recent ping"""
        if not self.is_connected:
            return False
        
        current_time = time.time()
        return (current_time - self.last_ping_time) < self.ping_timeout
    
    # === CONVENIENCE METHODS FOR LIVE CONTROL ===
    # (Los métodos existentes están bien, solo algunas mejoras menores)
    
    def set_track_volume(self, track_id: int, value: float):
        """Set track volume (0.0 - 1.0)"""
        value = max(0.0, min(1.0, value))  # MEJORADO: Clamp value
        return self.send_message(f"/live/track/{track_id}/volume", value)
    
    def set_track_pan(self, track_id: int, value: float):
        """Set track pan (-1.0 - 1.0)"""
        value = max(-1.0, min(1.0, value))  # MEJORADO: Clamp value
        return self.send_message(f"/live/track/{track_id}/pan", value)
    
    def set_track_mute(self, track_id: int, muted: bool):
        """Set track mute state"""
        return self.send_message(f"/live/track/{track_id}/mute", 1 if muted else 0)
    
    def set_track_solo(self, track_id: int, soloed: bool):
        """Set track solo state"""
        return self.send_message(f"/live/track/{track_id}/solo", 1 if soloed else 0)
    
    def set_track_arm(self, track_id: int, armed: bool):
        """Set track arm state"""
        return self.send_message(f"/live/track/{track_id}/arm", 1 if armed else 0)
    
    def set_track_send(self, track_id: int, send_id: str, value: float):
        """Set track send level (A, B, C)"""
        value = max(0.0, min(1.0, value))  # MEJORADO: Clamp value
        return self.send_message(f"/live/track/{track_id}/send/{send_id.lower()}", value)
    
    def trigger_clip(self, track_id: int, scene_id: int):
        """Trigger clip"""
        return self.send_message(f"/live/clip/{track_id}/{scene_id}/trigger")
    
    def stop_clip(self, track_id: int, scene_id: int):
        """Stop clip"""
        return self.send_message(f"/live/clip/{track_id}/{scene_id}/stop")
    
    def stop_track(self, track_id: int):
        """Stop all clips on track"""
        return self.send_message(f"/live/track/{track_id}/stop")
    
    def launch_scene(self, scene_id: int):
        """Launch scene"""
        return self.send_message(f"/live/scene/{scene_id}/launch")
    
    def request_sync(self):
        """Request full sync from Live"""
        return self.send_message("/live/sync/request")
    
    def set_tempo(self, bpm: float):
        """Set Live tempo"""
        bpm = max(20.0, min(999.0, bpm))  # MEJORADO: Clamp BPM
        return self.send_message("/live/tempo", bpm)
    
    def play(self):
        """Start Live playback"""
        return self.send_message("/live/play")
    
    def stop(self):
        """Stop Live playback"""
        return self.send_message("/live/stop")
    
    def record(self):
        """Start Live recording"""
        return self.send_message("/live/record")

    # === ABLETONOSC SPECIFIC METHODS ===
    
    def get_track_names(self):
        """Get all track names"""
        return self.send_message("/live/song/get/track_names")
    
    def get_scene_names(self):
        """Get all scene names"""
        return self.send_message("/live/song/get/scene_names")
    
    def get_track_devices(self, track_id: int):
        """Get devices for a track"""
        return self.send_message(f"/live/track/get/devices", track_id)
    
    def get_device_parameters(self, track_id: int, device_id: int):
        """Get device parameters"""
        return self.send_message(f"/live/device/get/parameters/name", track_id, device_id)
    
    def set_device_parameter(self, track_id: int, device_id: int, param_id: int, value: float):
        """Set device parameter value"""
        return self.send_message(f"/live/device/set/parameter/value", track_id, device_id, param_id, value)
    
    def get_clip_info(self, track_id: int, scene_id: int):
        """Get clip information"""
        return self.send_message(f"/live/clip/get/*", track_id, scene_id)
    
    def send_midi_note(self, track_id: int, note: int, velocity: int = 100):
        """Send MIDI note to track"""
        return self.send_message(f"/live/track/send/midi", track_id, note, velocity)
    
    def start_listen_track_volume(self, track_id: int):
        """Start listening for track volume changes"""
        return self.send_message(f"/live/track/start_listen/volume", track_id)
    
    def start_listen_clip_status(self, track_id: int, scene_id: int):
        """Start listening for clip status changes"""
        return self.send_message(f"/live/clip/start_listen/playing_status", track_id, scene_id)

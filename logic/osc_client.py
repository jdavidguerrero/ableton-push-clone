import threading
import logging
from typing import Callable, Dict, Any, Optional, Tuple
from pythonosc import osc
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.server import BlockingOSCUDPServer
import time

class OSCClient:
    """OSC Client for bidirectional communication with Ableton Live"""
    
    def __init__(self, send_host: str = "127.0.0.1", send_port: int = 11000, 
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
        
        # Message handlers
        self.handlers: Dict[str, Callable] = {}
        
        # Statistics
        self.messages_sent = 0
        self.messages_received = 0
        self.last_message_time = 0
        
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Setup default OSC message handlers"""
        # Heartbeat/connection monitoring
        self.register_handler("/live/ping", self._handle_ping)
        self.register_handler("/live/status", self._handle_status)
        
        # Error handling
        self.dispatcher.set_default_handler(self._handle_unknown_message)
    
    def connect(self) -> bool:
        """Establish connection to Live"""
        try:
            # Create UDP client for sending
            self.client = SimpleUDPClient(self.send_host, self.send_port)
            
            # Start server for receiving
            self._start_server()
            
            # Test connection with ping
            self.send_message("/live/ping", "hello")
            
            self.is_connected = True
            self.logger.info(f"OSC Client connected: {self.send_host}:{self.send_port} → {self.receive_port}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect OSC Client: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Close OSC connection"""
        self.is_connected = False
        
        if self.server:
            self.server.shutdown()
            self.is_server_running = False
        
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=2.0)
        
        self.client = None
        self.server = None
        self.server_thread = None
        
        self.logger.info("OSC Client disconnected")
    
    def _start_server(self):
        """Start OSC server in background thread"""
        try:
            self.server = BlockingOSCUDPServer(("127.0.0.1", self.receive_port), self.dispatcher)
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            self.is_server_running = True
            self.logger.info(f"OSC Server listening on port {self.receive_port}")
        except Exception as e:
            self.logger.error(f"Failed to start OSC server: {e}")
            raise
    
    def _run_server(self):
        """Server main loop (runs in background thread)"""
        try:
            self.server.serve_forever()
        except Exception as e:
            if self.is_server_running:  # Only log if unexpected shutdown
                self.logger.error(f"OSC Server error: {e}")
    
    def send_message(self, address: str, *args) -> bool:
        """Send OSC message to Live"""
        if not self.is_connected or not self.client:
            self.logger.warning(f"Cannot send OSC message - not connected: {address}")
            return False
        
        try:
            self.client.send_message(address, args if args else [])
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
    
    def _handle_ping(self, address: str, *args):
        """Handle ping messages (connection test)"""
        self.logger.debug(f"Received ping: {args}")
        # Respond with pong
        self.send_message("/push/pong", "hello")
    
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
        return {
            "connected": self.is_connected,
            "server_running": self.is_server_running,
            "send_endpoint": f"{self.send_host}:{self.send_port}",
            "receive_port": self.receive_port,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "last_message_time": self.last_message_time,
            "handlers_count": len(self.handlers)
        }
    
    # === CONVENIENCE METHODS FOR LIVE CONTROL ===
    
    def set_track_volume(self, track_id: int, value: float):
        """Set track volume (0.0 - 1.0)"""
        self.send_message(f"/live/track/{track_id}/volume", value)
    
    def set_track_pan(self, track_id: int, value: float):
        """Set track pan (-1.0 - 1.0)"""
        self.send_message(f"/live/track/{track_id}/pan", value)
    
    def set_track_mute(self, track_id: int, muted: bool):
        """Set track mute state"""
        self.send_message(f"/live/track/{track_id}/mute", 1 if muted else 0)
    
    def set_track_solo(self, track_id: int, soloed: bool):
        """Set track solo state"""
        self.send_message(f"/live/track/{track_id}/solo", 1 if soloed else 0)
    
    def set_track_arm(self, track_id: int, armed: bool):
        """Set track arm state"""
        self.send_message(f"/live/track/{track_id}/arm", 1 if armed else 0)
    
    def set_track_send(self, track_id: int, send_id: str, value: float):
        """Set track send level (A, B, C)"""
        self.send_message(f"/live/track/{track_id}/send/{send_id.lower()}", value)
    
    def trigger_clip(self, track_id: int, scene_id: int):
        """Trigger clip"""
        self.send_message(f"/live/clip/{track_id}/{scene_id}/trigger")
    
    def stop_clip(self, track_id: int, scene_id: int):
        """Stop clip"""
        self.send_message(f"/live/clip/{track_id}/{scene_id}/stop")
    
    def stop_track(self, track_id: int):
        """Stop all clips on track"""
        self.send_message(f"/live/track/{track_id}/stop")
    
    def launch_scene(self, scene_id: int):
        """Launch scene"""
        self.send_message(f"/live/scene/{scene_id}/launch")
    
    def request_sync(self):
        """Request full sync from Live"""
        self.send_message("/live/sync/request")
    
    def set_tempo(self, bpm: float):
        """Set Live tempo"""
        self.send_message("/live/tempo", bpm)
    
    def play(self):
        """Start Live playback"""
        self.send_message("/live/play")
    
    def stop(self):
        """Stop Live playback"""
        self.send_message("/live/stop")
    
    def record(self):
        """Start Live recording"""
        self.send_message("/live/record")

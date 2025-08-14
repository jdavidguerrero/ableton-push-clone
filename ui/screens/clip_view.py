from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty
from logic.bus import bus
from typing import Optional
import logging

class ClipViewScreen(Screen):
    
    # Track state
    focused_track = NumericProperty(0)
    current_track_text = StringProperty("Kick")
    
    def __init__(self, app_state=None, clip_manager=None, live_integration=None, **kwargs):
        super().__init__(**kwargs)
        self.app_state = app_state
        self.clip_manager = clip_manager
        self.live_integration = live_integration  # NUEVO: Integración real
        self.logger = logging.getLogger(__name__)
        
        # Datos de Live (reemplazan demo_tracks)
        self.live_tracks = []
        self.live_scenes = []
        
        # Setup event listeners
        self._setup_events()
    
    def _setup_events(self):
        """Setup event bus listeners"""
        bus.on("track:focus", self._on_track_focus)
        bus.on("clip:changed", self._on_clip_changed)
        
        # Live data listeners
        bus.on("live:track_names", self._on_live_track_names)
        bus.on("live:clip_status", self._on_live_clip_status)
        bus.on("live:clip_name", self._on_live_clip_name)  # NEW
        bus.on("live:track_color", self._on_live_track_color)  # NEW
        bus.on("live:connection_confirmed", self._on_live_connected)
        bus.on("live:structure_changed", self._on_structure_changed)
        bus.on("live:clip_has_content", self._on_live_clip_has_content)  # NEW
    
    def on_enter(self):
        """Called when screen becomes active"""
        self.logger.info("Entering Clip View")
        
        # DEBUG: Verificar estado de integración
        self.logger.info(f"🔍 Live integration: {self.live_integration}")
        
        if self.live_integration:
            self.logger.info(f"🔍 Live integration status: {self.live_integration.get_status()}")
            if self.live_integration.osc_client:
                self.logger.info(f"🔍 OSC client connected: {self.live_integration.osc_client.is_connected}")
        else:
            self.logger.error("❌ No live_integration provided to ClipView!")
        
        if self.live_integration and self.live_integration.osc_client and self.live_integration.osc_client.is_connected:
            # Usar datos reales de Live
            self.logger.info("📡 Using REAL Live data")
            self._request_live_data()
        else:
            # Fallback a datos demo si Live no conectado
            self.logger.warning("⚠️ Live not connected, using DEMO data")
            self._use_demo_data()
    
    def _create_demo_tracks(self):
        """Create demo track data"""
        tracks = [
            {"name": "Kick", "color": (0, 0.016, 1, 1)},
            {"name": "Hats", "color": (0, 1, 0.05, 1)},
            {"name": "Bass", "color": (1, 0.6, 0, 1)},
            {"name": "Tom", "color": (1, 0.85, 0, 1)},
            {"name": "FX", "color": (1, 0, 0.48, 1)},
            {"name": "Pad", "color": (0, 1, 0.97, 1)},
            {"name": "Lead", "color": (1, 0.57, 0, 1)},
            {"name": "Keys", "color": (0, 0.016, 1, 1)},
            {"name": "Perc", "color": (0.8, 0.2, 0.8, 1)},
            {"name": "Vocal", "color": (0.2, 0.8, 0.2, 1)},
        ]
        
        # Add clips to each track
        for track in tracks:
            track["clips"] = [{"status": "empty", "name": ""} for _ in range(12)]
        
        # Add some demo clips
        tracks[0]["clips"][0] = {"status": "playing", "name": "Kick Loop"}
        tracks[1]["clips"][1] = {"status": "queued", "name": "Hats Pattern"}
        tracks[2]["clips"][2] = {"status": "empty", "name": "Bass Line"}
        tracks[3]["clips"][0] = {"status": "playing", "name": "Tom Beat"}
        tracks[8]["clips"][0] = {"status": "playing", "name": "Perc Loop"}
        tracks[9]["clips"][1] = {"status": "queued", "name": "Vocal Chop"}
        
        return tracks
    
    def _request_live_data(self):
        """Request real data from Live"""
        self.logger.info("📡 Requesting data from Live...")
        
        osc = self.live_integration.osc_client
        
        # Solicitar nombres de tracks
        osc.send_message("/live/song/get/track_names")
        
        # Solicitar número de scenes
        osc.send_message("/live/song/get/num_scenes")
        
        # NO solicitar clips aquí - hacerlo después de recibir track_names

    def _on_live_track_names(self, **kwargs):
        """Handle track names from Live"""
        names = kwargs.get('names', [])
        self.logger.info(f"📋 Received track names from Live: {names}")
        
        # Crear estructura de tracks con datos reales
        self.live_tracks = []
        for i, name in enumerate(names):
            track = {
                "name": name,
                "color": self._get_track_color(i),  # Se actualizará con color real
                "clips": [{"status": "empty", "name": ""} for _ in range(12)]
            }
            self.live_tracks.append(track)
        
        # Poblar UI con datos reales
        self._populate_headers()
        self._populate_clips()
        
        # AHORA solicitar clips con nombres para el número real de tracks
        osc = self.live_integration.osc_client
        for track_id in range(len(names)):
            for scene_id in range(12):
                osc.send_message("/live/clip/get/playing_status", track_id, scene_id)
                osc.send_message("/live/clip/get/name", track_id, scene_id)
                osc.send_message("/live/clip/get/length", track_id, scene_id)  # NUEVO
                osc.send_message("/live/clip/get/has_audio_output", track_id, scene_id)  # NUEVO

    def _on_live_clip_status(self, **kwargs):
        """Handle clip status updates from Live"""
        track = kwargs.get('track', 0)
        scene = kwargs.get('scene', 0)
        status = kwargs.get('status', 'empty')
        
        # Actualizar datos locales
        if track < len(self.live_tracks) and scene < len(self.live_tracks[track]["clips"]):
            self.live_tracks[track]["clips"][scene]["status"] = status
            
            # Actualizar UI
            self._update_clip_visual(track, scene, status)

    def _on_live_clip_name(self, **kwargs):
        """Handle clip name updates from Live"""
        track = kwargs.get('track', 0)
        scene = kwargs.get('scene', 0) 
        name = kwargs.get('name', '')
        
        self.logger.debug(f"📝 Clip name: T{track}S{scene} = '{name}'")
        
        # Actualizar datos locales
        if (track < len(self.live_tracks) and 
            scene < len(self.live_tracks[track]["clips"])):
            self.live_tracks[track]["clips"][scene]["name"] = name
            
            # Actualizar UI si es necesario
            self._update_clip_name_visual(track, scene, name)

    def _update_clip_name_visual(self, track_id, scene_id, name):
        """Update clip name in UI"""
        # Encontrar el widget ClipSlot y actualizar su texto
        if hasattr(self.ids, 'clips_container'):
            # Buscar el slot específico y actualizar
            # (implementación depende de cómo esté estructurada la UI)
            pass

    def _on_live_clip_has_content(self, **kwargs):
        """Handle clip content updates from Live"""
        track = kwargs.get('track', 0)
        scene = kwargs.get('scene', 0) 
        has_content = kwargs.get('has_content', False)
        
        self.logger.debug(f"📁 Clip content: T{track}S{scene} = {has_content}")
        
        # Actualizar datos locales
        if (track < len(self.live_tracks) and 
            scene < len(self.live_tracks[track]["clips"])):
            self.live_tracks[track]["clips"][scene]["has_content"] = has_content
            
            # Actualizar visual del clip
            self._update_clip_content_visual(track, scene, has_content)

    def _get_track_color(self, track_index):
        """Get default color for track"""
        colors = [
            (0, 0.016, 1, 1),      # Azul
            (0, 1, 0.05, 1),       # Verde
            (1, 0.6, 0, 1),        # Naranja
            (1, 0.85, 0, 1),       # Amarillo
            (1, 0, 0.48, 1),       # Rosa
            (0, 1, 0.97, 1),       # Cyan
            (1, 0.57, 0, 1),       # Naranja claro
            (0.8, 0.2, 0.8, 1),    # Morado
        ]
        return colors[track_index % len(colors)]

    def _use_demo_data(self):
        """Fallback to demo data if Live not available"""
        self.live_tracks = self._create_demo_tracks()
        self._populate_headers()
        self._populate_clips()

    def _populate_headers(self):
        """Create track headers with real data"""
        from ui.widgets.track_header import TrackHeader
        
        if hasattr(self.ids, 'track_headers_container'):
            headers_container = self.ids.track_headers_container
            headers_container.clear_widgets()
            
            tracks_to_use = self.live_tracks if self.live_tracks else self._create_demo_tracks()
            
            for track_idx, track in enumerate(tracks_to_use):
                header = TrackHeader(
                    track_index=track_idx,
                    track_name=track["name"],
                    color_rgba=track["color"]
                )
                headers_container.add_widget(header)
            
            headers_container.width = len(tracks_to_use) * 88
    
    def _populate_clips(self):
        """Create clips grid"""
        from ui.widgets.clip_slot import ClipSlot
        
        if hasattr(self.ids, 'clips_container'):
            clips_container = self.ids.clips_container
            clips_container.clear_widgets()
            
            tracks_to_use = self.live_tracks if self.live_tracks else self._create_demo_tracks()
            
            for track_idx, track in enumerate(tracks_to_use):
                # Create clips column for this track
                clips_column = BoxLayout(
                    orientation='vertical',
                    size_hint_x=None,
                    width=88,
                    spacing=0
                )
                
                # Add clip slots (12 scenes)
                for scene_idx in range(12):
                    clip_info = track["clips"][scene_idx] if scene_idx < len(track["clips"]) else {}
                    
                    slot = ClipSlot(
                        track_index=track_idx,
                        scene_index=scene_idx,
                        status=clip_info.get("status", "empty"),
                    )
                    slot.label_text = clip_info.get("name", "")
                    clips_column.add_widget(slot)
                
                clips_container.add_widget(clips_column)
            
            clips_container.width = len(tracks_to_use) * 88
    
    def _sync_header_scroll(self, scroll_x):
        """Sync header scroll with content scroll"""
        if hasattr(self.ids, 'headers_scroll'):
            self.ids.headers_scroll.scroll_x = scroll_x
    
    def _focus_track(self, track_id: int):
        """Focus on a specific track"""
        tracks_to_use = self.live_tracks if self.live_tracks else self._create_demo_tracks()
        if 0 <= track_id < len(tracks_to_use):
            self.focused_track = track_id
            self.current_track_text = tracks_to_use[track_id]["name"]
            
            # Emit focus event
            bus.emit("track:focus", track=track_id)
    
    # Event Handlers
    def _on_track_focus(self, **kwargs):
        """Handle track focus events from other components"""
        track_id = kwargs.get('track', 0)
        self._focus_track(track_id)
    
    def _on_clip_changed(self, **kwargs):
        """Handle clip state changes"""
        track = kwargs.get('track', 0)
        scene = kwargs.get('scene', 0)
        status = kwargs.get('status', 'empty')
        
        # Update demo data to reflect changes
        if 0 <= track < len(self.live_tracks) and 0 <= scene < len(self.live_tracks[track]["clips"]):
            self.live_tracks[track]["clips"][scene]["status"] = status
            self.logger.debug(f"Clip changed: T{track}S{scene} -> {status}")

    def _on_live_connected(self, **kwargs):
        """Handle Live connection confirmation"""
        self.logger.info("🎉 Live connection confirmed in ClipView!")
        # Optionally do something when Live connects

    def _on_structure_changed(self, **kwargs):
        """Handle Live structure changes (tracks added/removed)"""
        self.logger.info("🔄 Live structure changed - refreshing UI...")
        # Re-request data to update UI
        self._request_live_data()

    def _on_live_track_color(self, **kwargs):
        """Handle track color updates from Live"""
        track = kwargs.get('track', 0)
        color = kwargs.get('color', (0.5, 0.5, 0.5, 1.0))
        
        # Actualizar color en datos locales
        if track < len(self.live_tracks):
            self.live_tracks[track]["color"] = color
            
            # Actualizar header visual
            self._update_track_header_color(track, color)

    def _update_track_header_color(self, track_id, color):
        """Update track header color in UI"""
        if hasattr(self.ids, 'track_headers_container'):
            headers = self.ids.track_headers_container.children
            if track_id < len(headers):
                header = headers[-(track_id + 1)]  # Kivy reverses children
                header.color_rgba = color
#!/usr/bin/env python3
"""Debug the integration to see why mocks are still showing"""

import time
import logging
from logic.state.app_state import AppState
from logic.clip_manager import ClipManager
from logic.live_integration import LiveIntegration
from logic.bus import bus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IntegrationDebug")

def debug_integration():
    """Debug the integration flow"""
    logger.info("🔍 Debugging integration flow...")
    
    # Create components exactly like main.py
    app_state = AppState()
    app_state.init_project(tracks=8, scenes=12)
    
    clip_manager = ClipManager(app_state)
    live_integration = LiveIntegration(app_state)
    
    # Check connection status
    logger.info(f"📡 Initial connection status: {live_integration.get_status()}")
    
    # Try to connect
    logger.info("🔌 Attempting to connect to Live...")
    connection_success = live_integration.connect()
    
    if connection_success:
        logger.info("✅ Connected to Live!")
        
        # Check status after connection
        status = live_integration.get_status()
        logger.info(f"📊 Connection status: {status}")
        
        # Test basic communication
        logger.info("📤 Testing basic communication...")
        live_integration.osc_client.send_message("/live/test", "debug_test")
        time.sleep(1)
        
        # Request track names
        logger.info("📋 Requesting track names...")
        live_integration.osc_client.send_message("/live/song/get/track_names")
        time.sleep(2)
        
        # Check if any Live events were fired
        logger.info("🎯 Testing event bus...")
        
        def test_handler(**kwargs):
            logger.info(f"📥 Event received: {kwargs}")
        
        bus.on("live:track_names", test_handler)
        bus.on("live:connection_confirmed", test_handler)
        
        # Send another test
        live_integration.osc_client.send_message("/live/song/get/track_names")
        time.sleep(2)
        
    else:
        logger.error("❌ Failed to connect to Live")
        logger.error("This is why you're seeing mock data!")
        
        # Check specific failure reasons
        if not live_integration.osc_client:
            logger.error("   - OSC client not created")
        elif not live_integration.osc_client.is_connected:
            logger.error("   - OSC client not connected")
        
    live_integration.disconnect()

if __name__ == "__main__":
    debug_integration()
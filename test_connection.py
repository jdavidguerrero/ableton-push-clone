#!/usr/bin/env python3
"""Simple test for OSC connection to Live"""

import time
import logging
from logic.osc_client import OSCClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Test")

def test_connection():
    """Test AbletonOSC connection"""
    
    logger.info("🚀 Testing connection to AbletonOSC...")
    
    # Create OSC client
    osc_client = OSCClient("192.168.80.33", 11000, 11001)
    
    # Test handlers
    def on_test_response(address, *args):
        logger.info(f"✅ Live responded: {args}")
    
    def on_track_names(address, *args):
        logger.info(f"📋 Track names: {args}")
    
    # Register handlers
    osc_client.register_handler("/live/test", on_test_response)
    osc_client.register_handler("/live/song/get/track_names", on_track_names)
    
    # Connect
    if not osc_client.connect():
        logger.error("❌ Failed to connect")
        return
    
    logger.info("✅ Connected!")
    
    # Test commands
    logger.info("🏓 Testing Live connection...")
    osc_client.send_message("/live/test", "hello")
    time.sleep(1)
    
    logger.info("📋 Getting track names...")
    osc_client.send_message("/live/song/get/track_names")
    time.sleep(1)
    
    logger.info("🎚️ Testing volume...")
    osc_client.set_track_volume(0, 0.75)
    time.sleep(1)
    
    # Status
    status = osc_client.get_connection_info()
    logger.info(f"📊 Status: sent={status['messages_sent']}, received={status['messages_received']}")
    
    osc_client.disconnect()
    logger.info("✅ Test completed!")

if __name__ == "__main__":
    test_connection()

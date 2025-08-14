#!/usr/bin/env python3
"""Simple test for OSC connection to Live"""

import time
import logging
from logic.osc_client import OSCClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Test")

def test_with_client_setup():
    """Test OSC with explicit client setup"""
    logger.info("🚀 Testing OSC with client setup...")
    
    osc_client = OSCClient("192.168.80.33", 11000, 11001)
    
    # Response handler
    def on_response(address, *args):
        logger.info(f"✅ RECEIVED: {address} {args}")
    
    # Register handlers
    osc_client.register_handler("/live/test", on_response)
    osc_client.register_handler("/live/song/get/tempo", on_response)
    
    if not osc_client.connect():
        logger.error("❌ Failed to connect")
        return
    
    # 🔑 IMPORTANTE: Decirle a AbletonOSC dónde enviar respuestas
    logger.info("📍 Setting up client IP for responses...")
    osc_client.send_message("/live/startup")  # Esto registra tu IP automáticamente
    time.sleep(1)
    
    # Ahora hacer los tests normales
    logger.info("🏓 Testing with client registered...")
    osc_client.send_message("/live/test", "hello_after_startup")
    time.sleep(2)
    
    osc_client.send_message("/live/song/get/tempo")
    time.sleep(2)
    
    status = osc_client.get_connection_info()
    logger.info(f"📊 Status: sent={status['messages_sent']}, received={status['messages_received']}")
    
    osc_client.disconnect()

if __name__ == "__main__":
    test_with_client_setup()

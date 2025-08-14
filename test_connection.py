#!/usr/bin/env python3
"""Simple test to see all incoming OSC messages"""

import time
import logging
from logic.osc_client import OSCClient

# CAMBIAR A DEBUG para ver TODO
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("SimpleTest")

def test_receive_all():
    """Test receiving all OSC messages"""
    logger.info("🎯 Testing OSC message reception...")
    
    osc_client = OSCClient("192.168.80.33", 11000, 11001)
    
    # Handler que cuenta todo
    message_count = [0]
    
    def count_messages(address, *args):
        message_count[0] += 1
        logger.info(f"📩 MESSAGE #{message_count[0]}: {address} {args}")
    
    # Registrar handler para TODO
    osc_client.register_handler("/*", count_messages)  # Wildcard
    
    if not osc_client.connect():
        logger.error("❌ Failed to connect")
        return
    
    logger.info("✅ Connected and listening for ALL messages...")
    
    # Enviar algunos comandos simples
    logger.info("📤 Sending test commands...")
    osc_client.send_message("/live/test", "hello")
    time.sleep(2)
    
    osc_client.send_message("/live/application/get/version")
    time.sleep(2)
    
    osc_client.send_message("/live/song/get/tempo")
    time.sleep(2)
    
    # Resultado
    status = osc_client.get_connection_info()
    logger.info(f"\n📊 RESULTS:")
    logger.info(f"   Sent: {status['messages_sent']}")
    logger.info(f"   Received (client): {status['messages_received']}")
    logger.info(f"   Received (handler): {message_count[0]}")
    
    if message_count[0] > 0:
        logger.info("🎉 SUCCESS! Messages are being received!")
    else:
        logger.error("❌ No messages received in handlers")
        logger.info("But tcpdump shows packets arriving...")
        logger.info("Check OSC message format or dispatcher")
    
    osc_client.disconnect()

if __name__ == "__main__":
    test_receive_all()
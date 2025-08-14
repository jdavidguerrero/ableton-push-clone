#!/usr/bin/env python3
"""Test OSC server functionality"""

import time
import logging
import socket
import threading
from logic.osc_client import OSCClient

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("ServerTest")

def test_server_directly():
    """Test OSC server directly"""
    logger.info("🔧 Testing OSC server directly...")
    
    received_messages = []
    
    def message_handler(address, *args):
        received_messages.append((address, args))
        logger.info(f"✅ HANDLER CALLED: {address} {args}")
    
    # Create OSC client
    osc_client = OSCClient("192.168.80.33", 11000, 11001)
    
    # Register handler
    osc_client.register_handler("/*", message_handler)
    
    if not osc_client.connect():
        logger.error("❌ Failed to connect")
        return
    
    logger.info("✅ OSC Client connected")
    
    # Give server time to start
    time.sleep(1)
    
    # Send some commands
    logger.info("📤 Sending test commands...")
    
    commands = [
        "/live/test",
        "/live/application/get/version", 
        "/live/song/get/tempo"
    ]
    
    for cmd in commands:
        logger.info(f"📤 Sending: {cmd}")
        osc_client.send_message(cmd, "test_arg")
        time.sleep(3)  # More time between commands
    
    # Wait for responses
    logger.info("⏳ Waiting for responses...")
    time.sleep(5)
    
    # Check results
    status = osc_client.get_connection_info()
    logger.info(f"\n📊 Server Test Results:")
    logger.info(f"   Commands sent: {status['messages_sent']}")
    logger.info(f"   Messages received (counter): {status['messages_received']}")
    logger.info(f"   Messages received (handler): {len(received_messages)}")
    logger.info(f"   Server running: {status['server_running']}")
    
    if received_messages:
        logger.info("🎉 Server is working!")
        for addr, args in received_messages:
            logger.info(f"   📥 {addr}: {args}")
    else:
        logger.error("❌ Server not receiving messages")
        
        # Check if server thread is alive
        if osc_client.server_thread and osc_client.server_thread.is_alive():
            logger.info("✅ Server thread is alive")
        else:
            logger.error("❌ Server thread is dead")
            
        logger.info("\n🔧 Try manual UDP test:")
        logger.info("1. In another terminal: echo '/test hello' | nc -u 192.168.80.74 11001")
        logger.info("2. Check if manual UDP works")
    
    osc_client.disconnect()

def test_manual_udp_server():
    """Test manual UDP server to isolate the problem"""
    logger.info("🛠️ Testing manual UDP server...")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 11001))
    sock.settimeout(5.0)
    
    logger.info("📡 Manual UDP server listening on 0.0.0.0:11001")
    logger.info("📤 Send test from Live machine: echo 'test' | nc -u 192.168.80.74 11001")
    
    try:
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                logger.info(f"📥 RAW UDP received from {addr}: {data}")
                
                # Try to decode as OSC
                try:
                    # Basic OSC message starts with '/'
                    if data.startswith(b'/'):
                        logger.info(f"🎵 Looks like OSC: {data}")
                    else:
                        logger.info(f"📄 Plain text: {data.decode('utf-8', errors='ignore')}")
                except:
                    logger.info(f"🔥 Binary data: {data.hex()}")
                    
            except socket.timeout:
                logger.info("⏰ Timeout - no data received")
                break
                
    except KeyboardInterrupt:
        logger.info("⏹️ Manual test stopped")
    finally:
        sock.close()

if __name__ == "__main__":
    print("Choose test:")
    print("1. Test OSC server")
    print("2. Test manual UDP server") 
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_server_directly()
    elif choice == "2":
        test_manual_udp_server()
    else:
        logger.info("Running both tests...")
        test_server_directly()
        print("\n" + "="*50 + "\n")
        test_manual_udp_server()
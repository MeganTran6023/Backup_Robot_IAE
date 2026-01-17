'''
Only sends metadata from python rpi to server java
'''

#!/usr/bin/env python3
import socket
import time
import zlib
import threading
from bson import BSON  # pip install pymongo

CHUNK_SIZE = 65000 - 4
UDP_IP = "192.168.1.209"  # Java receiver IP
UDP_PORT = 9999

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def sendBson(payload: dict):
    data = BSON.encode(payload)
    sock.sendto(data, (UDP_IP, UDP_PORT))
    print(f"[Python] Sent BSON: {payload}")

def sendChunkWithChecksum(chunk: bytes):
    checksum = zlib.crc32(chunk)
    packet = chunk + checksum.to_bytes(4, byteorder="big")
    sock.sendto(packet, (UDP_IP, UDP_PORT))
    print(f"[Python] Sent chunk ({len(chunk)} bytes) with checksum {checksum}")

def metadata_loop():
    while True:
        meta = {
            "sensor_id": "PiCam_001",
            "timestamp": time.time(),
            "status": "active"
        }
        sendBson(meta)
        time.sleep(5)

def stream_loop():
    counter = 0
    while True:
        frame_data = f"Frame {counter}".encode("utf-8")  # Dummy frame data
        for i in range(0, len(frame_data), CHUNK_SIZE):
            sendChunkWithChecksum(frame_data[i:i+CHUNK_SIZE])
        counter += 1
        time.sleep(1)

# Start threads
threading.Thread(target=metadata_loop, daemon=True).start()
threading.Thread(target=stream_loop, daemon=True).start()

# Keep main thread alive
while True:
    time.sleep(1)

'''
videoViewer.py
---------------
Receives UDP packets, validates checksum, and streams frames over HTTP.
After 15 seconds of streaming, simulates a socket failure and then
recovers using retry logic.
'''

from flask import Flask, Response
import socket
import cv2
import numpy as np
import threading
import zlib
import time
import random
from datetime import datetime

app = Flask(__name__)

UDP_IP = "0.0.0.0"
UDP_PORT = 5005
BUFFER_SIZE = 65536

frame_data = b''
frame_lock = threading.Lock()

simulate_failure_after = 15  # seconds
failure_triggered = False

# Exponential backoff with jitter
def exponential_backoff_with_jitter(base=1.0, max_attempts=1):
    for attempt in range(1, max_attempts + 1):
        delay = base * (2 ** (attempt - 1))
        jitter = random.uniform(0, delay * 0.5)
        yield delay + jitter

def udp_listener():
    """Listen for UDP packets, validate checksum, and assemble frames."""
    global frame_data, failure_triggered
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    buffer = b''

    start_time = time.time()
    last_report_time = start_time
    packets_received = 0
    packets_bad_checksum = 0

    while True:
        # Simulate failure after X seconds
        if not failure_triggered and time.time() - start_time >= simulate_failure_after:
            print("Simulating UDP listener failure...")
            sock.close()
            failure_triggered = True
            raise ConnectionError("Simulated socket failure")

        packet, _ = sock.recvfrom(BUFFER_SIZE)
        if len(packet) < 4:
            packets_bad_checksum += 1
            continue

        chunk = packet[:-4]
        recv_checksum = int.from_bytes(packet[-4:], byteorder='big')
        calc_checksum = zlib.crc32(chunk)

        packets_received += 1
        if recv_checksum != calc_checksum:
            packets_bad_checksum += 1
        else:
            buffer += chunk
            img = cv2.imdecode(np.frombuffer(buffer, dtype=np.uint8), cv2.IMREAD_COLOR)
            if img is not None:
                ret, jpeg = cv2.imencode('.jpg', img)
                if ret:
                    with frame_lock:
                        frame_data = jpeg.tobytes()
                buffer = b''

        # Log stats every 5 sec
        now = time.time()
        if now - last_report_time >= 5:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            good = packets_received - packets_bad_checksum
            print(f"[{timestamp}] Packets received: {packets_received}, Good: {good}, Bad checksum: {packets_bad_checksum}")
            last_report_time = now

def udp_listener_with_retry():
    """Wrap listener with retry logic."""
    while True:
        try:
            udp_listener()
        except (OSError, socket.error, ConnectionError) as e:
            print(f"UDP listener error: {e}")
            for attempt, delay in enumerate(exponential_backoff_with_jitter(), 1):
                print(f"Retry {attempt} in {delay:.2f}s...")
                time.sleep(delay)
                try:
                    print("Reinitializing UDP listener...")
                    udp_listener()
                    print("Listener successfully restored.")
                    break
                except Exception as err:
                    print(f"Retry {attempt} failed: {err}")

def generate_frames():
    global frame_data
    while True:
        with frame_lock:
            if frame_data:
                frame = frame_data
            else:
                continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return '<h2>UDP Camera Stream</h2><img src="/video_feed">'

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    threading.Thread(target=udp_listener_with_retry, daemon=True).start()
    app.run(host='0.0.0.0', port=8000)

'''
UDPCamera.py
------------
Streams video frames via UDP with checksum validation and includes
a retry mechanism using exponential backoff. After 15 seconds of
streaming, simulates a connection loss and then forces two failed
reconnect attempts before succeeding on the third attempt.
'''

import cv2
import socket
import mediapipe as mp
import zlib
import random
import time
import sys

# UDP Settings
UDP_IP = "127.0.0.1"  # Change to receiver IP if needed
UDP_PORT = 5005
CHUNK_SIZE = 65000 - 4  # Reserve 4 bytes for checksum

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

simulate_failure_after = 15  # seconds
failure_triggered = False
forced_failure_count = 0  # Track forced retry failures

# Exponential backoff with jitter for 3 attempts
def exponential_backoff_with_jitter(base=1.0, max_attempts=3):
    for attempt in range(1, max_attempts + 1):
        delay = base * (2 ** (attempt - 1))  # 1, 2, 4 sec
        jitter = random.uniform(0, delay * 0.5)
        yield delay + jitter

def start_stream():
    global failure_triggered
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    camera = cv2.VideoCapture('/dev/video0')

    if not camera.isOpened():
        raise RuntimeError("Camera could not be opened")

    start_time = time.time()

    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:

        while True:
            # Simulate failure after X seconds
            if not failure_triggered and time.time() - start_time >= simulate_failure_after:
                print("Simulating connection loss...")
                camera.release()
                sock.close()
                failure_triggered = True
                raise ConnectionError("Simulated camera/socket failure")

            ret, frame = camera.read()
            if not ret:
                break

            # Convert BGR to RGB for Mediapipe
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(image_rgb)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            data = buffer.tobytes()

            # Break into chunks and send with checksum
            for i in range(0, len(data), CHUNK_SIZE):
                chunk = data[i:i+CHUNK_SIZE]
                checksum = zlib.crc32(chunk)
                packet = chunk + checksum.to_bytes(4, byteorder='big')
                sock.sendto(packet, (UDP_IP, UDP_PORT))

    camera.release()
    sock.close()

if __name__ == "__main__":
    while True:
        try:
            start_stream()
        except (OSError, socket.error, ConnectionError) as e:
            print(f"Streaming error: {e}")
            success = False
            for attempt, delay in enumerate(exponential_backoff_with_jitter(max_attempts=3), 1):
                print(f"Retry {attempt} in {delay:.2f}s...")
                time.sleep(delay)

                # Force first 2 retries to fail
                if attempt < 3:
                    print(f"Simulated failure on retry {attempt}.")
                    continue

                try:
                    print("Reconnecting (attempt 3)...")
                    start_stream()
                    print("Stream successfully restored on attempt 3.")
                    success = True
                    break
                except Exception as err:
                    print(f"Retry {attempt} failed: {err}")

            if not success:
                print("All retries failed. Exiting program.")
                sys.exit(1)

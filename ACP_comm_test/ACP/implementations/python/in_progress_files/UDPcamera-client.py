'''
UDPCamera.py - client
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
from typing import Generator, Any

class VideoStreamSender:
    """
    Client implementation for capturing video from a local camera, performing
    MediaPipe processing (Hand Tracking), segmenting frames, and streaming
    them via UDP with checksums to a remote receiver.

    Includes retry logic with exponential backoff for connection recovery.
    """

    def __init__(self, receiver_ip: str = "127.0.0.1", udp_port: int = 5005, chunk_size: int = 65000 - 4, simulate_failure_after: int = 15):
        """
        Initialize the streaming sender instance.

        :param receiver_ip: The IP address of the UDP receiver (server).
        :param udp_port: The UDP port number on the receiver to send packets to.
        :param chunk_size: The maximum size of the data chunk within a UDP packet (minus checksum bytes).
        :param simulate_failure_after: Time in seconds after which a connection failure is simulated.
        """
        # Configuration
        self.UDP_IP: str = receiver_ip
        self.UDP_PORT: int = udp_port
        self.CHUNK_SIZE: int = chunk_size
        self.simulate_failure_after: int = simulate_failure_after

        # State management
        self.failure_triggered: bool = False
        self.start_time: float = 0.0

        # MediaPipe initialization
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils

    def _exponential_backoff_with_jitter(self, base: float = 1.0, max_attempts: int = 3) -> Generator[float, None, None]:
        """
        Generator for calculating delays using exponential backoff with jitter.

        :param base: The base delay time (e.g., 1.0 seconds).
        :param max_attempts: The maximum number of retry attempts to yield delays for.
        :return: A generator yielding the calculated delay in seconds for each attempt.
        """
        for attempt in range(1, max_attempts + 1):
            delay = base * (2 ** (attempt - 1))  # 1, 2, 4 sec
            jitter = random.uniform(0, delay * 0.5)
            yield delay + jitter

    def start_stream(self) -> None:
        """
        Captures video from the camera, processes frames with MediaPipe,
        encodes them, fragments them into UDP packets with checksums, and sends
        them to the configured receiver.

        This method runs indefinitely until a connection failure occurs.

        :raises RuntimeError: If the camera cannot be opened (e.g., /dev/video0 not found).
        :raises ConnectionError: On simulated socket/camera failure, for testing recovery.
        """
        self.start_time = time.time()
        sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Using 0 for default camera
        camera: cv2.VideoCapture = cv2.VideoCapture(0)

        if not camera.isOpened():
            sock.close()
            raise RuntimeError("Camera could not be opened (check /dev/video0 or index 0)")

        print(f"Streaming started to {self.UDP_IP}:{self.UDP_PORT}. Chunk size: {self.CHUNK_SIZE} bytes.")

        # Initialize MediaPipe Hands model
        with self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5) as hands:

            while True:
                # Simulate failure check
                if not self.failure_triggered and time.time() - self.start_time >= self.simulate_failure_after:
                    print("Simulating connection loss...")
                    camera.release()
                    sock.close()
                    self.failure_triggered = True
                    raise ConnectionError("Simulated camera/socket failure")

                ret, frame = camera.read()
                if not ret:
                    # Camera read failure, can break the stream loop
                    break

                # 1. Process Frame with MediaPipe
                image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(image_rgb)

                # 2. Draw Landmarks
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                # 3. Encode Frame
                _, buffer = cv2.imencode('.jpg', frame)
                data = buffer.tobytes()

                # 4. Fragment and Send
                for i in range(0, len(data), self.CHUNK_SIZE):
                    chunk = data[i:i+self.CHUNK_SIZE]
                    checksum = zlib.crc32(chunk)
                    # Append 4-byte checksum to the chunk
                    packet = chunk + checksum.to_bytes(4, byteorder='big')
                    sock.sendto(packet, (self.UDP_IP, self.UDP_PORT))

        # Cleanup on normal exit (e.g., camera disconnection)
        camera.release()
        sock.close()

    def run(self) -> None:
        """
        The main execution loop for the streaming sender. It continuously calls
        `start_stream` and implements the retry logic with exponential backoff
        upon failure until successful or max retries are exceeded.

        :return: None. Runs the application until permanent failure or termination.
        """
        print("Starting Video Stream Sender...")
        while True:
            try:
                # Attempt to start or restart the stream
                self.start_stream()
            except (RuntimeError, OSError, socket.error, ConnectionError) as e:
                print(f"Streaming error detected: {e}")

                success = False
                # Iterate through retry attempts
                for attempt, delay in enumerate(self._exponential_backoff_with_jitter(max_attempts=3), 1):
                    print(f"Retry {attempt} in {delay:.2f}s...")
                    time.sleep(delay)

                    # Simulating forced failure for the first 2 retries
                    if attempt < 3:
                        print(f"Simulated failure on retry {attempt}.")
                        continue

                    try:
                        print(f"Reconnecting (attempt {attempt})...")
                        # Reset failure state and start_time for a clean re-run
                        self.failure_triggered = False
                        self.start_time = time.time()
                        self.start_stream()
                        print(f"Stream successfully restored on attempt {attempt}.")
                        success = True
                        break
                    except Exception as err:
                        print(f"Retry {attempt} failed: {err}")

                if not success:
                    print("All retries failed. Exiting program.")
                    sys.exit(1)


'''
videoViewer.py - server
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
from typing import Iterator, Generator, Tuple, Any, Optional

class VideoStreamingServer:
    """
    Server implementation for receiving a video stream via UDP (or simulated UDP)
    and re-streaming it to a client over HTTP using Flask.

    Includes robust features like checksum validation and exponential backoff
    for connection recovery.
    """

    def __init__(self, udp_ip: str = "0.0.0.0", udp_port: int = 5005, http_port: int = 8000, simulate_failure_after: int = 15):
        """
        Initialize the streaming server instance.

        :param udp_ip: The IP address the UDP listener will bind to.
        :param udp_port: The UDP port number to listen on for incoming video packets.
        :param http_port: The HTTP port number for the Flask server to run on.
        :param simulate_failure_after: Time in seconds after which a socket failure is simulated.
        """
        # Configuration
        self.UDP_IP = udp_ip
        self.UDP_PORT = udp_port
        self.HTTP_PORT = http_port
        self.BUFFER_SIZE = 65536 # Max packet size
        self.simulate_failure_after = simulate_failure_after

        # State management
        self.frame_data: bytes = b''
        self.frame_lock: threading.Lock = threading.Lock()
        self.failure_triggered: bool = False
        self.start_time: float = time.time()

        # Application setup
        self.app = Flask(__name__)
        self._setup_routes()

    def _setup_routes(self):
        """
        Registers the class methods as Flask routes.
        """
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/video_feed', 'video_feed', self.video_feed)

    def _exponential_backoff_with_jitter(self, base: float = 1.0, max_attempts: int = 5) -> Generator[float, None, None]:
        """
        Generator for calculating delays using exponential backoff with jitter.

        :param base: The base delay time (e.g., 1.0 seconds).
        :param max_attempts: The maximum number of retry attempts to yield delays for.
        :return: A generator yielding the calculated delay in seconds for each attempt.
        """
        for attempt in range(1, max_attempts + 1):
            delay = base * (2 ** (attempt - 1))
            jitter = random.uniform(0, delay * 0.5)
            yield delay + jitter

    def _udp_listener(self) -> None:
        """
        Listens for UDP packets on the configured port, validates checksum,
        and assembles the video frame.

        This function runs indefinitely in a thread and updates self.frame_data.
        It raises a ConnectionError after 'simulate_failure_after' seconds to
        trigger the retry logic.

        :raises ConnectionError: On simulated socket failure, for testing recovery.
        """
        sock: Optional[socket.socket] = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind((self.UDP_IP, self.UDP_PORT))
            buffer = b''

            last_report_time = time.time()
            packets_received = 0
            packets_bad_checksum = 0

            print(f"UDP Listener started on {self.UDP_IP}:{self.UDP_PORT}")

            while True:
                # Simulate failure check
                if not self.failure_triggered and time.time() - self.start_time >= self.simulate_failure_after:
                    print("Simulating UDP listener failure...")
                    sock.close()
                    self.failure_triggered = True
                    raise ConnectionError("Simulated socket failure")

                packet, _ = sock.recvfrom(self.BUFFER_SIZE)

                if len(packet) < 4:
                    packets_bad_checksum += 1
                    continue

                # Checksum validation
                chunk = packet[:-4]
                recv_checksum = int.from_bytes(packet[-4:], byteorder='big')
                calc_checksum = zlib.crc32(chunk)

                packets_received += 1
                if recv_checksum != calc_checksum:
                    packets_bad_checksum += 1
                else:
                    buffer += chunk
                    # Try to decode the image from the buffer
                    img = cv2.imdecode(np.frombuffer(buffer, dtype=np.uint8), cv2.IMREAD_COLOR)

                    if img is not None:
                        # Frame successfully decoded, encode to JPEG for streaming
                        ret, jpeg = cv2.imencode('.jpg', img)
                        if ret:
                            with self.frame_lock:
                                self.frame_data = jpeg.tobytes()
                        buffer = b'' # Reset buffer after successful frame assembly

                # Log statistics every 5 seconds
                now = time.time()
                if now - last_report_time >= 5:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    good = packets_received - packets_bad_checksum
                    print(f"[{timestamp}] Packets received: {packets_received}, Good: {good}, Bad checksum: {packets_bad_checksum}")
                    last_report_time = now
        except Exception as e:
            # Clean up socket on exit
            if sock:
                sock.close()
            raise e


    def _udp_listener_with_retry(self) -> None:
        """
        Wraps the UDP listener in a loop with retry logic using exponential backoff
        to handle and recover from simulated or real socket failures.

        :return: None. Runs indefinitely in a daemon thread.
        """
        while True:
            try:
                self._udp_listener()
            except (OSError, socket.error, ConnectionError) as e:
                print(f"UDP listener error: {e}")
                for attempt, delay in enumerate(self._exponential_backoff_with_jitter(), 1):
                    print(f"Retry {attempt} in {delay:.2f}s...")
                    time.sleep(delay)
                    try:
                        print("Attempting to reinitialize UDP listener...")
                        # Reset failure state if the listener is successfully reinitialized
                        self.failure_triggered = False
                        self.start_time = time.time() # Reset simulation timer
                        self._udp_listener() # This call blocks until a new error occurs or forever
                        print("Listener successfully restored.")
                        break # Exit the backoff loop and continue the main while True loop
                    except Exception as err:
                        print(f"Retry {attempt} failed: {err}")
                else:
                    # This block executes if the loop completes (max retries reached)
                    print("Maximum retries reached. Shutting down UDP listener thread.")
                    return


    def _generate_frames(self) -> Iterator[bytes]:
        """
        Generator function that yields JPEG video frames formatted for
        HTTP Multipart streaming (MJPEG).

        :return: A generator yielding byte chunks of the HTTP response,
                 each containing a single JPEG frame.
        """
        while True:
            frame: bytes = b''
            with self.frame_lock:
                if self.frame_data:
                    frame = self.frame_data
                else:
                    # Skip if no frame data is available yet
                    continue

            # Yield the frame using the multipart boundary
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def index(self) -> str:
        """
        Flask route handler for the root path ('/'). Displays a simple HTML page
        with an image tag pointing to the video feed.

        :return: HTML string for the main page.
        """
        return '<h2>UDP Camera Stream</h2><img src="/video_feed">'

    def video_feed(self) -> Response:
        """
        Flask route handler for the video stream ('/video_feed').

        This endpoint initiates the MJPEG stream response.

        :return: A Flask Response object configured for MJPEG streaming.
        """
        return Response(self._generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def run(self) -> None:
        """
        Starts the UDP listener thread and the Flask HTTP server.

        :return: None. Runs the application until terminated.
        """
        print("Starting Video Streaming Server...")
        # Start the UDP listener thread
        threading.Thread(target=self._udp_listener_with_retry, daemon=True).start()

        # Start the Flask web server
        self.app.run(host=self.UDP_IP, port=self.HTTP_PORT)

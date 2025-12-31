import cv2
import mediapipe as mp
import threading
import time
from acpcomms.python.src.acpcomms.streamer import Streamer  # ADDED
import zlib

# Initialize MediaPipe hand detection solutions
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Define chunk size for splitting JPEG data (留出4字节用于校验和)
CHUNK_SIZE = 65000 - 4

# ADDED: shared landmarks
# Dictionary to store hand landmark coordinates, shared between threads
latest_landmarks = {}
landmark_lock = threading.Lock()

# ADDED: streamer setup
# Configure UDP streamer to send data to localhost:5005
streamer = Streamer()
streamer.configure({
    "host": "127.0.0.1",
    "port": 5005
})
streamer.connect()

def send_metadata():
    """Send BSON template every 5 seconds."""
    while True:
        # Template structure for metadata transmission
        template = {
            "sensor_id": "TEMP_001",
            "sensor_type": "temperature",
            "data_type": "float",
            "timestamp": time.time(),
            "location": {"lat": 27.9944, "lon": -82.6367},
            "metadata": {
                "units": "Celsius",
                "schema_version": "1.0",
                "tags": ["ambient", "test"]
            },
            "data": {}
        }

        # Safely copy current landmark data into template
        with landmark_lock:
            template["data"] = latest_landmarks.copy()

        # Send metadata as BSON over UDP
        streamer.sendBson(template)
        time.sleep(5)

def start_stream():
    # Open camera device
    camera = cv2.VideoCapture('/dev/video0')
    
    # Start metadata transmission thread in background
    threading.Thread(target=send_metadata, daemon=True).start()

    # Initialize MediaPipe Hands detector with specified parameters
    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as hands:

        while True:
            # Capture frame from camera
            ret, frame = camera.read()
            if not ret:
                break

            # Convert frame from BGR to RGB for MediaPipe processing
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process frame to detect hand landmarks
            results = hands.process(image_rgb)

            # ADDED: Draw hand landmarks on the frame
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw landmarks and connections on the frame
                    mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),  # Landmark points (green)
                        mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)  # Connections (blue)
                    )

            # Update shared landmark dictionary with detected hand positions
            with landmark_lock:
                latest_landmarks.clear()
                if results.multi_hand_landmarks:
                    for h, hand in enumerate(results.multi_hand_landmarks):
                        for i, lm in enumerate(hand.landmark):
                            # Store normalized x, y, z coordinates for each landmark
                            latest_landmarks[f"hand_{h}_lm_{i}"] = {
                                "x": lm.x,
                                "y": lm.y,
                                "z": lm.z
                            }

            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            data = buffer.tobytes()

            # Split JPEG data into chunks and send with checksum
            for i in range(0, len(data), CHUNK_SIZE):
                streamer.sendChunkWithChecksum(data[i:i + CHUNK_SIZE])

    # Clean up resources
    camera.release()
    streamer.disconnect()

if __name__ == "__main__":
    start_stream()
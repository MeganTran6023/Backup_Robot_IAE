import cv2
import threading
import time
from acpcomms.streamer import Streamer 


# Define chunk size for splitting JPEG data 
CHUNK_SIZE = 65000 - 4

# ADDED: streamer setup
# Configure UDP streamer to send data to localhost:5005
streamer = Streamer()
streamer.configure({
    "host": "127.0.0.1",
    "port": 9999
})
streamer.connect()

def send_metadata():
    """Send BSON template every 5 seconds."""
    while True:
        # Template structure for metadata transmission
        template = {
            "sensor_id": "Camera_001",
            "sensor_type": "Camera Streamer",
            "data_type": "float",
            "timestamp": time.time(),
            "location": {"lat": 27.9944, "lon": -82.6367},
            "metadata": {
                "units": "Celsius",
                "schema_version": "1.0",
                "tags": ["ambient", "test"]
            },
            "data": {}  # regular/static data payload
        }

        # Send metadata as BSON over UDP
        streamer.sendBson(template)
        time.sleep(5)

def start_stream():
    # Open camera device
    camera = cv2.VideoCapture(0)
    
    # Start metadata transmission thread in background
    threading.Thread(target=send_metadata, daemon=True).start()

    while True:
        # Capture frame from camera
        ret, frame = camera.read()
        if not ret:
            break

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

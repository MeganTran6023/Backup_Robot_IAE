import socket
import threading
import zlib
import cv2
import numpy as np
from flask import Flask, Response

UDP_IP = "0.0.0.0"
UDP_PORT = 9990
CHUNK_SIZE = 65000

latest_frame = None
lock = threading.Lock()

app = Flask(__name__)

# ---------------- UDP RECEIVER ----------------
def udp_receiver():
    global latest_frame

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    buffer = b""

    while True:
        packet, _ = sock.recvfrom(CHUNK_SIZE + 4)
        chunk = packet[:-4]
        recv_checksum = int.from_bytes(packet[-4:], "big")

        if zlib.crc32(chunk) != recv_checksum:
            buffer = b""
            continue

        buffer += chunk

        # JPEG end marker
        if buffer.endswith(b'\xff\xd9'):
            img = cv2.imdecode(
                np.frombuffer(buffer, dtype=np.uint8),
                cv2.IMREAD_COLOR
            )
            buffer = b""

            if img is not None:
                with lock:
                    latest_frame = img

# ---------------- HTTP STREAM ----------------
def mjpeg_generator():
    while True:
        with lock:
            if latest_frame is None:
                continue
            _, jpeg = cv2.imencode(".jpg", latest_frame)
            frame = jpeg.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            frame +
            b"\r\n"
        )

@app.route("/video")
def video():
    return Response(
        mjpeg_generator(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

# ---------------- MAIN ----------------
if __name__ == "__main__":
    threading.Thread(target=udp_receiver, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, threaded=True)

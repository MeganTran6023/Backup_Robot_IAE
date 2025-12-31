from flask import Flask, Response
import cv2
import numpy as np
import threading
import zlib
import json
from acpcomms.python.src.acpcomms.streamer import Streamer  # ADDED

app = Flask(__name__)

frame_data = b''
frame_lock = threading.Lock()

# ADDED: streamer setup
streamer = Streamer()
streamer.configure({
    "localPort": 5005,
    "bufferSize": 65536
})
streamer.connect()


# ADDED: frame assembly buffer
frame_buffer = b''

def packet_handler(packet):
    global frame_data, frame_buffer
    data = packet.getData()

    # Try BSON metadata first
    meta = streamer.tryDecodeBson(data)
    if meta is not None:
        print(json.dumps(meta, indent=2))
        return

    if len(data) < 4:
        return

    chunk = data[:-4]
    recv_checksum = int.from_bytes(data[-4:], "big")

    if zlib.crc32(chunk) != recv_checksum:
        return

    # ADDED: accumulate JPEG chunks
    frame_buffer += chunk

    img = cv2.imdecode(
        np.frombuffer(frame_buffer, dtype=np.uint8),
        cv2.IMREAD_COLOR
    )

    if img is not None:
        ret, jpeg = cv2.imencode(".jpg", img)
        if ret:
            with frame_lock:
                frame_data = jpeg.tobytes()
        frame_buffer = b''  # reset after full frame


streamer.setPacketHandler(packet_handler)
streamer.startListener()


def generate_frames():
    while True:
        with frame_lock:
            if not frame_data:
                frame = None
            else:
                frame = frame_data
        
        if frame is None:
            continue  # Now we continue AFTER releasing the lock
        
        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' +
            frame +
            b'\r\n'
        )


@app.route('/')
def index():
    return '<h2>UDP Camera Stream</h2><img src="/video_feed">'

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

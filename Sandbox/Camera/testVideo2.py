from flask import Flask, Response
import cv2
import threading
import time
import os

app = Flask(__name__)
camera = cv2.VideoCapture(0)  # Use /dev/video0

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return '<h2>📷 USB Camera Stream</h2><img src="/video_feed" width="640" height="480">'

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def open_chromium():
    """Wait for Flask to start, then open Chromium at localhost."""
    time.sleep(2)
    print("🌐 Launching Chromium browser...")
    os.system("chromium-browser http://127.0.0.1:8000 &")

if __name__ == '__main__':
    # Launch Chromium automatically in a background thread
    threading.Thread(target=open_chromium, daemon=True).start()

    print("🎥 Starting Flask camera stream...")
    print("Your live video will open shortly in Chromium (http://127.0.0.1:8000)")
    print("Press Ctrl+C to stop.\n")

    app.run(host='0.0.0.0', port=8000, threaded=True)

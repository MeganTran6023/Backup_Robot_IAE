from flask import Flask, Response
import cv2
import threading
import time
import os
import random
from adafruit_servokit import ServoKit

# --------------------------
# Servo setup
# --------------------------
kit = ServoKit(channels=16)

def smooth_random_sweep(ch, step=0.05, delay=0.05):
    """Continuously sweep a servo channel smoothly to random throttle values between -1 and 1."""
    current = 0.0
    kit.continuous_servo[ch].throttle = current
    
    while True:
        target = random.uniform(-1, 1)
        while abs(current - target) > step:
            current += step if current < target else -step
            kit.continuous_servo[ch].throttle = current
            time.sleep(delay)
        current = target
        kit.continuous_servo[ch].throttle = current
        time.sleep(delay)

# Start servo threads
threading.Thread(target=smooth_random_sweep, args=(0,), daemon=True).start()
threading.Thread(target=smooth_random_sweep, args=(1,), daemon=True).start()

# --------------------------
# Flask camera stream setup
# --------------------------
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

# --------------------------
# Main program
# --------------------------
if __name__ == '__main__':
    threading.Thread(target=open_chromium, daemon=True).start()

    print("🎥 Starting Flask camera stream with servo control...")
    print("Your live video will open shortly in Chromium (http://127.0.0.1:8000)")
    print("Press Ctrl+C to stop.\n")

    try:
        app.run(host='0.0.0.0', port=8000, threaded=True)
    except KeyboardInterrupt:
        kit.continuous_servo[0].throttle = 0
        kit.continuous_servo[1].throttle = 0
        camera.release()
        print("\n🛑 Stopped all servos and released camera safely.")

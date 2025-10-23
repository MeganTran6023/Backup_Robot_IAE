"""
Full Robot Control + Live Camera Stream
---------------------------------------
Includes:
- DC motors: forward, backward, turn
- Ultrasonic distance sensing
- Random servo motion (PCA9685)
- IR sensors (GPIO 16 & 21)
- Live camera stream via Flask, auto-opens in Chromium

Press Ctrl+C to stop safely.
"""

import time
import random
import threading
import os
import cv2
from flask import Flask, Response
import lgpio as GPIO
from adafruit_servokit import ServoKit
import RPi.GPIO as RPiGPIO
from gpiozero import DigitalInputDevice

# ============================================================
#   DC MOTOR (Wheel) Setup
# ============================================================
DIR1, PWM1 = 17, 18   # Left motor
DIR2, PWM2 = 22, 23   # Right motor

RPiGPIO.setmode(RPiGPIO.BCM)
RPiGPIO.setup(DIR1, RPiGPIO.OUT)
RPiGPIO.setup(PWM1, RPiGPIO.OUT)
RPiGPIO.setup(DIR2, RPiGPIO.OUT)
RPiGPIO.setup(PWM2, RPiGPIO.OUT)

pwm1 = RPiGPIO.PWM(PWM1, 1000)
pwm2 = RPiGPIO.PWM(PWM2, 1000)
pwm1.start(0)
pwm2.start(0)

def wheel_loop():
    """Continuously move wheels forward/backward and turn."""
    try:
        while True:
            print("🚗 Moving forward")
            RPiGPIO.output(DIR1, RPiGPIO.HIGH)
            RPiGPIO.output(DIR2, RPiGPIO.HIGH)
            pwm1.ChangeDutyCycle(60)
            pwm2.ChangeDutyCycle(60)
            time.sleep(3)

            print("🛑 Stop")
            pwm1.ChangeDutyCycle(0)
            pwm2.ChangeDutyCycle(0)
            time.sleep(1)

            print("🔙 Moving backward")
            RPiGPIO.output(DIR1, RPiGPIO.LOW)
            RPiGPIO.output(DIR2, RPiGPIO.LOW)
            pwm1.ChangeDutyCycle(60)
            pwm2.ChangeDutyCycle(60)
            time.sleep(3)

            print("🛑 Stop")
            pwm1.ChangeDutyCycle(0)
            pwm2.ChangeDutyCycle(0)
            time.sleep(1)

            print("↪️ Turn Left")
            RPiGPIO.output(DIR1, RPiGPIO.LOW)
            RPiGPIO.output(DIR2, RPiGPIO.HIGH)
            pwm1.ChangeDutyCycle(60)
            pwm2.ChangeDutyCycle(60)
            time.sleep(2)

            print("↩️ Turn Right")
            RPiGPIO.output(DIR1, RPiGPIO.HIGH)
            RPiGPIO.output(DIR2, RPiGPIO.LOW)
            pwm1.ChangeDutyCycle(60)
            pwm2.ChangeDutyCycle(60)
            time.sleep(2)

            print("🛑 Stop")
            pwm1.ChangeDutyCycle(0)
            pwm2.ChangeDutyCycle(0)
            time.sleep(1)

    except Exception as e:
        print(f"Wheel loop error: {e}")

# ============================================================
#   ULTRASONIC SENSOR (HC-SR04)
# ============================================================
TRIG, ECHO = 26, 6
h = GPIO.gpiochip_open(0)
GPIO.gpio_claim_output(h, TRIG)
GPIO.gpio_claim_input(h, ECHO)

def get_distance():
    GPIO.gpio_write(h, TRIG, 0)
    time.sleep(0.05)
    GPIO.gpio_write(h, TRIG, 1)
    time.sleep(0.00001)
    GPIO.gpio_write(h, TRIG, 0)
    pulse_start = time.time()
    timeout = pulse_start + 0.05

    while GPIO.gpio_read(h, ECHO) == 0:
        pulse_start = time.time()
        if time.time() > timeout:
            return None
    while GPIO.gpio_read(h, ECHO) == 1:
        pulse_end = time.time()
        if time.time() > timeout:
            return None

    duration = pulse_end - pulse_start
    distance = duration * 17150
    return round(distance, 2)

def ultrasonic_loop():
    try:
        while True:
            d = get_distance()
            if d:
                print(f"📏 Distance: {d} cm")
            else:
                print("⚠️ Ultrasonic timeout")
            time.sleep(0.5)
    except Exception as e:
        print(f"Ultrasonic error: {e}")

# ============================================================
#   SERVOS (PCA9685)
# ============================================================
kit = ServoKit(channels=16)
CHANNELS = [12, 13, 14, 15]

def random_throttle():
    return round(random.uniform(-1.0, 1.0), 2)

def random_duration():
    return round(random.uniform(0.2, 2.5), 2)

def servo_random_loop():
    try:
        while True:
            active = random.sample(CHANNELS, random.randint(1, len(CHANNELS)))
            print(f"\n⚙️ Active servos: {active}")
            for ch in active:
                t = random_throttle()
                kit.continuous_servo[ch].throttle = t
                print(f"  Servo {ch}: throttle={t}")
            time.sleep(random_duration())
    except Exception as e:
        print(f"Servo loop error: {e}")

# ============================================================
#   IR SENSORS (GPIO 16 & 21)
# ============================================================
ir_sensor_1 = DigitalInputDevice(16)
ir_sensor_2 = DigitalInputDevice(21)

def ir_loop():
    try:
        while True:
            s1 = "LIGHT" if ir_sensor_1.value else "DARK"
            s2 = "LIGHT" if ir_sensor_2.value else "DARK"
            print(f"👁️ IR1(GPIO16): {s1} | IR2(GPIO21): {s2}")
            time.sleep(0.3)
    except Exception as e:
        print(f"IR sensor error: {e}")

# ============================================================
#   FLASK CAMERA STREAM
# ============================================================
app = Flask(__name__)
camera = cv2.VideoCapture(0)

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
    """Wait briefly, then open Chromium at the stream URL."""
    time.sleep(2)
    print("🌐 Launching Chromium browser...")
    os.system("chromium-browser http://127.0.0.1:8000 &")

def flask_loop():
    """Run Flask server for live camera streaming."""
    threading.Thread(target=open_chromium, daemon=True).start()
    print("🎥 Starting Flask camera stream...")
    print("Your live video will open shortly in Chromium (http://127.0.0.1:8000)\n")
    app.run(host='0.0.0.0', port=8000, threaded=True)

# ============================================================
#   MAIN PROGRAM
# ============================================================
if __name__ == "__main__":
    try:
        print("🎯 Starting All Systems (Motors + Servos + Ultrasonic + IR + Camera)")
        print("Press Ctrl+C to stop.\n")

        threads = [
            threading.Thread(target=wheel_loop, daemon=True),
            threading.Thread(target=ultrasonic_loop, daemon=True),
            threading.Thread(target=servo_random_loop, daemon=True),
            threading.Thread(target=ir_loop, daemon=True),
            threading.Thread(target=flask_loop, daemon=True),
        ]

        for t in threads:
            t.start()

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")

    finally:
        pwm1.stop()
        pwm2.stop()
        RPiGPIO.cleanup()
        for ch in CHANNELS:
            kit.continuous_servo[ch].throttle = 0
        GPIO.gpiochip_close(h)
        camera.release()
        print("✅ Clean exit. All systems stopped.")

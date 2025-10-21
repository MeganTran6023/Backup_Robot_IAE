"""
Combined Servo (PCA9685) and Ultrasonic Sensor Test
---------------------------------------------------
- Channels 12–15 run at random throttle ranges and times.
- Ultrasonic sensor continuously reports distance.
- Loop runs until user stops with Ctrl+C.
"""

import random
import time
import threading
from adafruit_servokit import ServoKit
import lgpio as GPIO

# -----------------------------
# Servo Setup
# -----------------------------
kit = ServoKit(channels=16)
CHANNELS = [12, 13, 14, 15]

# -----------------------------
# Ultrasonic Sensor Setup
# -----------------------------
TRIG = 26  # GPIO pin for TRIG
ECHO = 6   # GPIO pin for ECHO
h = GPIO.gpiochip_open(0)
GPIO.gpio_claim_output(h, TRIG)
GPIO.gpio_claim_input(h, ECHO)


def get_distance():
    """Measure distance using the HC-SR04 ultrasonic sensor"""
    GPIO.gpio_write(h, TRIG, 0)
    time.sleep(0.05)

    GPIO.gpio_write(h, TRIG, 1)
    time.sleep(0.00001)
    GPIO.gpio_write(h, TRIG, 0)

    pulse_start = time.time()
    timeout = pulse_start + 0.05  # safety timeout

    while GPIO.gpio_read(h, ECHO) == 0:
        pulse_start = time.time()
        if time.time() > timeout:
            return None

    while GPIO.gpio_read(h, ECHO) == 1:
        pulse_end = time.time()
        if time.time() > timeout:
            return None

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # cm
    return round(distance, 2)


def ultrasonic_loop():
    """Continuously measure distance in background"""
    try:
        while True:
            dist = get_distance()
            if dist is not None:
                print(f"📏 Distance: {dist:.2f} cm")
            else:
                print("⚠️  Ultrasonic timeout or out of range")
            time.sleep(0.5)
    except Exception as e:
        print(f"Ultrasonic thread error: {e}")


# -----------------------------
# Random Servo Motion
# -----------------------------
def random_throttle():
    return round(random.uniform(-1.0, 1.0), 2)

def random_duration():
    return round(random.uniform(0.2, 2.5), 2)

def servo_random_loop():
    """Continuously move servos in random combinations"""
    try:
        while True:
            active_channels = random.sample(CHANNELS, random.randint(1, len(CHANNELS)))
            print(f"\n⚙️ Active channels: {active_channels}")

            for ch in active_channels:
                throttle = random_throttle()
                kit.continuous_servo[ch].throttle = throttle
                print(f"  CH {ch}: throttle={throttle}")

            duration = random_duration()
            print(f"⏱️ Holding for {duration}s...")
            time.sleep(duration)

            if random.random() < 0.4:
                stop_ch = random.choice(CHANNELS)
                kit.continuous_servo[stop_ch].throttle = 0
                print(f"🛑 Stopped CH {stop_ch}")

            time.sleep(random.uniform(0.1, 0.5))
    except Exception as e:
        print(f"Servo thread error: {e}")


# -----------------------------
# Main Program
# -----------------------------
if __name__ == '__main__':
    try:
        print("🎯 Starting Combined Servo + Ultrasonic Test")
        print("Press Ctrl+C to exit.\n")

        # Start ultrasonic sensor in a background thread
        ultrasonic_thread = threading.Thread(target=ultrasonic_loop, daemon=True)
        ultrasonic_thread.start()

        # Run servo random loop in main thread
        servo_random_loop()

    except KeyboardInterrupt:
        print("\n🛑 Test stopped by user.")
    finally:
        # Stop all servos
        for ch in CHANNELS:
            kit.continuous_servo[ch].throttle = 0
        GPIO.gpiochip_close(h)
        print("✅ Clean exit. All servos stopped.")

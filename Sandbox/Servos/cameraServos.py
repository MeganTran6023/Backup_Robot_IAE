import threading
import random
from time import sleep
from adafruit_servokit import ServoKit

# Initialize the kit (16-channel board)
kit = ServoKit(channels=16)

def smooth_random_sweep(ch, step=0.05, delay=0.05):
    """Continuously sweep a servo channel smoothly to random throttle values between -1 and 1."""
    current = 0.0
    kit.continuous_servo[ch].throttle = current
    
    while True:
        target = random.uniform(-1, 1)  # New random target
        # Gradually move toward the target
        while abs(current - target) > step:
            if current < target:
                current += step
            else:
                current -= step
            kit.continuous_servo[ch].throttle = current
            sleep(delay)
        # Ensure final position exactly matches the target
        current = target
        kit.continuous_servo[ch].throttle = current
        sleep(delay)

# Create threads for both servos
thread0 = threading.Thread(target=smooth_random_sweep, args=(0,), daemon=True)
thread1 = threading.Thread(target=smooth_random_sweep, args=(1,), daemon=True)

# Start threads
thread0.start()
thread1.start()

# Keep the main program running
try:
    while True:
        sleep(1)
except KeyboardInterrupt:
    kit.continuous_servo[0].throttle = 0
    kit.continuous_servo[1].throttle = 0
    print("\n🛑 Stopped all servos safely.")

# Here we will import all the extra functionality desired
from time import sleep
from adafruit_servokit import ServoKit

# Initialize the ServoKit for 16 channels on the PCA9685
kit = ServoKit(channels=16)

print("Starting servo scan test (channels 0–15)...")
print("Each servo will move briefly if connected.\nPress Ctrl+C to stop.\n")

try:
    while True:
        for ch in range(16):
            print(f"Testing channel {ch}...")

            # Stop (neutral)
            kit.continuous_servo[ch].throttle = 0
            sleep(0.5)

            # Rotate clockwise at full speed
            kit.continuous_servo[ch].throttle = 1
            sleep(1)

            # Stop
            kit.continuous_servo[ch].throttle = 0
            sleep(0.5)

            # Rotate counter-clockwise at half speed
            kit.continuous_servo[ch].throttle = -0.5
            sleep(1)

            # Stop again
            kit.continuous_servo[ch].throttle = 0
            sleep(0.5)

        print("\nFinished one full sweep through all channels. Looping again...\n")
        sleep(2)

except KeyboardInterrupt:
    print("\nTest stopped by user. All servos off.")
    for ch in range(16):
        kit.continuous_servo[ch].throttle = 0

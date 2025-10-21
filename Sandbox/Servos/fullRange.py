from time import sleep
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)

print("Starting full throttle sweep test (channels 0–15)...")
print("Each servo will gradually sweep from -1 → +1 → -1.\nPress Ctrl+C to stop.\n")

try:
    while True:
        for ch in range(16):
            print(f"Sweeping throttle on channel {ch}...")

            # Sweep from -1 to +1
            for t in [x/20 for x in range(-20, 21)]:  # -1.0 to +1.0 in 0.1 steps
                kit.continuous_servo[ch].throttle = t
                sleep(0.05)

            # Sweep back from +1 to -1
            for t in [x/20 for x in range(20, -21, -1)]:
                kit.continuous_servo[ch].throttle = t
                sleep(0.05)

            # Stop
            kit.continuous_servo[ch].throttle = 0
            print(f"Finished channel {ch}")
            sleep(0.5)

        print("\nCompleted one full sweep through all channels.\n")
        sleep(1)

except KeyboardInterrupt:
    print("\nTest stopped by user. All servos off.")
    for ch in range(16):
        kit.continuous_servo[ch].throttle = 0

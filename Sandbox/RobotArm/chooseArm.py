# Import required libraries
from time import sleep
from adafruit_servokit import ServoKit

# Initialize the ServoKit for 16 channels on the PCA9685
kit = ServoKit(channels=16)

print("Servo Channel Test (Channels 12–15)")
print("------------------------------------")
print("You can test individual channels (12, 13, 14, 15) or multiple ones separated by commas.")
print("Example: 12 or 12,13,15")
print("Press Ctrl+C to stop at any time.\n")

try:
    # Ask user which channels to test
    user_input = input("Enter the channel numbers to test (12–15): ").strip()
    channels = [int(ch.strip()) for ch in user_input.split(",") if ch.strip().isdigit()]

    # Validate channel numbers
    channels = [ch for ch in channels if 12 <= ch <= 15]
    if not channels:
        print("No valid channels selected (must be between 12 and 15). Exiting.")
        exit(0)

    print(f"\nTesting channels: {channels}\n")

    while True:
        for ch in channels:
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

        print("\nFinished one full sweep through selected channels. Looping again...\n")
        sleep(2)

except KeyboardInterrupt:
    print("\nTest stopped by user. All servos off.")
    for ch in range(12, 16):
        kit.continuous_servo[ch].throttle = 0

# Import required libraries
from time import sleep
from adafruit_servokit import ServoKit

# Initialize the ServoKit for 16 channels on the PCA9685
kit = ServoKit(channels=16)

print("Simultaneous Servo Channel Test (Channels 12–15)")
print("------------------------------------------------")
print("You can test multiple channels at once, e.g.: 12,13,14,15")
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

    print(f"\nTesting channels simultaneously: {channels}\n")

    while True:
        print("→ Setting all to neutral (stop)")
        for ch in channels:
            kit.continuous_servo[ch].throttle = 0
        sleep(0.5)

        print("→ Rotating all clockwise (full speed)")
        for ch in channels:
            kit.continuous_servo[ch].throttle = 1
        sleep(1)

        print("→ Stopping all")
        for ch in channels:
            kit.continuous_servo[ch].throttle = 0
        sleep(0.5)

        print("→ Rotating all counter-clockwise (half speed)")
        for ch in channels:
            kit.continuous_servo[ch].throttle = -0.5
        sleep(1)

        print("→ Stopping all again")
        for ch in channels:
            kit.continuous_servo[ch].throttle = 0
        sleep(0.5)

        print("\nFinished one full motion cycle. Looping again...\n")
        sleep(2)

except KeyboardInterrupt:
    print("\nTest stopped by user. All servos off.")
    for ch in range(12, 16):
        kit.continuous_servo[ch].throttle = 0

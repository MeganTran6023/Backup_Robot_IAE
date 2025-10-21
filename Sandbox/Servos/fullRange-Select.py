from time import sleep
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)

print("🧭 Interactive Continuous Servo Test")
print("-----------------------------------")
print("Select a channel number (0–15) to test.")
print("Type 'c' at any time to choose another channel.")
print("Press Ctrl+C to exit.\n")

def sweep_channel(ch):
    """Sweep a continuous rotation servo from -1 → +1 → -1"""
    print(f"\n⚙️ Sweeping channel {ch}...")
    
    # Sweep from -1.0 to +1.0
    for t in [x / 20 for x in range(-20, 21)]:
        kit.continuous_servo[ch].throttle = t
        sleep(0.05)

    # Sweep back from +1.0 to -1.0
    for t in [x / 20 for x in range(20, -21, -1)]:
        kit.continuous_servo[ch].throttle = t
        sleep(0.05)

    # Stop
    kit.continuous_servo[ch].throttle = 0
    print(f"✅ Finished sweep on channel {ch}.\n")

try:
    while True:
        # Channel selection
        user_input = input("Enter a channel (0–15) to test: ").strip()
        if not user_input.isdigit() or not (0 <= int(user_input) < 16):
            print("❌ Invalid input. Please enter a number between 0 and 15.\n")
            continue

        ch = int(user_input)

        print(f"\n🎯 Ready to test channel {ch}.")
        print("Type 'c' to change channel, or let it run repeatedly.\n")

        # Run until user types 'c'
        while True:
            sweep_channel(ch)
            next_action = input("Press Enter to repeat this channel or 'c' to change: ").strip().lower()
            if next_action == 'c':
                break  # go back to channel selection

except KeyboardInterrupt:
    print("\n🛑 Test stopped by user. Turning off all servos...")
    for ch in range(16):
        kit.continuous_servo[ch].throttle = 0
    print("All servos off. Goodbye!")

import random
from time import sleep
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)

print("🎲 Random Continuous Servo Test (channels 12–15)")
print("Each servo will run at random throttle levels and durations.")
print("Press Ctrl+C to stop.\n")

CHANNELS = [12, 13, 14, 15]

def random_throttle():
    """Generate a random throttle value between -1.0 and +1.0"""
    return round(random.uniform(-1.0, 1.0), 2)

def random_duration():
    """Random duration between 0.2 and 2.5 seconds"""
    return round(random.uniform(0.2, 2.5), 2)

try:
    while True:
        # Randomize which subset of channels to activate (1–4 at once)
        active_channels = random.sample(CHANNELS, random.randint(1, len(CHANNELS)))
        print(f"\n⚙️ Active channels: {active_channels}")

        # Assign a random throttle to each active servo
        for ch in active_channels:
            throttle = random_throttle()
            kit.continuous_servo[ch].throttle = throttle
            print(f"  CH {ch}: throttle={throttle}")

        # Hold this state for a random duration
        duration = random_duration()
        print(f"⏱️ Holding for {duration} seconds...")
        sleep(duration)

        # Occasionally stop one or more servos
        if random.random() < 0.4:  # 40% chance
            stop_channel = random.choice(CHANNELS)
            kit.continuous_servo[stop_channel].throttle = 0
            print(f"🛑 Stopped CH {stop_channel}")

        # Small random delay before next mix
        sleep(random.uniform(0.1, 0.5))

except KeyboardInterrupt:
    print("\n🛑 User interrupted. Stopping all servos...")
    for ch in CHANNELS:
        kit.continuous_servo[ch].throttle = 0
    print("✅ All servos off. Goodbye!")

from time import sleep
from adafruit_servokit import ServoKit

# Initialize the ServoKit for 16 channels
kit = ServoKit(channels=16)

# Replace this with your servo channel
claw_channel = 0

# Sweep range
MIN_ANGLE = 0
MAX_ANGLE = 100
STEP = 5      # change in degrees per step
DELAY = 0.05  # time to wait between steps in seconds

try:
    while True:
        # Sweep up from MIN_ANGLE to MAX_ANGLE
        for angle in range(MIN_ANGLE, MAX_ANGLE + 1, STEP):
            kit.servo[claw_channel].angle = angle
            sleep(DELAY)

        # Sweep down from MAX_ANGLE to MIN_ANGLE
        for angle in range(MAX_ANGLE, MIN_ANGLE - 1, -STEP):
            kit.servo[claw_channel].angle = angle
            sleep(DELAY)

except KeyboardInterrupt:
    print("\nStopping sweep. Servo at MIN_ANGLE.")
    kit.servo[claw_channel].angle = MIN_ANGLE

from time import sleep
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)
claw_channel = 0  # replace with your servo channel

# Sweep from 0 to 180
for angle in range(0, 181, 10):
    print(f"Angle: {angle}")
    kit.servo[claw_channel].angle = angle
    sleep(0.3)

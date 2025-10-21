import time
from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio

# Create I2C bus interface
i2c = busio.I2C(SCL, SDA)

# Create PCA9685 instance
pca = PCA9685(i2c)
pca.frequency = 50  # typical servo frequency

# Channel 15 = servo connector marked "15" on the board
channel = 15

def set_servo_pulse(channel, pulse_us):
    # 20 ms period (50 Hz)
    pulse_length = 1000000 / 50 / 4096  # us per bit
    value = int(pulse_us / pulse_length)
    pca.channels[channel].duty_cycle = value

try:
    print("Center position")
    set_servo_pulse(channel, 1500)
    time.sleep(2)

    print("Rotate forward")
    set_servo_pulse(channel, 1600)
    time.sleep(2)

    print("Rotate reverse")
    set_servo_pulse(channel, 1400)
    time.sleep(2)

    print("Center again")
    set_servo_pulse(channel, 1500)
    time.sleep(1)

finally:
    pca.deinit()

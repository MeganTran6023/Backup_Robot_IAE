import RPi.GPIO as GPIO
import time

# Pin setup
DIR1 = 17
PWM1 = 18
DIR2 = 22
PWM2 = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR1, GPIO.OUT)
GPIO.setup(PWM1, GPIO.OUT)
GPIO.setup(DIR2, GPIO.OUT)
GPIO.setup(PWM2, GPIO.OUT)

# Set up PWM at 1 kHz
pwm1 = GPIO.PWM(PWM1, 1000)
pwm2 = GPIO.PWM(PWM2, 1000)
pwm1.start(0)  # duty cycle = 0 (stopped)
pwm2.start(0)

try:
    print("Moving forward...")
    GPIO.output(DIR1, GPIO.HIGH)
    GPIO.output(DIR2, GPIO.HIGH)
    pwm1.ChangeDutyCycle(60)  # 60% speed
    pwm2.ChangeDutyCycle(60)
    time.sleep(3)

    print("Stopping...")
    pwm1.ChangeDutyCycle(0)
    pwm2.ChangeDutyCycle(0)
    time.sleep(1)

    print("Moving backward...")
    GPIO.output(DIR1, GPIO.LOW)
    GPIO.output(DIR2, GPIO.LOW)
    pwm1.ChangeDutyCycle(60)
    pwm2.ChangeDutyCycle(60)
    time.sleep(3)

    print("Stopping...")
    pwm1.ChangeDutyCycle(0)
    pwm2.ChangeDutyCycle(0)

finally:
    pwm1.stop()
    pwm2.stop()
    GPIO.cleanup()
    print("GPIO cleaned up.")

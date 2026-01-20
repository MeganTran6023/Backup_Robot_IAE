#!/usr/bin/python3
# coding=utf8

import sys
import time
import tty
import termios
from pathlib import Path

# =======================
# Add common SDK path
# =======================
common_sdk_root = Path('/home/megan/MasterPi/masterpi_sdk/common_sdk')
sys.path.append(str(common_sdk_root))

from common.ros_robot_controller_sdk import Board

board = Board()

if sys.version_info.major == 2:
    print("Please run with python3")
    sys.exit(0)

# =======================
# Constants
# =======================
MOVE_SPEED = 90
SLIDE_SPEED = 45
TURN_SPEED = 60
TURN_TIMEOUT = 0.15

ANGLE_STEP = 5
MIN_ANGLE = -90
MAX_ANGLE = 90

# =======================
# Servo reset angles (degrees)
# =======================
servo_angle = {
    1: 10,     # Claw
    3: -80,    # Joint 1
    4: 80,     # Joint 2
    5: -90,    # Joint 3
    6: 0       # Rotate claw
}

# =======================
# State
# =======================
last_turn_time = 0.0
active_motion = None

# =======================
# Raw key reader
# =======================
def get_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch1 = sys.stdin.read(1)
        if ch1 == '\x1b':
            ch2 = sys.stdin.read(1)
            if ch2 == '[':
                ch3 = sys.stdin.read(1)
                if ch3 == '1':
                    sys.stdin.read(2)
                    ch6 = sys.stdin.read(1)
                    return '\x1b[1;2' + ch6
                return '\x1b[' + ch3
        return ch1
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

# =======================
# Motor helpers
# =======================
def stop_motors():
    board.set_motor_duty([[1,0],[2,0],[3,0],[4,0]])

def move_forward():
    board.set_motor_duty([[1,MOVE_SPEED],[2,MOVE_SPEED],[3,-MOVE_SPEED],[4,-MOVE_SPEED]])

def move_backward():
    board.set_motor_duty([[1,-MOVE_SPEED],[2,-MOVE_SPEED],[3,MOVE_SPEED],[4,MOVE_SPEED]])

def slide_left():
    board.set_motor_duty([[1,SLIDE_SPEED],[2,-SLIDE_SPEED],[3,-SLIDE_SPEED],[4,SLIDE_SPEED]])

def slide_right():
    board.set_motor_duty([[1,-SLIDE_SPEED],[2,SLIDE_SPEED],[3,SLIDE_SPEED],[4,-SLIDE_SPEED]])

def turn_left():
    board.set_motor_duty([[1,TURN_SPEED],[3,TURN_SPEED]])

def turn_right():
    board.set_motor_duty([[2,-TURN_SPEED],[4,-TURN_SPEED]])

# =======================
# Servo helpers
# =======================
def angle_to_pulse(angle):
    angle = max(MIN_ANGLE, min(MAX_ANGLE, angle))
    return int(1500 + angle * (1000 / 90))

def update_servos():
    board.pwm_servo_set_position(
        0.05,
        [[s, angle_to_pulse(servo_angle[s])] for s in servo_angle]
    )

def reset_servos():
    update_servos()

# =======================
# Startup reset
# =======================
reset_servos()

print("""
========================================
 Unified Robot Keyboard Control
========================================
↑  : Forward (toggle) - PRESS again to turn off
↓  : Backward (toggle) - PRESS again to turn off
←  : Slide Left (toggle) - PRESS again to turn off
→  : Slide Right (toggle) - PRESS again to turn off

Shift + ← : Turn Left (hold) - press E to turn off
Shift + → : Turn Right (hold) - press E to turn off


q : Quit
========================================
""")

try:
    while True:
        key = get_key()
        now = time.time()

        if key == 'q':
            break

        # Turning (priority)
        if key == '\x1b[1;2D':
            turn_left()
            last_turn_time = now
            continue


        if key == '\x1b[1;2C':
            turn_right()
            last_turn_time = now
            continue

        # Directional toggles
        if key == '\x1b[A':
            active_motion = None if active_motion == 'forward' else 'forward'
        elif key == '\x1b[B':
            active_motion = None if active_motion == 'backward' else 'backward'
        elif key == '\x1b[D':
            active_motion = None if active_motion == 'left' else 'left'
        elif key == '\x1b[C':
            active_motion = None if active_motion == 'right' else 'right'

        if active_motion == 'forward':
            move_forward()
        elif active_motion == 'backward':
            move_backward()
        elif active_motion == 'left':
            slide_left()
        elif active_motion == 'right':
            slide_right()
        else:
            stop_motors()

        # Servo controls (no output)
        if key == '1': servo_angle[1] -= ANGLE_STEP
        elif key == '2': servo_angle[1] += ANGLE_STEP
        elif key == '3': servo_angle[3] -= ANGLE_STEP
        elif key == '4': servo_angle[3] += ANGLE_STEP
        elif key == '5': servo_angle[4] -= ANGLE_STEP
        elif key == '6': servo_angle[4] += ANGLE_STEP
        elif key == '7': servo_angle[5] -= ANGLE_STEP
        elif key == '8': servo_angle[5] += ANGLE_STEP
        elif key == '9': servo_angle[6] -= ANGLE_STEP
        elif key == '0': servo_angle[6] += ANGLE_STEP
        else:
            continue

        for s in servo_angle:
            servo_angle[s] = max(MIN_ANGLE, min(MAX_ANGLE, servo_angle[s]))

        update_servos()

        if now - last_turn_time > TURN_TIMEOUT and active_motion is None:
            stop_motors()

except KeyboardInterrupt:
    pass
finally:
    stop_motors()
    reset_servos()

#!/usr/bin/python3
# coding=utf8

import sys
from pathlib import Path
import time
import tty
import termios

# =======================
# Add common SDK path
# =======================
common_sdk_root = Path('/home/megan/MasterPi/masterpi_sdk/common_sdk')
sys.path.append(str(common_sdk_root))

from common.ros_robot_controller_sdk import Board

# =======================
# Initialize board
# =======================
board = Board()

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

print('''
========================================
 Slide Control (Hold BOTH keys)
========================================
 Hold Shift + Left  : Slide Left
 Hold Shift + Right : Slide Right
 Release either key : Stop
 Press q to quit
========================================
''')

MOTOR_SPEED = 45
TURN_TIMEOUT = 0.15  # seconds

last_turn_time = 0.0

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
                if ch3 == '1':          # Shift + Arrow
                    sys.stdin.read(2)   # skip ";2"
                    ch6 = sys.stdin.read(1)
                    return '\x1b[1;2' + ch6
                return '\x1b[' + ch3
        return ch1
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

try:
    while True:
        key = get_key()
        now = time.time()

        if key == 'q':
            break

        # =======================
        # Move Side left (Shift + Left)
        # =======================
        if key == '\x1b[1;2D':
            board.set_motor_duty([[1, MOTOR_SPEED], [2, -MOTOR_SPEED],[3, -MOTOR_SPEED], [4, MOTOR_SPEED]])
            last_turn_time = now
            continue

        # =======================
        # Move Side right (Shift + Right)
        # =======================
        if key == '\x1b[1;2C':
            board.set_motor_duty([[1, -MOTOR_SPEED], [2, MOTOR_SPEED],[3, MOTOR_SPEED], [4, -MOTOR_SPEED]])
            last_turn_time = now
            continue

        # =======================
        # Stop if no valid combo recently
        # =======================
        if now - last_turn_time > TURN_TIMEOUT:
            board.set_motor_duty([[1, 0], [2, 0], [3, 0], [4, 0]])

except KeyboardInterrupt:
    pass
finally:
    board.set_motor_duty([[1, 0], [2, 0], [3, 0], [4, 0]])

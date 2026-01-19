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

# Now import works
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
 Motor Toggle Control
========================================
 Press UP arrow   : Move forward / Stop
 Press DOWN arrow : Move backward / Stop
 Press q          : Quit
========================================
''')

# =======================
# Motor parameters
# =======================
SPEED = 90
moving_forward = False
moving_backward = False

# =======================
# Raw key reader (no Enter)
# =======================
def get_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch1 = sys.stdin.read(1)
        if ch1 == '\x1b':       # ESC
            ch2 = sys.stdin.read(1)
            if ch2 == '[':
                ch3 = sys.stdin.read(1)
                return '\x1b[' + ch3
        return ch1
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

try:
    while True:
        key = get_key()

        # Quit
        if key == 'q':
            break

        # =======================
        # UP arrow toggle (forward)
        # =======================
        if key == '\x1b[A':
            if moving_forward:
                moving_forward = False
                board.set_motor_duty([[1, 0],[2, 0],[3, 0],[4, 0]])
                print("Forward stopped")
            else:
                moving_forward = True
                moving_backward = False  # stop backward if active
                board.set_motor_duty([[1, SPEED],[2, SPEED],[3, -SPEED],[4, -SPEED]])
                print("Moving forward")

        # =======================
        # DOWN arrow toggle (backward)
        # =======================
        elif key == '\x1b[B':
            if moving_backward:
                moving_backward = False
                board.set_motor_duty([[1, 0],[2, 0],[3, 0],[4, 0]])
                print("Backward stopped")
            else:
                moving_backward = True
                moving_forward = False  # stop forward if active
                board.set_motor_duty([[1, -SPEED],[2, -SPEED],[3, SPEED],[4, SPEED]])
                print("Moving backward")

except KeyboardInterrupt:
    pass
finally:
    # Stop all motors safely
    board.set_motor_duty([[1, 0],[2, 0],[3, 0],[4, 0]])

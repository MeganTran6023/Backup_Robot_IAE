#!/usr/bin/python3
# coding=utf8

'''
Move arm for bot
'''



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
**********************************************************
********************PWM舵机和电机测试************************
**********************************************************
----------------------------------------------------------
Official website:https://www.hiwonder.com
Online mall:https://hiwonder.tmall.com
----------------------------------------------------------
Tips:
 * 按下Ctrl+C可关闭此次程序运行，若失败请多次尝试！
----------------------------------------------------------
''')

# =======================
# Manual servo control
# =======================

servo_pos = {
    1: 1500,
    3: 695,
    4: 2215,
    5: 780,
    6: 1500
}

STEP = 50
MIN_PULSE = 500
MAX_PULSE = 2500

print('''
Key controls (no Enter needed):
 Servo 1: 1 (L) / 2 (R)
 Servo 3: 3 / 4
 Servo 4: 5 / 6
 Servo 5: 7 / 8
 Servo 6: 9 / 0
 Press q to quit
''')

def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        key = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return key

try:
    while True:
        key = get_key()

        if key == 'q':
            break

        elif key == '1':
            servo_pos[1] -= STEP
        elif key == '2':
            servo_pos[1] += STEP

        elif key == '3':
            servo_pos[3] -= STEP
        elif key == '4':
            servo_pos[3] += STEP

        elif key == '5':
            servo_pos[4] -= STEP
        elif key == '6':
            servo_pos[4] += STEP

        elif key == '7':
            servo_pos[5] -= STEP
        elif key == '8':
            servo_pos[5] += STEP

        elif key == '9':
            servo_pos[6] -= STEP
        elif key == '0':
            servo_pos[6] += STEP

        else:
            continue

        for s in servo_pos:
            servo_pos[s] = max(MIN_PULSE, min(MAX_PULSE, servo_pos[s]))

        board.pwm_servo_set_position(
            0.05,
            [[s, servo_pos[s]] for s in servo_pos]
        )

except KeyboardInterrupt:
    pass


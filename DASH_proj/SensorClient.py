# sensor_client.py (with print statements)
import socket
import time
import gpiod

SERVER_IP = '192.168.128.89'  # Replace with your laptop IP
PORT = 5001

CHIP = 'gpiochip0'
TRIG_LINE = 17
ECHO_LINE = 5

def wait_for_value(line, target, timeout=0.02):
    start = time.time()
    while line.get_value() != target:
        if time.time() - start > timeout:
            return False
    return True

def get_sonar_data():
    chip = gpiod.Chip(CHIP)
    trig = chip.get_line(TRIG_LINE)
    echo = chip.get_line(ECHO_LINE)
    trig.request(consumer='trig', type=gpiod.LINE_REQ_DIR_OUT)
    echo.request(consumer='echo', type=gpiod.LINE_REQ_DIR_IN)

    trig.set_value(0)
    time.sleep(0.05)

    trig.set_value(1)
    time.sleep(0.00001)
    trig.set_value(0)

    if not wait_for_value(echo, 1):
        chip.close()
        print("Timeout waiting for echo HIGH")
        return None

    pulse_start = time.time()

    if not wait_for_value(echo, 0):
        chip.close()
        print("Timeout waiting for echo LOW")
        return None

    pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    chip.close()
    return round(distance, 2)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print("Client: Connecting to server...")
    s.connect((SERVER_IP, PORT))
    print("Client: Connected.")
    while True:
        dist = get_sonar_data()
        if dist is not None:
            print(f"Client: Sending distance {dist} cm")
            s.sendall(str(dist).encode())
        else:
            print("Client: No distance data")
        time.sleep(1)

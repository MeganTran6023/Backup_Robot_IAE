"""
Publisher for IR sensor data using ZeroMQ and BSON.
Runs on Raspberry Pi 5 with IR sensor on GPIO 14 (BCM).
"""

import time
import zmq
import lgpio
from bson import BSON

class IRSensorPublisher:
    """
    Publisher class for transmitting IR sensor state over ZeroMQ using BSON.
    """

    def __init__(self, gpio_pin=14, chip=0, zmq_port=5556, topic=b"sensor/ir"):
        """
        Initialize the IR sensor publisher.

        :param gpio_pin: BCM GPIO pin where the IR sensor is connected.
        :param chip: GPIO chip number (typically 0 for gpiochip0).
        :param zmq_port: TCP port for ZeroMQ PUB socket.
        :param topic: Topic name in bytes for publishing messages.
        """
        self.gpio_pin = gpio_pin
        self.chip = chip
        self.zmq_port = zmq_port
        self.topic = topic

        # GPIO setup
        self.gpio_handle = lgpio.gpiochip_open(self.chip)
        lgpio.gpio_claim_input(self.gpio_handle, self.gpio_pin)

        # ZeroMQ setup
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(f"tcp://*:{self.zmq_port}")

    def read_sensor(self):
        """
        Read the current state of the IR sensor.

        :return: 0 or 1 depending on sensor state.
        """
        return lgpio.gpio_read(self.gpio_handle, self.gpio_pin)

    def build_message(self, sensor_state):
        """
        Build a BSON message from the sensor state.

        :param sensor_state: Current state of the sensor (0 or 1).
        :return: BSON-encoded message as bytes.
        """
        payload = {
            "timestamp": time.time(),
            "sensor": "IR",
            "state": sensor_state
        }
        return BSON.encode(payload)

    def publish_message(self, message):
        """
        Publish a BSON message over the ZeroMQ PUB socket.

        :param message: BSON-encoded message bytes.
        """
        self.socket.send_multipart([self.topic, message])

    def run(self, interval=1):
        """
        Continuously read sensor data and publish messages at given interval.

        :param interval: Time in seconds between sensor reads.
        """
        print("Starting IR sensor publisher. Press Ctrl+C to exit.")
        try:
            while True:
                state = self.read_sensor()
                message = self.build_message(state)
                self.publish_message(message)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nExiting...")
        finally:
            self.cleanup()

    def cleanup(self):
        """
        Release GPIO and ZeroMQ resources.
        """
        lgpio.gpiochip_close(self.gpio_handle)
        self.socket.close()
        self.context.term()

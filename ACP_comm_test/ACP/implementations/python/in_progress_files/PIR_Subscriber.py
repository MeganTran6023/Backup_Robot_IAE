"""
Subscriber for IR sensor data using ZeroMQ and BSON.
Connects to a PUB socket on TCP port 5556 and subscribes to "sensor/ir".
"""

import zmq
from bson import BSON

class IRSensorSubscriber:
    """
    Subscriber class for receiving IR sensor state over ZeroMQ using BSON.
    """

    def __init__(self, zmq_address="tcp://localhost:5556", topic=b"sensor/ir"):
        """
        Initialize the subscriber.

        :param zmq_address: Address of the PUB socket to connect to.
        :param topic: Topic name in bytes to subscribe to.
        """
        self.zmq_address = zmq_address
        self.topic = topic

        # ZeroMQ setup
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect(self.zmq_address)
        self.socket.setsockopt(zmq.SUBSCRIBE, self.topic)

    def receive_message(self):
        """
        Receive a single message from the PUB socket.

        :return: tuple of (topic, decoded payload dict)
        """
        topic, payload = self.socket.recv_multipart()
        data = BSON(payload).decode()
        return topic.decode(), data

    def run(self):
        """
        Continuously listen for messages and print the decoded sensor data.
        """
        print("Subscriber started. Waiting for BSON messages...")
        try:
            while True:
                topic, data = self.receive_message()
                print(f"[{topic}] {data}")
        except KeyboardInterrupt:
            print("\nSubscriber exiting...")
        finally:
            self.cleanup()

    def cleanup(self):
        """
        Close ZeroMQ resources.
        """
        self.socket.close()
        self.context.term()


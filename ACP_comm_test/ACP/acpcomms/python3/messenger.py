"""
Messenger - ZeroMQ messaging wrapper with internal BSON serialization.
Publisher/subscriber scripts do NOT need bson, json, or zmq imports.
"""

import zmq
import threading
from typing import Dict, Any, Callable, Optional

# Keep your original package structure
from .acp_comms import ACPComms

# Internal serialization
from bson import dumps as bson_dumps, loads as bson_loads
import json


class Messenger(ACPComms):
    """ZeroMQ-based messaging implementation with automatic BSON serialization/deserialization."""

    def __init__(self):
        super().__init__()
        self.context: Optional[zmq.Context] = None
        self.socket: Optional[zmq.Socket] = None
        self.endpoint: str = ""
        self.socketType: int = zmq.SUB
        self.listenerThread: Optional[threading.Thread] = None
        self.listening: bool = False
        self.messageHandler: Optional[Callable[[dict], None]] = None

        # ------------------------------------------------------------------
        # Default JSON message template
        # Industry-standard: centrally defined to avoid duplication
        # Publishers may override fields when sending messages
        # ------------------------------------------------------------------
        self.messageTemplate: Dict[str, Any] = {
            "sensor_id": None,
            "sensor_type": None,
            "data_type": None,
            "timestamp": None,
            "location": {
                "lat": None,
                "lon": None
            },
            "metadata": {
                "units": None,
                "schema_version": "1.0",
                "tags": []
            },
            "data": {}
        }

    # -----------------------------
    # Configure ZMQ socket
    # -----------------------------
    def configure(self, configuration: Dict[str, Any]) -> None:
        self.config.update(configuration)

        self.endpoint = self.config.get("endpoint", "tcp://localhost:5555")
        socket_type_str = self.config.get("socketType", "SUB")

        socket_type_map = {
            "PUB": zmq.PUB,
            "SUB": zmq.SUB,
            "REQ": zmq.REQ,
            "REP": zmq.REP,
            "PUSH": zmq.PUSH,
            "PULL": zmq.PULL
        }

        if socket_type_str not in socket_type_map:
            raise ValueError(f"Invalid socket type: {socket_type_str}")

        self.socketType = socket_type_map[socket_type_str]

    # -----------------------------
    # Connect / Disconnect
    # -----------------------------
    def connect(self) -> None:
        if self.connected:
            raise RuntimeError("Already connected")

        self.context = zmq.Context()
        self.socket = self.context.socket(self.socketType)

        if self.config.get("bind", False):
            self.socket.bind(self.endpoint)
        else:
            self.socket.connect(self.endpoint)

        if self.socketType == zmq.SUB:
            topic = self.config.get("topic", "")
            self.socket.subscribe(topic.encode())

        self.connected = True

    def disconnect(self) -> None:
        if not self.connected:
            return

        self.stopListener()

        if self.socket:
            self.socket.close()
        if self.context:
            self.context.term()

        self.connected = False

    # -----------------------------
    # Internal serialization helpers
    # -----------------------------
    def serialize(self, obj: dict) -> bytes:
        """dict → BSON bytes"""
        return bson_dumps(obj)

    def deserialize(self, data: bytes) -> dict:
        """BSON bytes → dict"""
        return bson_loads(data)

    def deserialize_to_json(self, data: bytes) -> str:
        """BSON bytes → JSON string"""
        return json.dumps(self.deserialize(data))

    # -----------------------------
    # Message Template
    # -----------------------------
    def setTemplate(self, jsonTemplate: Dict[str, Any]) -> None:
        # Industry-standard: allow template replacement if needed
        self.messageTemplate = jsonTemplate

    def getTemplate(self) -> Dict[str, Any]:
        """Return a copy of the current template for publishers."""
        return self.messageTemplate.copy()

    def sendMessageTemplate(self, **kwargs):
        if self.messageTemplate is None:
            raise ValueError("Message template not set")

        # Industry-standard: merge template defaults with overrides
        populated = json.loads(json.dumps(self.messageTemplate))  # deep copy
        populated.update(kwargs)

        bson_bytes = self.serialize(populated)
        self.sendMessage(bson_bytes)

    # -----------------------------
    # Raw send/receive
    # -----------------------------
    def sendMessage(self, message: bytes) -> None:
        if not self.connected:
            raise RuntimeError("Not connected")
        self.socket.send(message)

    def receiveMessage(self) -> bytes:
        if not self.connected:
            raise RuntimeError("Not connected")
        return self.socket.recv()

    def receiveMessageObject(self) -> dict:
        return self.deserialize(self.receiveMessage())

    # -----------------------------
    # Background listener
    # -----------------------------
    def setMessageHandler(self, handler: Callable[[dict], None]) -> None:
        """Handler receives **Python dict**, not raw bytes."""
        self.messageHandler = handler

    def startListener(self) -> None:
        if not self.connected:
            raise RuntimeError("Not connected")
        if self.listening:
            raise RuntimeError("Listener already running")

        self.listening = True

        def loop():
            while self.listening:
                try:
                    raw = self.socket.recv()

                    json_string = self.deserialize_to_json(raw)

                    if self.messageHandler:
                        self.messageHandler(json_string)

                except Exception as e:
                    if self.listening:
                        print("Error receiving:", e)

        self.listenerThread = threading.Thread(target=loop, daemon=True)
        self.listenerThread.start()

    def stopListener(self) -> None:
        self.listening = False
        if self.listenerThread:
            self.listenerThread.join(timeout=1.0)

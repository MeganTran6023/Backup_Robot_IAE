"""
Streamer - UDP-based streaming implementation
Uses Python standard library (socket module)
"""
import socket
import threading
from typing import Dict, Any, Callable, Optional, Tuple
from .acp_comms import ACPComms

# ADDED: optional BSON + checksum helpers used by sender/receiver
import zlib
from bson import BSON


class DatagramPacket:
    """
    Wrapper class to mimic Java's DatagramPacket
    Created to maintain interface compatibility
    """
    def __init__(self, data: bytes, address: Tuple[str, int]):
        self.data = data
        self.address = address
        self.length = len(data)
    
    def getData(self) -> bytes:
        """Get packet data"""
        return self.data
    
    def getAddress(self) -> Tuple[str, int]:
        """Get source address as (host, port) tuple"""
        return self.address
    
    def getLength(self) -> int:
        """Get data length"""
        return self.length


class Streamer(ACPComms):
    """UDP-based streaming implementation"""
    
    def __init__(self):
        super().__init__()
        self.socket: Optional[socket.socket] = None
        self.address: str = ""
        self.port: int = 0
        self.listenerThread: Optional[threading.Thread] = None
        self.listening: bool = False
        self.packetHandler: Optional[Callable[[DatagramPacket], None]] = None
        self.bufferSize: int = 8192
    
    def configure(self, configuration: Dict[str, Any]) -> None:
        """
        Configure the streamer
        """
        self.config.update(configuration)
        
        host = self.config.get("host", "localhost")
        self.port = self.config.get("port", 9999)
        self.address = host
        self.bufferSize = self.config.get("bufferSize", 8192)
        
        local_port = self.config.get("localPort")
        if local_port is not None and self.socket is None:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind(("", local_port))
    
    def connect(self) -> None:
        """Initialize UDP socket"""
        if self.connected:
            raise RuntimeError("Already connected")
        
        if self.socket is None:
            local_port = self.config.get("localPort")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            if local_port is not None:
                self.socket.bind(("", local_port))
        
        timeout = self.config.get("timeout")
        if timeout is not None:
            self.socket.settimeout(timeout / 1000.0)
        
        self.connected = True
    
    def disconnect(self) -> None:
        """Close UDP socket"""
        if not self.connected:
            return
        
        self.stopListener()
        
        if self.socket is not None:
            self.socket.close()
        
        self.connected = False
    
    def sendData(self, data: bytes) -> None:
        """Send raw UDP data"""
        if not self.connected:
            raise RuntimeError("Not connected")
        self.socket.sendto(data, (self.address, self.port))
    
    # ADDED: BSON metadata sender
    def sendBson(self, payload: dict) -> None:
        """Serialize dict to BSON and send"""
        self.sendData(BSON.encode(payload))
    
    # ADDED: JPEG chunk sender with checksum
    def sendChunkWithChecksum(self, chunk: bytes) -> None:
        """Send binary chunk with CRC32 checksum"""
        checksum = zlib.crc32(chunk)
        packet = chunk + checksum.to_bytes(4, byteorder="big")
        self.sendData(packet)
    
    def receiveData(self) -> DatagramPacket:
        """Receive data via UDP"""
        if not self.connected:
            raise RuntimeError("Not connected")
        data, addr = self.socket.recvfrom(self.bufferSize)
        return DatagramPacket(data, addr)
    
    # ADDED: BSON decoder helper
    def tryDecodeBson(self, data: bytes) -> Optional[dict]:
        """Attempt BSON decode, return None if not BSON"""
        try:
            return BSON(data).decode()
        except Exception:
            return None
    
    def setPacketHandler(self, handler: Callable[[DatagramPacket], None]) -> None:
        """Set packet handler callback"""
        self.packetHandler = handler
    
    def startListener(self) -> None:
        """Start listening for packets in a background thread"""
        if not self.connected:
            raise RuntimeError("Not connected")
        if self.listening:
            raise RuntimeError("Listener already running")
        
        self.listening = True
        
        def listener_loop():
            while self.listening:
                try:
                    data, addr = self.socket.recvfrom(self.bufferSize)
                    packet = DatagramPacket(data, addr)
                    if self.packetHandler is not None:
                        self.packetHandler(packet)
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.listening:
                        print(f"Error receiving packet: {e}", flush=True)
        
        self.listenerThread = threading.Thread(target=listener_loop, daemon=True)
        self.listenerThread.start()
    
    def stopListener(self) -> None:
        """Stop the listener thread"""
        self.listening = False
        if self.listenerThread is not None:
            self.listenerThread.join(timeout=1.0)
    
    def getAddress(self) -> str:
        return self.address
    
    def getPort(self) -> int:
        return self.port

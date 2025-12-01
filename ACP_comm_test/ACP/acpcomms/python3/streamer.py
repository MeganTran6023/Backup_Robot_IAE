"""
Streamer - UDP-based streaming implementation
Uses Python standard library (socket module)
"""
import socket
import threading
from typing import Dict, Any, Callable, Optional, Tuple
from .acp_comms import ACPComms


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
        
        Args:
            configuration: Dictionary containing:
                - host: Target host (default: "localhost")
                - port: Target port (default: 9999)
                - bufferSize: Receive buffer size (default: 8192)
                - localPort: Local port to bind to (optional)
                - timeout: Socket timeout in milliseconds (optional)
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
            # Convert milliseconds to seconds for Python socket
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
        """
        Send data via UDP
        
        Args:
            data: Bytes to send
        """
        if not self.connected:
            raise RuntimeError("Not connected")
        
        self.socket.sendto(data, (self.address, self.port))
    
    def sendDataString(self, data: str) -> None:
        """
        Send string data via UDP
        
        Args:
            data: String to send
        """
        self.sendData(data.encode())
    
    def receiveData(self) -> DatagramPacket:
        """
        Receive data via UDP
        
        Returns:
            DatagramPacket: Received packet with data and address
        """
        if not self.connected:
            raise RuntimeError("Not connected")
        
        data, addr = self.socket.recvfrom(self.bufferSize)
        return DatagramPacket(data, addr)
    
    def setPacketHandler(self, handler: Callable[[DatagramPacket], None]) -> None:
        """
        Set the packet handler callback
        
        Args:
            handler: Callable that accepts DatagramPacket
        """
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
                    # Normal timeout, continue listening
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
        """
        Get target address
        
        Returns:
            str: Target host address
        """
        return self.address  # Are these redundant?
    
    def getPort(self) -> int:
        """
        Get target port
        
        Returns:
            int: Target port number
        """
        return self.port
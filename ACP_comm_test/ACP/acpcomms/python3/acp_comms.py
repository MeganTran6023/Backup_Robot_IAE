"""
ACPComms - Abstract base class for communication protocols
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class ACPComms(ABC):
    """Abstract base class for ACP communications"""
    
    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.connected: bool = False
    
    @abstractmethod
    def configure(self, configuration: Dict[str, Any]) -> None:
        """
        Configure the communication instance
        
        Args:
            configuration: Dictionary of configuration parameters
        """
        pass
    
    @abstractmethod
    def connect(self) -> None:
        """Establish connection"""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close connection"""
        pass
    
    def isConnected(self) -> bool:
        """
        Check if currently connected
        
        Returns:
            bool: Connection status
        """
        return self.connected
    
    def getConfig(self) -> Dict[str, Any]:
        """
        Get a copy of the current configuration
        
        Returns:
            dict: Copy of configuration dictionary
        """
        return self.config.copy()
# acpcomms

## Overview

This directory is language specific communications libraries in support of the 
IAE Autonomy capability platform. Each folder contains the supported 
communications protocols in the folder's respective language.

## File Structure

* `acpcomms/java/*` - Java implementation files
* `acpcomms/python3/*` - Python implementation files

## Features and Purpose

- **Abstract base class** for protocol-agnostic communication
- **ZeroMQ messaging** support (PUB/SUB, REQ/REP, PUSH/PULL)
- **UDP streaming** with datagram packet handling
- **Asynchronous listeners** for background message/packet reception
- **Configurable** connection parameters
- **Thread-safe** implementations

## Installation

As the installation requirements vary from language to language, their specific 
information can be found in their relative directory. For information regarding 
installation requirements, refer to acpcomms/[language]/README.md

## Architecture

### Class Hierarchy

All language libraries within the acpcomms directory all should be designed as 
identical as possible using the following class structure:

```
ACPComms (Abstract Base Class)
├── Messenger (ZeroMQ implementation)
└── Streamer (UDP implementation)
```

### ACPComms (Base Class)

Abstract base class defining the common interface for all communication protocols.

**Methods:**
- `configure(configuration: Dict[str, Any])` - Configure the communication instance
- `connect()` - Establish connection
- `disconnect()` - Close connection
- `isConnected()` - Check connection status
- `getConfig()` - Get current configuration

### Messenger

ZeroMQ-based messaging implementation supporting multiple socket patterns.

**Configuration Options:**
- `endpoint` - ZMQ endpoint (default: "tcp://localhost:5555")
- `socketType` - Socket type: "PUB", "SUB", "REQ", "REP", "PUSH", "PULL" (default: "SUB")
- `bind` - Whether to bind or connect (default: False)
- `topic` - Subscription topic for SUB sockets (default: "")

**Additional Methods:**
- `sendMessage(message: bytes)` - Send binary message
- `sendMessageString(message: str)` - Send string message
- `receiveMessage()` - Receive binary message
- `receiveMessageString()` - Receive string message
- `setMessageHandler(handler)` - Set callback for async reception
- `startListener()` - Start background listener thread
- `stopListener()` - Stop listener thread

### Streamer

UDP-based streaming implementation for connectionless datagram communication.

**Configuration Options:**
- `host` - Target host (default: "localhost")
- `port` - Target port (default: 9999)
- `localPort` - Local port to bind to (optional)
- `bufferSize` - Receive buffer size in bytes (default: 8192)
- `timeout` - Socket timeout in milliseconds (optional)

**Additional Methods:**
- `sendData(data: bytes)` - Send binary data
- `sendDataString(data: str)` - Send string data
- `receiveData()` - Receive datagram packet
- `setPacketHandler(handler)` - Set callback for async reception
- `startListener()` - Start background listener thread
- `stopListener()` - Stop listener thread
- `getAddress()` - Get target address
- `getPort()` - Get target port


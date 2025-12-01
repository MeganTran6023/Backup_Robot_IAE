# ACP Communications Library

A Python communication library providing unified interfaces for different 
messaging and streaming protocols.

## Overview

The ACP Communications Library provides abstract base classes and concrete 
implementations for various communication protocols, making it easy to switch 
between different transport mechanisms while maintaining a consistent API.

## Installation

### Requirements

- Python 3.7+
- pyzmq (for Messenger class)

### Install Dependencies

```bash
pip install pyzmq
```

The `Streamer` class uses only Python standard library components and requires 
no additional dependencies.

## Thread Safety

Both `Messenger` and `Streamer` use background threads for asynchronous 
message/packet reception. Always call `stopListener()` before `disconnect()` to 
ensure proper cleanup.

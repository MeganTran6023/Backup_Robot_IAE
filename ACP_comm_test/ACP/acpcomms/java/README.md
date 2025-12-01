# ACP Communications Library (Java)

A Java communication library providing unified interfaces for different 
messaging and streaming protocols.

## Overview

The ACP Communications Library provides abstract base classes and concrete 
implementations for various communication protocols, making it easy to switch 
between different transport mechanisms while maintaining a consistent API.

**IMPORTANT INFO**
There is a known bug for importing classes described in `acpcomms/java/*` which 
requires users of the library to change the package declarations to build their 
code. We are working to define a fully independent and importable solution. 
For now, when importing this code in java applications, ensure you copy the 
code over and change the package declarations there. **DO NOT COMMIT CHANGES TO 
THE PACKAGE DECLARATIONS IN THE ACPCOMMS DIRECTORY**.

## Installation

### Requirements

- Java 21+
- JeroMQ (ZeroMQ for Java)

### Maven Dependency

```xml
<dependency>
    <groupId>org.zeromq</groupId>
    <artifactId>jeromq</artifactId>
    <version>0.5.3</version>
</dependency>
```

### Gradle Dependency

```gradle
implementation 'org.zeromq:jeromq:0.5.3'
```

The `Streamer` class uses only Java standard library components and requires no 
additional dependencies.

## Thread Safety

Both `Messenger` and `Streamer` use background threads for asynchronous 
message/packet reception. Always call `stopListener()` before `disconnect()` to 
ensure proper cleanup and avoid resource leaks.

The listener threads are designed to be interrupted gracefully during shutdown. 
A timeout of 1 second is used when joining threads to prevent indefinite 
blocking.

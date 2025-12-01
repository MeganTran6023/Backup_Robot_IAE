package com.usfiae.acp.commlib.acpcomms.java;

import java.net.*;
import java.util.Map;
import java.util.function.Consumer;


public class Streamer extends ACPComms {
    private DatagramSocket socket;
    private InetAddress address;
    private int port;
    private Thread listenerThread;
    private volatile boolean listening;
    private Consumer<DatagramPacket> packetHandler;
    private int bufferSize;

    public Streamer() {
        super();
    }

    @Override
    public void configure(Map<String, Object> configuration) throws Exception {
        this.config.putAll(configuration);

        String host = (String) config.getOrDefault("host", "localhost");
        this.port = (int) config.getOrDefault("port", 9999);
        this.address = InetAddress.getByName(host);
        this.bufferSize = (int) config.getOrDefault("bufferSize", 8192);

        Integer localPort = (Integer) config.get("localPort");
        if (localPort != null && socket == null) {
            socket = new DatagramSocket(localPort);
        }
    }


    @Override
    public void connect() throws Exception {
        if (connected) {
            throw new IllegalStateException("Already connected");
        }

        if (socket == null) {
            Integer localPort = (Integer) config.get("localPort");
            if (localPort != null) {
                socket = new DatagramSocket(localPort);
            } else {
                socket = new DatagramSocket();
            }
        }

        Integer timeout = (Integer) config.get("timeout");
        if (timeout != null) {
            socket.setSoTimeout(timeout);
        }

        connected = true;
    }


    @Override
    public void disconnect() throws Exception {
        if (!connected) {
            return;
        }

        stopListener();

        if (socket != null && !socket.isClosed()) {
            socket.close();
        }

        connected = false;
    }


    public void sendData(byte[] data) throws Exception {
        if (!connected) {
            throw new IllegalStateException("Not connected");
        }

        DatagramPacket packet = new DatagramPacket(data, data.length, address, port);
        socket.send(packet);
    }


    public void sendData(String data) throws Exception {
        sendData(data.getBytes());
    }


    public DatagramPacket receiveData() throws Exception {
        if (!connected) {
            throw new IllegalStateException("Not connected");
        }

        byte[] buffer = new byte[bufferSize];
        DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
        socket.receive(packet);
        return packet;
    }


    public void setPacketHandler(Consumer<DatagramPacket> handler) {
        this.packetHandler = handler;
    }


    public void startListener() throws Exception {
        if (!connected) {
            throw new IllegalStateException("Not connected");
        }
        if (listening) {
            throw new IllegalStateException("Listener already running");
        }

        listening = true;
        listenerThread = new Thread(() -> {
            while (listening && !Thread.currentThread().isInterrupted()) {
                try {
                    byte[] buffer = new byte[bufferSize];
                    DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
                    socket.receive(packet);

                    if (packetHandler != null) {
                        packetHandler.accept(packet);
                    }
                } catch (SocketTimeoutException e) {
                    // Normal timeout, continue listening
                } catch (Exception e) {
                    if (listening) {
                        System.err.println("Error receiving packet: " + e.getMessage());
                    }
                }
            }
        });
        listenerThread.start();
    }


    public void stopListener() {
        listening = false;
        if (listenerThread != null) {
            listenerThread.interrupt();
            try {
                listenerThread.join(1000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }


    public InetAddress getAddress() {
        return address;
    } // Are these redundent?


    public int getPort() {
        return port;
    }
}
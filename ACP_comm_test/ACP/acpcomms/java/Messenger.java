package ACP.acpcomms.java;

import org.zeromq.ZMQ;
import org.zeromq.ZContext;
import java.util.Map;
import java.util.HashMap;
import java.util.function.Consumer;

import com.fasterxml.jackson.databind.ObjectMapper;

public class Messenger extends ACPComms {
    private ZContext context;
    private ZMQ.Socket socket;
    private String endpoint;
    private int socketType;
    private Thread listenerThread;
    private volatile boolean listening;
    private Consumer<byte[]> messageHandler;

    // -----------------------------
    // JSON TEMPLATE SUPPORT (ADDED)
    // -----------------------------
    private Map<String, Object> messageTemplate;
    private final ObjectMapper jsonMapper = new ObjectMapper();


    public Messenger() {
        super();
    }

    @Override
    public void configure(Map<String, Object> configuration) throws Exception {
        this.config.putAll(configuration);

        // TODO: need to add configuration type for other protocols
        // this.protocol = (String) config.getOrDefault("protocol", "ZMQ");

        this.endpoint = (String) config.getOrDefault("endpoint", "tcp://localhost:5555");
        String type = (String) config.getOrDefault("socketType", "SUB"); // Only applies to MQ need to make submodules for supported protocols

        switch (type) {
            case "PUB" -> this.socketType = ZMQ.PUB;
            case "SUB" -> this.socketType = ZMQ.SUB;
            case "REQ" -> this.socketType = ZMQ.REQ;
            case "REP" -> this.socketType = ZMQ.REP;
            case "PUSH" -> this.socketType = ZMQ.PUSH;
            case "PULL" -> this.socketType = ZMQ.PULL;
            default -> throw new IllegalArgumentException("Invalid socket type: " + type);
        }
    }


    @Override
    public void connect() throws Exception {
        if (connected) {
            throw new IllegalStateException("Already connected");
        }

        context = new ZContext();
        socket = context.createSocket(socketType);

        boolean bind = (boolean) config.getOrDefault("bind", false);

        if (bind) {
            socket.bind(endpoint);
        } else {
            socket.connect(endpoint);
        }

        // For SUB sockets, subscribe to topics
        if (socketType == ZMQ.SUB) {
            String topic = (String) config.getOrDefault("topic", ""); // TODO: parameterize topics
            socket.subscribe(topic.getBytes());
        }

        connected = true;
    }


    @Override
    public void disconnect() throws Exception {
        if (!connected) {
            return;
        }

        stopListener();

        if (socket != null) {
            socket.close();
        }
        if (context != null) {
            context.close();
        }

        connected = false;
    }


    // -----------------------------
    // JSON TEMPLATE METHODS (ADDED)
    // -----------------------------

    /** Store a JSON message template. */
    public void setTemplate(Map<String, Object> template) {
        this.messageTemplate = new HashMap<>(template);
    }

    /** Return a copy of the stored template (to avoid mutation). */
    public Map<String, Object> getTemplate() {
        if (this.messageTemplate == null) {
            return null;
        }
        return new HashMap<>(this.messageTemplate);
    }

    /**
     * Populate the JSON template with caller-supplied overrides and send.
     * Equivalent to Python's sendMessageTemplate(temp=42, mode="run").
     */
    public void sendMessageTemplate(Map<String, Object> overrides) throws Exception {
        if (messageTemplate == null) {
            throw new IllegalStateException("Message template is not set");
        }

        // Copy template so we don’t mutate the original
        Map<String, Object> merged = new HashMap<>(messageTemplate);
        merged.putAll(overrides);

        String jsonString = jsonMapper.writeValueAsString(merged);
        sendMessage(jsonString);
    }

    // -----------------------------
    // ZMQ SEND / RECEIVE METHODS
    // -----------------------------

    public void sendMessage(byte[] message) throws Exception {
        if (!connected) {
            throw new IllegalStateException("Not connected");
        }
        socket.send(message, 0);
    }


    public void sendMessage(String message) throws Exception {
        sendMessage(message.getBytes());
    }


    public byte[] receiveMessage() throws Exception {
        if (!connected) {
            throw new IllegalStateException("Not connected");
        }
        return socket.recv(0);
    }


    public String receiveMessageString() throws Exception {
        return new String(receiveMessage());
    }


    public void setMessageHandler(Consumer<byte[]> handler) {
        this.messageHandler = handler;
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
                    byte[] message = socket.recv(0);
                    if (message != null && messageHandler != null) {
                        messageHandler.accept(message);
                    }
                } catch (Exception e) {
                    if (listening) {
                        System.err.println("Error receiving message: " + e.getMessage());
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
}

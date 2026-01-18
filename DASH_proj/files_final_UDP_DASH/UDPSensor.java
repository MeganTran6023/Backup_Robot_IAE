package com.usfiae.udpsensor;

import org.slf4j.LoggerFactory;

import com.usfiae.sensorapi.SensorTask;
import com.usfiae.sensorapi.Field;
import com.usfiae.sensorapi.DatabaseClient;

import java.net.*;
import java.io.IOException;
import java.util.Map;

// BSON imports (added)
import org.bson.BsonDocument;
import org.bson.RawBsonDocument;

public class UDPSensor extends SensorTask {

    // Max size heuristic for BSON metadata packets (added)
    private static final int BSON_MAX_SIZE = 2000;

    public UDPSensor(String id, Map<String, Object> config) {
        this.id = id;
        this.plugin = this.getClass().getName();  // Full class name
        this.log = LoggerFactory.getLogger(UDPSensor.class);

        // Initialize parent config field with default values (matching ZMQSensor structure)
        this.config = Map.ofEntries(
                Map.entry("name", new Field<String>("Name", "UDPSensor")),

                Map.entry("port", new Field<Integer>("Port", 9999)),
                Map.entry("url", new Field<String>("URL", "localhost")),
                Map.entry("pattern", new Field<String>("Pattern", "SUB")),
                // UDP-specific parameters for receive operations
                Map.entry("bufferSize", new Field<Integer>("Buffer Size", 8192)),
                Map.entry("socketTimeout", new Field<Integer>("Socket Timeout (ms)", 5000)),
                Map.entry("receiveBufferSize", new Field<Integer>("Receive Buffer Size (bytes)", 65536)),
                // Database configuration
                Map.entry("dbName", new Field<String>("Database Name", "dash")),
                Map.entry("dbUri", new Field<String>("Database URI", "mongodb://localhost:27017")),
                Map.entry("dbCollection", new Field<String>("Database Collection", "sensor_" + this.id))
        );

        // Update config with provided values
        if (config != null) {
            for (Map.Entry<String, Object> entry : config.entrySet()) {
                String key = entry.getKey();
                Map<String, Object> value = (Map<String, Object>) entry.getValue();
                this.config.get(key).setValue(value.get("value"));
            }
        }
    }

    /**
     * Attempt to parse a UDP packet payload as BSON.
     * Mirrors logic from standalone UDPReceiver example.
     */
    private BsonDocument tryParseBson(byte[] data, int length) {
        try {
            // BSON minimum size
            if (length < 5) {
                return null;
            }

            // BSON documents start with int32 length (little-endian)
            int declaredLength =
                    (data[0] & 0xFF) |
                            ((data[1] & 0xFF) << 8) |
                            ((data[2] & 0xFF) << 16) |
                            ((data[3] & 0xFF) << 24);

            // Length mismatch → not BSON
            if (declaredLength != length) {
                return null;
            }

            byte[] bsonBytes = new byte[length];
            System.arraycopy(data, 0, bsonBytes, 0, length);

            RawBsonDocument raw = new RawBsonDocument(bsonBytes);
            return raw.toBsonDocument();

        } catch (Exception e) {
            return null;
        }
    }


    @Override
    public void run() {
        this.running = true;
        log.info(this.config.get("name").getValue() + " is running...");

        DatagramSocket socket = null;

        try {
            int port = (int) this.config.get("port").getValue();
            int bufferSize = (int) this.config.get("bufferSize").getValue();
            int socketTimeout = (int) this.config.get("socketTimeout").getValue();
            int receiveBufferSize = (int) this.config.get("receiveBufferSize").getValue();

            socket = new DatagramSocket(port);
            socket.setSoTimeout(socketTimeout);
            socket.setReceiveBufferSize(receiveBufferSize);

            log.info("Connected to udp://localhost:" + port);

            DatabaseClient db = new DatabaseClient(
                    (String) this.config.get("dbUri").getValue(),
                    (String) this.config.get("dbName").getValue(),
                    (String) this.config.get("dbCollection").getValue()
            );

            byte[] buffer = new byte[bufferSize];

            while (running) {
                try {
                    DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
                    socket.receive(packet);

                    int packetSize = packet.getLength();
                    String sourceAddress = packet.getAddress().getHostAddress();
                    int sourcePort = packet.getPort();

                    // --- Safe BSON check ---
                    BsonDocument bson = parseBsonIfValid(packet.getData(), packetSize);

                    if (bson != null) {
                        log.info("Received BSON metadata: " + bson.toJson());

                        db.insertSensorData(
                                "UDPSensor",
                                this.id,
                                Map.of(
                                        "source", "UDP",
                                        "remoteHost", sourceAddress,
                                        "remotePort", sourcePort,
                                        "packetSize", packetSize
                                ),
                                Map.of("metadata", bson)
                        );

                    } else {
                        // Non-BSON packet (likely frame chunk) → ignore
                        log.debug("Non-BSON packet ignored ({} bytes)", packetSize);
                    }

                } catch (SocketTimeoutException e) {
                    // loop heartbeat
                } catch (IOException e) {
                    if (running) {
                        log.error("Error receiving message: " + e.getMessage());
                    }
                }
            }

        } catch (Exception e) {
            log.warn(this.config.get("name").getValue() + " has been stopped: " + e);
            running = false;
        } finally {
            if (socket != null && !socket.isClosed()) socket.close();
        }
    }

    /**
     * Only parse valid BSON packets.
     * Returns null if packet is not valid BSON metadata.
     */
    private BsonDocument parseBsonIfValid(byte[] data, int length) {
        try {
            // BSON minimum size
            if (length < 5) return null;

            // First 4 bytes = BSON length (little-endian)
            int declaredLength =
                    (data[0] & 0xFF) |
                            ((data[1] & 0xFF) << 8) |
                            ((data[2] & 0xFF) << 16) |
                            ((data[3] & 0xFF) << 24);

            // Length mismatch → not valid BSON
            if (declaredLength != length) return null;

            byte[] bsonBytes = new byte[length];
            System.arraycopy(data, 0, bsonBytes, 0, length);

            RawBsonDocument raw = new RawBsonDocument(bsonBytes);
            return raw.toBsonDocument();

        } catch (Exception e) {
            return null;
        }

    }
}

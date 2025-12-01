/** 
 * ACPSubscriber.java
 * 
 * This file is an example of the acpcomms python Messenger class showcasing 
 * ZMQ messaging
 * 
 * This is meant to be used with ACPPublisher.java
 */

import ACP.acpcomms.java.Messenger;

import java.util.HashMap;
import java.util.Map;
import com.fasterxml.jackson.databind.ObjectMapper;

public class ACPSubscriber {
    public static void main(String[] args) throws Exception {

        Messenger subscriber = new Messenger();

        Map<String, Object> config = new HashMap<>();
        config.put("endpoint", "tcp://localhost:6000");
        config.put("socketType", "SUB");
        config.put("topic", "");   // Subscribe to all messages

        subscriber.configure(config);
        subscriber.connect();

        ObjectMapper mapper = new ObjectMapper();

        subscriber.setMessageHandler(message -> {
            try {
                String decoded = new String(message);
                Map<String, Object> data = mapper.readValue(decoded, Map.class);

                String sensorId = (String) data.getOrDefault("sensor_id", "N/A");
                String sensorType = (String) data.getOrDefault("sensor_type", "N/A");
                String timestamp = (String) data.getOrDefault("timestamp", "N/A");

                Map<String, Object> dataField =
                    (Map<String, Object>) data.getOrDefault("data", new HashMap<>());

                Object reading = dataField.getOrDefault("value", "N/A");

                Map<String, Object> meta =
                    (Map<String, Object>) data.getOrDefault("metadata", new HashMap<>());

                String units = (String) meta.getOrDefault("units", "N/A");

                System.out.println("--- Sensor Reading ---");
                System.out.println("ID/Type: " + sensorId + " / " + sensorType);
                System.out.println("Timestamp: " + timestamp);
                System.out.println("Reading: " + reading + " " + units);

            } catch (Exception e) {
                System.out.println("Error decoding or processing message: " + e);
            }
        });

        subscriber.startListener();

        // Keep running 20 seconds like Python version
        Thread.sleep(20000);

        subscriber.stopListener();
        subscriber.disconnect();
    }
}

/**
 * ACPPublisher.java
 * 
 * This file is an example of the acpcomms python Messenger class showcasing 
 * ZMQ messaging
 * 
 * This is meant to be used with ACPSubscriber.java
 */

import ACP.acpcomms.java.Messenger;

import java.util.HashMap;
import java.util.Map;
import java.time.Instant;
import java.util.Random;

public class ACPPublisher {
    public static void main(String[] args) throws Exception {

        Messenger publisher = new Messenger();

        Map<String, Object> config = new HashMap<>();
        config.put("endpoint", "tcp://127.0.0.1:6000");
        config.put("socketType", "PUB");
        config.put("bind", true);   // Publisher binds

        publisher.configure(config);

        // -----------------------------
        // Define JSON template (same as Python)
        // -----------------------------
        Map<String, Object> template = new HashMap<>();
        template.put("sensor_id", "TEMP_001");
        template.put("sensor_type", "temperature");
        template.put("data_type", "float");
        template.put("timestamp", null);

        Map<String, Object> location = new HashMap<>();
        location.put("lat", 27.9944);
        location.put("lon", -82.6367);
        template.put("location", location);

        Map<String, Object> metadata = new HashMap<>();
        metadata.put("units", "Celsius");
        metadata.put("schema_version", "1.0");
        metadata.put("tags", new String[]{"ambient", "test"});
        template.put("metadata", metadata);

        template.put("data", new HashMap<String, Object>());

        publisher.setTemplate(template);

        publisher.connect();
        System.out.println("Publisher started...");

        Random rng = new Random();

        // -----------------------------
        // Publish 10 temperature readings
        // -----------------------------
        for (int i = 0; i < 10; i++) {

            String timestamp = Instant.now().toString();

            double tempReading = 20.0 + (rng.nextDouble() * 10.0);

            Map<String, Object> overrides = new HashMap<>();
            overrides.put("sensor_id", "TEMP_001");
            overrides.put("timestamp", timestamp);

            Map<String, Object> dataField = new HashMap<>();
            dataField.put("value", tempReading);
            overrides.put("data", dataField);

            overrides.put("count", i);  // Tracking

            publisher.sendMessageTemplate(overrides);

            System.out.printf(
                "Sent message index %d with temp: %.2f C%n", 
                i, tempReading
            );

            Thread.sleep(1000);
        }

        publisher.disconnect();
    }
}

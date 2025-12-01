/**
 * DASHPublisher.java
 * 
 * This class is used as a testing script specifically to emulate a sensor that 
 * can send data to the DASH ACP plugin. This uses the `acpcomms/java/Messenger.java` class
 */

import ACP.acpcomms.java.Messenger;

import java.util.Map;

public class DASHPublisher {
    public static void main(String[] args) throws Exception {
        Messenger publisher = new Messenger();

        Map<String, Object> config = Map.ofEntries(
                Map.entry("endpoint", "tcp://*:5555"),
                Map.entry("socketType", "PUB"),
                Map.entry("bind", true)
        );

        publisher.configure(config);
        publisher.connect();

        System.out.println("Publisher started on port 5555");


        // Publish messages
        for (int i = 0; i < 100; i++) {
            Thread.sleep(2000); // Set a delay between messages
            String message = "status:Message No. " + i;
            publisher.sendMessage(message);
            System.out.println("Published: " + message);
            Thread.sleep(100);
        }

        publisher.disconnect();
    }
}

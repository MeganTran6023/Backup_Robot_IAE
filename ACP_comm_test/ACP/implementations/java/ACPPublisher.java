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

public class ACPPublisher {
    public static void main(String[] args) throws Exception {
        Messenger publisher = new Messenger();
        
        Map<String, Object> config = new HashMap<>();
        config.put("endpoint", "tcp://*:5555");
        config.put("socketType", "PUB");
        config.put("bind", true);
        
        publisher.configure(config);
        publisher.connect();
        
        // Send messages
        for (int i = 0; i < 10; i++) {
            publisher.sendMessage("status:Hello, World!");
            Thread.sleep(2000); // Give time for message delivery
        }

        publisher.disconnect();
    }
}
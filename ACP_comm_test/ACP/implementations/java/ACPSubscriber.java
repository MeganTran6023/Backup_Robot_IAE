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

public class ACPSubscriber {
    public static void main(String[] args) throws Exception {
        Messenger subscriber = new Messenger();
        
        Map<String, Object> config = new HashMap<>();
        config.put("endpoint", "tcp://localhost:5555");
        config.put("socketType", "SUB");
        config.put("topic", "status");
        
        subscriber.configure(config);
        subscriber.connect();
        
        subscriber.setMessageHandler(message -> {
            System.out.println("Received: " + new String(message));
        });
        
        subscriber.startListener();
        
        // Keep running
        Thread.sleep(10000);
        
        subscriber.stopListener();
        subscriber.disconnect();
    }
}
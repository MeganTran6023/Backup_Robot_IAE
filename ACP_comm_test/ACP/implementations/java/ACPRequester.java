/**
 * ACPRequester.java
 * 
 * This file is an example of the acpcomms python Messenger class showcasing 
 * ZMQ messaging
 * 
 * This is meant to be used with ACPReplier.java
 */

import ACP.acpcomms.java.Messenger;

import java.util.HashMap;
import java.util.Map;

public class ACPRequester {
    public static void main(String[] args) throws Exception {
        Messenger client = new Messenger();
        
        Map<String, Object> config = new HashMap<>();
        config.put("endpoint", "tcp://localhost:5556");
        config.put("socketType", "REQ");
        
        client.configure(config);
        client.connect();
        
        // Send request
        client.sendMessage("Hello Server");
        
        // Receive reply
        String reply = client.receiveMessageString();
        System.out.println("Received reply: " + reply);
        
        client.disconnect();
    }
}

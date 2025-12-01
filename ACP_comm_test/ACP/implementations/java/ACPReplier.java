/**
 * ACPReplier.java
 * 
 * This file is an example of the acpcomms python Messenger class showcasing 
 * ZMQ messaging
 * 
 * This is meant to be used with ACPRequester.java
 */

import ACP.acpcomms.java.Messenger;

import java.util.HashMap;
import java.util.Map;

public class ACPReplier {
    public static void main(String[] args) throws Exception {
        Messenger server = new Messenger();
        
        Map<String, Object> config = new HashMap<>();
        config.put("endpoint", "tcp://*:5556");
        config.put("socketType", "REP");
        config.put("bind", true);
        
        server.configure(config);
        server.connect();
        
        while (true) {
            String request = server.receiveMessageString();
            System.out.println("Received request: " + request);
            
            // Send reply
            server.sendMessage("Response to: " + request);
        }
    }
}
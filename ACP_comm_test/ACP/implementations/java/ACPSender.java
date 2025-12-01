/**
 * ACPSender.java
 * 
 * This file is an example of the acpcomms python Messenger class showcasing 
 * UDP streaming
 * 
 * This is meant to be used with ACPReceiver.java
 */

import ACP.acpcomms.java.Streamer;

import java.util.HashMap;
import java.util.Map;

public class ACPSender {
    public static void main(String[] args) throws Exception {
        Streamer sender = new Streamer();
        
        Map<String, Object> config = new HashMap<>();
        config.put("host", "localhost");
        config.put("port", 9999);
        
        sender.configure(config);
        sender.connect();
        
        // Send data
        for (int i = 0; i < 10; i++) {
            sender.sendData("UDP message");
            Thread.sleep(2000);
        }
        
        sender.disconnect();
    }
}

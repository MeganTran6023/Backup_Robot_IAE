/**
 * ACPReceiver.java
 * 
 * This file is an example of the acpcomms python Messenger class showcasing 
 * UDP streaming
 * 
 * This is meant to be used with ACPSender.java
 */

import ACP.acpcomms.java.Streamer;

import java.util.HashMap;
import java.util.Map;

public class ACPReceiver {
    public static void main(String[] args) throws Exception {
        Streamer receiver = new Streamer();
        
        Map<String, Object> config = new HashMap<>();
        config.put("localPort", 9999);
        config.put("bufferSize", 8192);
        
        receiver.configure(config);
        receiver.connect();
        
        receiver.setPacketHandler(packet -> {
            byte[] data = packet.getData();
            int length = packet.getLength();
            String message = new String(data, 0, length);
            System.out.println("Received: " + message);
        });
        
        receiver.startListener();
        
        // Keep running
        Thread.sleep(10000);
        
        receiver.stopListener();
        receiver.disconnect();
    }
}

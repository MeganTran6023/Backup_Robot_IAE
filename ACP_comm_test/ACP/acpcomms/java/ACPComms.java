package ACP.acpcomms.java;

import java.util.Map;
import java.util.HashMap;


// Abstract base class
public abstract class ACPComms {
    protected Map<String, Object> config;
    protected boolean connected;

    public ACPComms() {
        this.config = new HashMap<>();
        this.connected = false;
    }


    public abstract void configure(Map<String, Object> configuration) throws Exception;


    public abstract void connect() throws Exception;


    public abstract void disconnect() throws Exception;


    public boolean isConnected() {
        return connected;
    }


    public Map<String, Object> getConfig() {
        return new HashMap<>(config);
    }
}

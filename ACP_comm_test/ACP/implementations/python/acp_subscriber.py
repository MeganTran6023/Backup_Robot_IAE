# acp_subscriber.py
# 
# This file is an example of the acpcomms python Messenger class showcasing ZMQ 
# messaging
# 
# This is meant to be used with acp_publisher.py

from ACP.acpcomms.python3.messenger import Messenger
import time
import json

subscriber = Messenger()
subscriber.configure({
    "endpoint": "tcp://localhost:6000",
    "socketType": "SUB",
    "topic": ""
})
subscriber.connect()

def on_message(msg: bytes):
    try:
        decoded = msg.decode()
        data = json.loads(decoded)
        
        # Extract and print key information from the new template structure
        sensor_id = data.get("sensor_id", "N/A")
        sensor_type = data.get("sensor_type", "N/A")
        timestamp = data.get("timestamp", "N/A")
        
        # Assuming sensor data is stored as {"value": ...} in the "data" field
        reading = data.get("data", {}).get("value", "N/A")
        units = data.get("metadata", {}).get("units", "N/A")

        print(f"--- Sensor Reading ---")
        print(f"ID/Type: {sensor_id} / {sensor_type}")
        print(f"Timestamp: {timestamp}")
        print(f"Reading: **{reading} {units}**")
        
    except Exception as e:
        print("Error decoding or processing message:", e)


subscriber.setMessageHandler(on_message)
subscriber.startListener()

# Keep running
time.sleep(20)

subscriber.stopListener()
subscriber.disconnect()
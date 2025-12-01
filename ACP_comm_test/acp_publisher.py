# acp_publisher.py
# 
# This file is an example of the acpcomms python Messenger class showcasing ZMQ 
# messaging
# 
# This is meant to be used with acp_subscriber.py

from ACP.acpcomms.python3.messenger import Messenger
import time
# Use a standard library for ISO8601 timestamps
from datetime import datetime, timezone
import random 

# -----------------------------
# Configure Publisher (PUB)
# -----------------------------
pub = Messenger()
pub.configure({
    "endpoint": "tcp://127.0.0.1:6000",
    "socketType": "PUB",
    "bind": True     # Publisher binds
})

# Define the new, full JSON template
# Use None/default values where strings were used as placeholders
pub.setTemplate({
    "sensor_id": "TEMP_001", 
    "sensor_type": "temperature", 
    "data_type": "float", 
    "timestamp": None, 
    "location": { 
        "lat": 27.9944, 
        "lon": -82.6367
    },
    "metadata": { 
        "units": "Celsius", 
        "schema_version": "1.0", 
        "tags": ["ambient", "test"]
    },
    "data": {} 
})

pub.connect()
print("Publisher started...")

# -----------------------------
# test connection for 10 iterations
# -----------------------------
i = 0
while i < 10:
    # 1. Generate an ISO8601 timestamp
    current_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    # 2. Generate some random data
    temp_reading = 20.0 + (random.random() * 10) # 20.0 to 30.0

    # Populate the template with key/value overrides for the changing data
    pub.sendMessageTemplate(
        sensor_id="TEMP_001", 
        timestamp=current_time, 
        data={"value": temp_reading}, # Set the raw sensor data
        count=i # Add 'count' back for tracking, even though it's not in the template
    )
    
    print(f"Sent message index {i} with temp: {temp_reading:.2f} C")
    i += 1
    time.sleep(1)
pub.disconnect()
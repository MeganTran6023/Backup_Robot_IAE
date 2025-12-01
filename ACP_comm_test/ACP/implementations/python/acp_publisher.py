# acp_publisher.py
#
# This file is an example of the acpcomms python Messenger class showcasing ZMQ 
# messaging
#
# This is meant to be used with acp_subscriber.py

from ACP.acpcomms.python3.messenger import Messenger
import time
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

# ------------------------------------------------------------
# TEMPLATE HANDLING (Updated per request)
# ------------------------------------------------------------
# We no longer define a static template here.
# Instead, we *request the default template* from Messenger.
# Industry-standard practice: centralize template definitions to 
# ensure a single source of truth and avoid duplication.
# ------------------------------------------------------------
template = pub.getTemplate()

# ------------------------------------------------------------
# Populate ONLY the fields that are static for this publisher.
# Dynamic fields (timestamp, data, count, etc.) will be filled
# inside sendMessageTemplate() as overrides.
# ------------------------------------------------------------
template["sensor_id"] = "TEMP_001"
template["sensor_type"] = "temperature"
template["data_type"] = "float"

template["location"]["lat"] = 27.9944
template["location"]["lon"] = -82.6367

template["metadata"]["units"] = "Celsius"
template["metadata"]["schema_version"] = "1.0"
template["metadata"]["tags"] = ["ambient", "test"]

# Load the updated template back into Messenger
pub.setTemplate(template)

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

    # ------------------------------------------------------------
    # Use template + runtime overrides.
    # Industry-standard: Provide only the fields that change.
    # Template supplies all default/static fields automatically.
    # ------------------------------------------------------------
    pub.sendMessageTemplate(
        timestamp=current_time,
        data={"value": temp_reading},
        count=i     # Kept for backwards compatibility (not in template)
    )
    
    print(f"Sent message index {i} with temp: {temp_reading:.2f} C")
    i += 1
    time.sleep(1)

pub.disconnect()

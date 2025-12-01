# acp_sender.py
# 
# This file is an example of the acpcomms python Streamer class showcasing UDP 
# streaming
# 
# This is meant to be used with acp_receiver.py

from ACP.acpcomms.python3.streamer import Streamer
import time

sender = Streamer()
sender.configure({
    "host": "localhost",
    "port": 9999
})
sender.connect()

# Send data
for i in range(10):
    sender.sendDataString("UDP message")
    time.sleep(2)
sender.disconnect()
# acp_receiver.py
# 
# This file is an example of the acpcomms python Streamer class showcasing UDP 
# streaming
# 
# This is meant to be used with acp_sender.py

from ACP.acpcomms.python3.streamer import Streamer
import time

receiver = Streamer()
receiver.configure({
    "localPort": 9999,
    "bufferSize": 8192
})
receiver.connect()

def on_packet(packet):
    print(f"From {packet.getAddress()}: {packet.getData().decode()}")

receiver.setPacketHandler(on_packet)
receiver.startListener()

# Keep running
time.sleep(10)

receiver.stopListener()
receiver.disconnect()
"""
acp_subscriber.py
Subscriber receives JSON text (Messenger handles BSON → JSON).
"""

from ACP.acpcomms.python3.messenger import Messenger
import time

# ---------------------------------
# Configure Subscriber
# ---------------------------------
sub = Messenger()
sub.configure({
    "endpoint": "tcp://127.0.0.1:6000",
    "socketType": "SUB",
    "topic": ""
})

sub.connect()

# ---------------------------------
# Handler receives JSON STRING
# ---------------------------------
def on_message(json_string: str):
    print("---- JSON Message Received ----")
    print(json_string)
    print()

sub.setMessageHandler(on_message)
sub.startListener()

time.sleep(20)

sub.stopListener()
sub.disconnect()
print("Subscriber finished.")

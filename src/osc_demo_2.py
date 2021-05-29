# Simple OSC demo
import random
import time

import numpy as np
from pythonosc import udp_client

from genetic import init_chromosome

# TODO: default ip and port. argparse possible
IP = "127.0.0.1"
PORT = 57120


def chromosome_to_osc(c: np.ndarray):
    return c.tolist()


print(f"Sending OSC messages to {IP}, port {PORT}")

client = udp_client.SimpleUDPClient(IP, PORT)
while True:
    time.sleep(5)
    c = init_chromosome()
    args = chromosome_to_osc(c)
    print(f"Sending args: {args}")
    client.send_message("/playInstrument", args)

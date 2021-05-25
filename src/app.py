# Flask server
import random

from flask import Flask, request
from pythonosc import udp_client

app = Flask(__name__)

# For osc client
IP = "127.0.0.1"
PORT = 57120

client = udp_client.SimpleUDPClient(IP, PORT)


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/setActive", methods=["POST"])
def setActive():
    # TODO communicate with ChucK via OSC
    client.send_message("/setFreq", random.random() * 400)
    return "OK"

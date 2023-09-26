

import sys
import time
import threading
from scapy.all import *

# Access point object
class AP:
    def __init__(self, bssid):
        self.bssid = bssid
        self.ssid = []
        self.power_db = []
        self.channel = []
        self.enc = []
        self.frames = 1

# Client/station object
class Client:
    def __init__(self, mac):
        self.mac = mac
        self.bssid = []
        self.ssid = []
        self.power_db = []
        self.frames = 1
        


# Scapy sniffing function
def sniffer():
    pass


def listener():
    pass







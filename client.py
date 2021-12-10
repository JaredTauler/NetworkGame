# Jared Tauler 12/6/2021
import socket
import json
from _thread import *
from typing import Tuple, Union
import subprocess
import re

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.response = []
        self.waiting = False

    # Doesnt work lol
    def scan(self, port):
        str = subprocess.check_output(['arp', '-a'])
        # Search pattern
        p = re.compile(
            "(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
        )
        for i in re.findall(p, str.decode()):
            try:
                self.client.connect((i, port))
            except:
                pass


    def connect(self, addr: Tuple[str, int]):
        try:
            self.client.connect(addr)
            start_new_thread(self.listener, ())  # Start listener when connection is made
            return True
        except Exception as e:
            print(e)
            return False

    def listener(self):
        # print("Listening to " + str(addr))
        print("listening")
        while True:
            try:
                data = json.loads(
                    self.client.recv(4096).decode()
                )
                # print(data)
                self.response.append(data) # add response to the list of responses that need to be processed.
            except Exception as e:
                print("Exception: ", e)
                break

    def send(self, data: dict):
        self.client.send(str.encode(json.dumps(data)))


# net = Network()
# # print(net.search(5058))
# net.connect((socket.gethostname(), 5058))

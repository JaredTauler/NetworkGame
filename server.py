# Jared Tauler 12/6/2021
import socket
import json
import time
from _thread import *

class Server():
    def __init__(self):
        server = socket.gethostname()
        port = 5059
        self.client_id = 21


        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.bind((server, port))
        except socket.error as e:
            str(e)

        self.client.listen(2)

        print("Waiting for a connection, Server Started")

        self.listeners = []
        self.response = {}
        self.clients = {}

        start_new_thread(self.listen_new_connection, ())
        start_new_thread(self.sender, ())

    def sender(self):
        while True:
            time.sleep(.3)
            for id in self.clients:
                pass
                # print(self.clients)
                print("BRUH", self.clients[id])
                # client = self.clients[id]
                # print(client.response)

    def listen_new_connection(self):
        # Listen for new connections.
        while True:
            conn, addr = self.client.accept() # Accept

            id = self.client_id # Get new ID
            self.client_id += 1

            print("Connected to:", addr)
            print(id)
            self.clients[id] = start_new_thread(self.classclient, (conn, id)) # Client's listener
            print(self.clients)


    class classclient():
        def __init__(self, conn, id):
            self.response = []
            conn.send(str.encode(json.dumps({"id": id})))  # Give joined player their ID
            start_new_thread(self.listener, (conn, id))

        def listener(self, conn, id):
            while True:
                # Receive data from client
                res = conn.recv(4096).decode()
                print("SERVER RECEIVED:", res, id)
                # data = json.loads(res.decode())
                self.response.append(res)

            print("Lost connection")
            conn.close()


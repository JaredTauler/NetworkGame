# Jared Tauler 12/6/2021
import socket
import json
import time
from _thread import *

class Server():
    def __init__(self):
        server = socket.gethostname()
        port = 5059
        self.client_id = 21 # 0 is the server's ID


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
            time.sleep(.01) # Tickrate
            data = {}
            # Get data. Need to get data from every client and then clear their list.
            for id in self.clients:
                # Restrict data sent to 5 ticks. Normal circumstances will be 1-2.
                data[id] = self.clients[id].response[0:4]
                for i in range(0,4):
                    if self.clients[id].response == []:
                        break
                    self.clients[id].response.pop(0)

            for id in self.clients:
                c = self.clients[id]
                # Return everything except own client's stuff
                notmydata = lambda data, id: [{i: data[i]} for i in data if i != id]
                # Send data
                c.conn.send(
                    str.encode(
                        json.dumps(
                            notmydata(data, id)
                        )
                    )
                )
                c.response = [] # Clear list

    def listen_new_connection(self):
        # Listen for new connections.
        while True:
            conn, addr = self.client.accept() # Accept

            id = self.client_id # Get new ID
            self.client_id += 1

            print("Connected to:", addr)
            self.clients[id] = self.classclient(conn, id) # Client's listener


    class classclient():
        def __init__(self, conn, id):
            self.response = []
            self.conn = conn
            conn.send(str.encode(json.dumps([{0: [{"id": id}]}])))  # Give joined player their ID
            start_new_thread(self.listener, (conn, id))

        def listener(self, conn, id):
            while True:
                # Receive data from client
                res = conn.recv(4096).decode()
                # print("SERVER RECEIVED:", res, id)
                self.response.append(res) # ID and bytes
            print("Lost connection")
            conn.close()


# Jared Tauler 12/6/2021
import socket
import json
from _thread import *

class Server():
    def __init__(self):
        server = socket.gethostname()
        port = 5058
        self.client_id = 21


        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.bind((server, port))
        except socket.error as e:
            str(e)

        self.client.listen(2)

        print("Waiting for a connection, Server Started")

        connected = set()
        self.listeners = []
        self.response = {}

        start_new_thread(self.listen_new_connection, ())

    def listen_new_connection(self):
        # Listen for new connections.
        while True:
            conn, addr = self.client.accept() # Accept

            id = self.client_id # Get new ID
            self.client_id += 1

            conn.send(str.encode(json.dumps({"id": id}))) # Give joined player their ID

            print("Connected to:", addr)
            start_new_thread(self.listener, (conn, id))

    def listener(self,conn, id):
        self.response[id] = {}
        while True:
            # try:
                # Receive data from client
                data = json.loads(
                    conn.recv(4096).decode()
                )
                # Add newfound data to everybodies reponse list, except for mine.
                for i in self.response:
                    if i == id: continue
                    else:
                        # If a tick list for me doesnt exist in set client, create it
                        if not self.response[i].get(id):
                            self.response[i][id] = []
                        # append tick to ticklist
                        self.response[i][id].append(data)

                # Now to send my response dict to my client,
                res = self.response[id]
                self.response[id] = {} # Clear my doct.

                conn.send(str.encode(json.dumps(res)))
            # except Exception as e:
            #     print("Exception:", e)
            #     break
        print("Lost connection")
        conn.close()


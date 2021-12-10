# Jared Tauler 12/6/2021
import socket
import json
from _thread import *

class Server():
    def __init__(self):
        server = socket.gethostname()
        port = 5058


        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            self.s.bind((server, port))
        except socket.error as e:
            str(e)

        self.s.listen(2)

        print("Waiting for a connection, Server Started")

        connected = set()
        self.client = {}

        start_new_thread(self.listen_new_connection, ())

    def listen_new_connection(self):
        # Listen for new connections.
        while True:
            conn, addr = self.s.accept()
            print("Connected to:", addr)

            p = addr
            gameId = 0
            self.client[start_new_thread(self.listener, (conn, p, gameId))] = 0


    def listener(self,conn, p, gameId):
        reply = ""
        while True:
            try:
                data = conn.recv(4096).decode()
                # conn.send(str.encode(data))

            except Exception as e:
                print("Exception:", e)
                break
        print("Lost connection")
        try:
            del self.client[gameId]
            print("Disconnected", gameId)
        except:
            pass
        conn.close()


# Jared Tauler 12/6/2021
import socket
import json
from _thread import *

server = socket.gethostname()
port = 5058


s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)

print("Waiting for a connection, Server Started")

connected = set()
client = []


def listener(conn, p, gameId):
    # global idCount
    # conn.send(str.encode(str(p)))

    reply = ""
    while True:
        try:
            data = conn.recv(4096).decode()
            print(json.loads(data))

            # if gameId in client:
            #     game = client[gameId]
            #
            #     if not data:
            #         break
            #     else:
            #         # if data == "reset":
            #         #     game.resetWent()
            #         # elif data != "get":
            #         #     game.play(p, data)
            conn.send(str.encode(data))

            # else:
            #     break
        except Exception as e:
            print(e)
            break
    print("Lost connection")
    try:
        del client[gameId]
        print("Disconnected", gameId)
    except:
        pass
    # idCount -= 1
    conn.close()


# Listen for new connections.
while True:
    conn, addr = s.accept()
    print("Connected to:", addr)
    #
    # idCount += 1
    # p = 0
    # gameId = (idCount - 1)//2
    # if idCount % 2 == 1:
    #     client[gameId] = Game(gameId)
    #     print("Creating a new game...")
    # else:
    #     client[gameId].ready = True
    #     p = 1

    p = addr
    gameId = 0
    client.append(
        start_new_thread(listener, (conn, p, gameId))
    )

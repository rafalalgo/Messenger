import socket
from threading import Thread, Lock

global host, port, clientList, buforSize, user, tab

host = 'localhost'
port = 44000
buforSize = 2048
clientList = []
user = "ALL#"
tab = []


class Client(object):
    def __init__(self, conn, name):
        self.conn = conn
        self.name = name

    def send(self, message):
        self.conn.send(bytearray(message, 'utf-8'))

    def recv(self):
        return self.conn.recv(buforSize)

    def close(self):
        self.conn.close()


def get_client(name):
    for client in clientList:
        if client.name == name:
            return client
    return None


def send_to_one(data, name, lock):
    lock.acquire()
    print(name)
    get_client(name).send(data)
    lock.release()


def send_to_all(data, lock):
    lock.acquire()
    for cl in clientList:
        cl.send(data)
    lock.release()


def handle_client(client, lock):
    while True:
        data = client.recv()
        if not data:
            break
        print(data)
        if data == "LOGOUT":
            response = ""
            global user, tab
            lock.acquire()
            tab = user.split('#')
            tab.remove(client.name)
            for item in tab:
                response += item
                response += "#"
            user = response
            response = "LIST_USER#" + response
            lock.release()
            send_to_all(data=response, lock=lock)
            break
        elif data[0:3] == "ALL":
            response = "MSG#" + client.name + "#" + data
            send_to_all(data=response, lock=lock)
        else:
            response = "MSG#" + client.name + "#" + data
            pos = 0
            while data[pos] != "#":
                pos += 1
            send_to_one(data=response, name=data[0:pos], lock=lock)
    lock.acquire()
    clientList.remove(client)
    client.close()
    lock.release()


def handle_server(server_socket, lock):
    while True:
        conn, addr = server_socket.accept()
        name = conn.recv(buforSize)
        client = get_client(name)
        if client:
            conn.send(b'0')
            conn.close()
        else:
            conn.send(b'1')
            client = Client(conn, name)
            clientList.append(client)
            global user
            lock.acquire()
            user = user + name + "#"
            response = "LIST_USER#" + user
            lock.release()
            send_to_all(response, lock)
            Thread(target=handle_client, args=(client, lock)).start()


def start_server():
    global host, port
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    while True:
        try:
            server_socket.bind((host, port))
        except socket.error:
            port += 1
        else:
            break

    server_socket.listen(10)
    print("*****************************************")
    print("TCP/IP chat server listening on port " + str(port))
    print("*****************************************")
    lock = Lock()
    handle_server(server_socket, lock)


start_server()

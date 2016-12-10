import socket
from threading import Thread, Lock

buforSize = 2048


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


class Server(object):
    def __init__(self):
        self.host = 'localhost'
        self.port = 44000
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.lock = Lock()

        while True:
            try:
                self.server_socket.bind((self.host, self.port))
            except socket.error:
                self.port += 1
            else:
                break

        self.server_socket.listen(10)
        self.userList = []
        print("Server is run on port " + str(self.port))

    def get_client(self, name):
        for client in self.userList:
            if client.name == name:
                return client
        return None

    def send_to_one(self, data, name, lock):
        lock.acquire()
        self.get_client(name).send(data)
        lock.release()

    def send_to_all(self, data, lock):
        lock.acquire()
        for cl in self.userList:
            cl.send(data)
        lock.release()

    def handle_client(self, client, lock):
        while True:
            data = client.recv()
            if not data:
                self.userList.remove(client)
                break
            if data == "LOGOUT":
                print("LOGOUT: " + client.name)
                self.userList.remove(client)
                response = "LIST_USER#ALL#"
                for item in self.userList:
                    response += item.name + "#"
                self.send_to_all(data=response, lock=lock)
                break
            elif data[0:3] == "ALL":
                response = "MSG#" + client.name + "#" + data
                self.send_to_all(data=response, lock=lock)
            else:
                response = "MSG#" + client.name + "#" + data
                pos = 0
                while data[pos] != "#":
                    pos += 1
                self.send_to_one(data=response, name=data[0:pos], lock=lock)
        lock.acquire()
        client.close()
        lock.release()


def handle_server(server, serverSocket, lock):
    while True:
        conn, addr = serverSocket.accept()
        name = conn.recv(buforSize)
        client = server.get_client(name)
        if client:
            conn.send(b'0')
            conn.close()
        else:
            conn.send(b'1')
            client = Client(conn, name)
            server.userList.append(client)
            lock.acquire()
            print("LOGIN: " + client.name)
            response = "LIST_USER#ALL#"
            for item in server.userList:
                response += item.name + "#"
            lock.release()
            server.send_to_all(response, lock)
            Thread(target=server.handle_client, args=(client, lock)).start()


serwer = Server()
handle_server(serwer, serwer.server_socket, serwer.lock)

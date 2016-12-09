from threading import Thread, Lock
import socket

global host, port, buforSize, endClient, users, temp

host = 'localhost'
port = 44000
buforSize = 2048
endClient = False
users = []
temp = []


def send_data(client, lock):
    global endClient
    while True:
        if endClient:
            break
        data = str(raw_input())
        # "DOKOGO#MSG
        client.send(data)
        if send_data == "LOGOUT":
            lock.acquire()
            endClient = True
            client.close()
            lock.release()
            break


def recv_data(client, lock):
    global endClient
    while True:
        if endClient:
            break
        try:
            data = client.recv(buforSize)
        except:
            lock.acquire()
            endClient = True
            lock.release()
            break
        if not data:
            lock.acquire()
            endClient = True
            lock.release()
            break
        if data[0:4] == "LIST":
            response = data[9:]
            global users
            lock.acquire()
            users = response.split('#')
            users = filter(lambda a: a != '#' and a != '', users)
            print("Update users: ")
            for item in users:
                print(item)
            lock.release()
        elif data[0:3] == "MSG":
            global temp
            lock.acquire()
            response = data[3:]
            temp = response.split('#')
            temp = filter(lambda a: a != '#' and a != '', temp)
            print("From: " + temp[0])
            print("To: " + temp[1])
            print("Msg: " + temp[2])
            lock.release()


def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client_socket.connect((host, port))
    name = str(raw_input("Name: "))
    client_socket.send(name)
    print("BYL")
    response = client_socket.recv(buforSize)
    print("BYL" + response)
    if response == "0":
        print("ERROR. TRY AGAIN.")
        return
    if response == "1":
        print("BYL")
        # wyswietl okienko
        lock = Lock()
        Thread(target=send_data, args=(client_socket, lock)).start()
        Thread(target=recv_data, args=(client_socket, lock)).start()





start_client()

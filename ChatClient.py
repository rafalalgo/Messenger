import tkMessageBox
from threading import Thread, Lock
import socket
import Tkinter as tk

global name, host, port, buforSize, endClient, users, temp, lock, client_socket
global should, myapp, ok, message

host = 'localhost'
port = 44000
buforSize = 2048
endClient = False
users = []
temp = []
should = 0
myapp = None
message = ""


def send_data(client):
    global endClient, myapp, name, should
    while True:
        if should:
            data = myapp.users.curselection()
            if len(data) == 0:
                data = myapp.users.get(0) + "#"
            else:
                data = myapp.users.get(data[0]) + "#"
            res = myapp.textbox.get("1.0", tk.END)

            if len(res) <= 2:
                tkMessageBox.showerror("Error", "Nie podales wiadomosci do wyslania.")
                myapp.textbox.delete("1.0", tk.END)
                should = 0
                continue
            data += res
            myapp.textbox.delete("1.0", tk.END)
            client.send(data)
            if send_data == "LOGOUT":
                lock.acquire()
                endClient = True
                client.close()
                lock.release()
                break
            should = 0


def recv_data(client):
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
            global users, myapp
            lock.acquire()
            users = response.split('#')
            users = filter(lambda a: a != '#' and a != '', users)
            myapp.update_list()
            lock.release()
        elif data[0:3] == "MSG":
            global temp, message
            lock.acquire()
            response = data[3:]
            temp = response.split('#')
            temp = filter(lambda a: a != '#' and a != '', temp)
            message = temp[0] + " ==> " + temp[1] + ":\n"
            message += temp[2]
            lock.release()


def start_client():
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client_socket.connect((host, port))
    global name
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
        global lock
        lock = Lock()
        global myapp
        root = tk.Tk()
        myapp = MyApp(root)
        Thread(target=recv_data, args=(client_socket,)).start()
        Thread(target=send_data, args=(client_socket,)).start()
        root.mainloop()


class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat")
        self.root.minsize(600, 400)
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=2)
        self.root.columnconfigure(1, weight=1)
        self.ChatF = tk.Frame(self.root)
        self.ChatF.grid(column=0, row=0, sticky=tk.N + tk.S + tk.W + tk.E)
        self.ChatF.rowconfigure(0, weight=3)
        self.ChatF.rowconfigure(1, weight=2)
        self.ChatF.rowconfigure(2, weight=1)
        self.ChatF.columnconfigure(0, weight=1)

        self.UsersF = tk.Frame(self.root)
        self.UsersF.grid(column=1, row=0, sticky=tk.N + tk.S + tk.W + tk.E)
        self.UsersF.rowconfigure(0, weight=5)
        self.UsersF.rowconfigure(1, weight=1)
        self.UsersF.columnconfigure(0, weight=1)

        self.sendbutton = tk.Button(self.ChatF, text="Send Message")
        self.sendbutton.bind("<Button-1>", self.sending)
        self.sendbutton.grid(column=0, row=2, sticky=tk.N + tk.S + tk.W + tk.E)

        self.exitbutton = tk.Button(self.UsersF, text="Exit")
        self.exitbutton.bind("<Button-1>", self.exit)
        self.exitbutton.grid(column=0, row=1, sticky=tk.N + tk.S + tk.W + tk.E)

        self.textbox = tk.Text(self.ChatF, height=0, width=0)
        self.textbox.grid(column=0, row=1, sticky=tk.N + tk.S + tk.W + tk.E)
        self.textbox.grid(column=0, row=1, sticky=tk.N + tk.S + tk.W + tk.E)
        self.textbox.bind("<Return>", self.sending)

        self.chatbox = tk.Text(self.ChatF, height=0, width=0)
        self.chatbox.config(state=tk.DISABLED)
        self.chatbox.grid(column=0, row=0, sticky=tk.N + tk.S + tk.W + tk.E)

        self.users = tk.Listbox(self.UsersF, height=0, width=0)
        self.users.grid(column=0, row=0, sticky=tk.N + tk.S + tk.W + tk.E)
        self.num_users = 0
        self.update_list()
        Thread(target=self.run, args=[]).start()

    def sending(self, event):
        global should
        should = 1

    def update_list(self):
        self.users.delete(0, self.users.size())
        global users
        self.num_users = 0
        for item in users:
            self.users.insert(self.num_users, item)
            self.num_users += 1

    def exit(self, event):
        global should
        self.textbox.delete("1.0", tk.END)
        self.textbox.insert(tk.INSERT, "LOGOUT")
        should = 1
        self.root.destroy()

    def run(self):
        global message
        while 1:
            if len(message) > 1:
                lock.acquire()
                self.chatbox.config(state="normal")
                self.chatbox.insert(tk.INSERT, message)
                self.chatbox.config(state=tk.DISABLED)
                message = ""
                lock.release()


start_client()

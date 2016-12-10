import tkMessageBox
from threading import Thread, Lock
import socket
import sys
import Tkinter as tk


class MyWindow:
    def __init__(self, root, name):
        self.name = name
        self.root = root
        self.root.title("Chat: " + self.name)
        self.root.minsize(600, 400)
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=2)
        self.root.columnconfigure(1, weight=1)

        self.chatFrame = tk.Frame(self.root)
        self.chatFrame.grid(column=0, row=0, sticky=tk.N + tk.S + tk.W + tk.E)
        self.chatFrame.rowconfigure(0, weight=3)
        self.chatFrame.rowconfigure(1, weight=2)
        self.chatFrame.rowconfigure(2, weight=1)
        self.chatFrame.columnconfigure(0, weight=1)

        self.userListFrame = tk.Frame(self.root)
        self.userListFrame.grid(column=1, row=0, sticky=tk.N + tk.S + tk.W + tk.E)
        self.userListFrame.rowconfigure(0, weight=5)
        self.userListFrame.rowconfigure(1, weight=1)
        self.userListFrame.columnconfigure(0, weight=1)

        self.sendButton = tk.Button(self.chatFrame, text="Send Message")
        self.sendButton.grid(column=0, row=2, sticky=tk.N + tk.S + tk.W + tk.E)

        self.exitButton = tk.Button(self.userListFrame, text="Exit")
        self.exitButton.grid(column=0, row=1, sticky=tk.N + tk.S + tk.W + tk.E)

        self.textBox = tk.Text(self.chatFrame, height=0, width=0)
        self.textBox.grid(column=0, row=1, sticky=tk.N + tk.S + tk.W + tk.E)
        self.textBox.grid(column=0, row=1, sticky=tk.N + tk.S + tk.W + tk.E)

        self.chatBox = tk.Text(self.chatFrame, height=0, width=0)
        self.chatBox.config(state=tk.DISABLED)
        self.chatBox.grid(column=0, row=0, sticky=tk.N + tk.S + tk.W + tk.E)

        self.userList = tk.Listbox(self.userListFrame, height=0, width=0)
        self.userList.grid(column=0, row=0, sticky=tk.N + tk.S + tk.W + tk.E)


class MyApp:
    def __init__(self, root, name):
        self.myWindow = MyWindow(root, name)
        self.myWindow.sendButton.bind("<Button-1>", self.sending)
        self.myWindow.exitButton.bind("<Button-1>", self.exit)
        self.myWindow.textBox.bind("<Return>", self.sending)
        self.name = name
        self.num_userList = 0
        self.lock = Lock()
        self.should = False
        self.endClient = False
        self.nameUsers = []
        self.message = ""
        self.update_list()
        Thread(target=self.run, args=[]).start()

    def sending(self, event):
        self.should = True

    def update_list(self):
        self.myWindow.userList.delete(0, self.myWindow.userList.size())
        self.num_userList = 0
        for item in self.nameUsers:
            self.myWindow.userList.insert(self.num_userList, item)
            self.num_userList += 1

    def exit(self, event):
        global client_socket
        self.should = True
        self.endClient = True
        client_socket.send("LOGOUT")
        client_socket.close()
        self.myWindow.root.destroy()
        sys.exit()

    def run(self):
        while 1:
            print(3)
            if self.endClient:
                break
            if len(self.message) > 1:
                self.lock.acquire()
                self.myWindow.chatBox.config(state="normal")
                self.myWindow.chatBox.insert(tk.INSERT, self.message)
                self.myWindow.chatBox.config(state=tk.DISABLED)
                self.message = ""
                self.lock.release()

    def send_data(self, client):
        while True:
            print(1)
            if self.endClient:
                return
            if self.should:
                data = self.myWindow.userList.curselection()
                if len(data) == 0:
                    data = self.myWindow.userList.get(0) + "#"
                else:
                    data = self.myWindow.userList.get(data[0]) + "#"
                res = self.myWindow.textBox.get("1.0", tk.END)
                print("\t\t" + res)
                if len(res) <= 1:
                    tkMessageBox.showerror("Error", "Nie podales wiadomosci do wyslania.")
                    self.textBox.delete("1.0", tk.END)
                    self.should = 0
                    continue
                data += res
                self.myWindow.textBox.delete("1.0", tk.END)
                client.send(data)
                if self.send_data == "LOGOUT":
                    self.lock.acquire()
                    self.endClient = True
                    client.close()
                    self.lock.release()
                    break
                self.should = False

    def recv_data(self, client):
        while True:
            print(2)
            if self.endClient:
                return
            try:
                data = client.recv(buforSize)
            except:
                self.lock.acquire()
                self.endClient = True
                self.lock.release()
                break
            if not data:
                self.lock.acquire()
                self.endClient = True
                self.lock.release()
                break
            if data[0:4] == "LIST":
                data = data[9:]
                self.lock.acquire()
                self.nameUsers = data.split('#')
                self.nameUsers = filter(lambda a: a != '#' and a != '', self.nameUsers)
                self.update_list()
                self.lock.release()
            elif data[0:3] == "MSG":
                self.lock.acquire()
                data = data[3:]
                temp = data.split('#')
                temp = filter(lambda a: a != '#' and a != '', temp)
                self.message = temp[0] + " ==> " + temp[1] + ":\n"
                self.message += temp[2]
                self.lock.release()


host = 'localhost'
port = 44000
buforSize = 2048
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client_socket.connect((host, port))

nameN = str(raw_input("Name: "))
client_socket.send(nameN)
response = client_socket.recv(buforSize)

if response == "0":
    print("ERROR. TRY AGAIN.")
if response == "1":
    rootR = tk.Tk()
    myapp = MyApp(rootR, nameN)
    recv_thread = Thread(target=myapp.recv_data, args=(client_socket,))
    recv_thread.start()
    send_thread = Thread(target=myapp.send_data, args=(client_socket,))
    send_thread.start()
    rootR.mainloop()

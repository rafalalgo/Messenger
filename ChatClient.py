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


class Client:
    def __init__(self, root, name):
        self.myWindow = MyWindow(root, name)
        self.myWindow.sendButton.bind("<Button-1>", self.send_data_gui)
        self.myWindow.exitButton.bind("<Button-1>", self.exit)
        self.myWindow.textBox.bind("<Return>", self.send_data_gui)
        self.myWindow.root.bind("<Destroy>", self.exit)
        self.name = name
        self.isEndClient = False

        self.msgRecv = ""
        self.newMsgRecv = False

        self.userList = []
        self.userListSize = 0
        self.newUserList = True

        self.msgSend = ""
        self.newMsgSend = False

        self.lock = Lock()

        Thread(target=self.recv_data_gui, args=[]).start()

    def send_data_gui(self, event):
        self.lock.acquire()
        self.msgSend = self.myWindow.userList.curselection()
        if len(self.msgSend) == 0:
            self.msgSend = self.myWindow.userList.get(0) + "#"
        else:
            self.msgSend = self.myWindow.userList.get(self.msgSend[0]) + "#"
        res = self.myWindow.textBox.get("1.0", tk.END)
        if len(res) <= 1 or res == "\n":
            tkMessageBox.showerror("Error", "Nie podales wiadomosci do wyslania.")
            self.textBox.delete("1.0", tk.END)
            self.newMsgSend = False
        else:
            self.msgSend += res
            self.myWindow.textBox.delete("1.0", tk.END)
            self.newMsgSend = True
        self.lock.release()

    def recv_data_gui(self):
        while 1:
            if self.isEndClient:
                break
            if self.newMsgRecv:
                self.lock.acquire()
                self.myWindow.chatBox.config(state="normal")
                self.myWindow.chatBox.insert(tk.INSERT, self.msgRecv)
                self.myWindow.chatBox.config(state=tk.DISABLED)
                self.msgRecv = ""
                self.newMsgRecv = False
                self.lock.release()
            if self.newUserList:
                self.myWindow.userList.delete(0, self.myWindow.userList.size())
                self.userListSize = 0
                for item in self.userList:
                    self.myWindow.userList.insert(self.userListSize, item)
                    self.userListSize += 1
                self.newUserList = False

    def send_data_thread(self, client):
        while True:
            if self.isEndClient:
                return
            if self.newMsgSend:
                client.send(self.msgSend)
                if self.send_data_thread == "LOGOUT":
                    self.lock.acquire()
                    self.isEndClient = True
                    client.close()
                    self.lock.release()
                    break
                self.newMsgSend = False

    def recv_data_thread(self, client):
        while True:
            if self.isEndClient:
                return
            try:
                self.msgRecv = client.recv(buforSize)
            except:
                self.lock.acquire()
                self.isEndClient = True
                self.lock.release()
                break
            if not self.msgRecv:
                self.lock.acquire()
                self.isEndClient = True
                self.lock.release()
                break
            if self.msgRecv[0:4] == "LIST":
                self.lock.acquire()
                self.userList = self.msgRecv[9:].split('#')
                self.userList = filter(lambda a: a != '#' and a != '', self.userList)
                self.newMsgRecv = False
                self.newUserList = True
                self.lock.release()
            elif self.msgRecv[0:3] == "MSG":
                self.lock.acquire()
                self.msgRecv = filter(lambda a: a != '#' and a != '', self.msgRecv[3:].split('#'))
                self.msgRecv = self.msgRecv[0] + " ==> " + self.msgRecv[1] + ":\n" + self.msgRecv[2]
                self.newUserList = False
                self.newMsgRecv = True
                self.lock.release()

    def exit(self, event):
        global client_socket
        self.newMsgSend = True
        self.isEndClient = True
        client_socket.send("LOGOUT")
        client_socket.close()
        sys.exit()

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
    c = Client(rootR, nameN)
    recv_thread = Thread(target=c.recv_data_thread, args=(client_socket,))
    recv_thread.start()
    send_thread = Thread(target=c.send_data_thread, args=(client_socket,))
    send_thread.start()
    rootR.mainloop()

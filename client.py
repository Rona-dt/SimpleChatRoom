from socket import *
import threading
from tkinter import *


SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000


def start(sock):
    while True:
        global username
        log_option = input("Choose LOGIN or SIGNUP:")
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        send_msg = ("{}+{}+{}".format(log_option, username, password))
        sock.send(send_msg.encode('utf-8'))
        data = sock.recv(4096).decode("utf-8")
        if not data:
            return
        status, message = data.strip().split(":")
        print(data)
        if status == "Succeed_1":
            t1 = threading.Thread(target=reader, args=[sock])
            t2 = threading.Thread(target=writer, args=[sock])
            t1.start()
            t2.start()
            t1.join()
            t2.join()
        elif status == "Succeed_2":
            pass
        elif status == "Error":
            pass
        else:
            raise Exception("Not defined status!", status)


def reader(sock: socket):
    while True:
        data = sock.recv(4096).decode('utf-8')
        if not data:
            break
        print(data)

def writer(sock: socket):
    while True:
        data = input("").encode('utf-8')
        sock.send(data)

if __name__ == "__main__":
    try:
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        clientSocket.connect((SERVER_IP, SERVER_PORT))
        start(clientSocket)

    except Exception as msg:
        print("Connection establishment in client " + str(msg))
        print(msg)


from socket import *
from threading import *
from tkinter import *

SERVER_IP = "127.0.0.1"
SERVER_PORT = "5000"

# creat server socket
serverSocket = socket(AF_INET, SOCK_STREAM)
# keep the port ready to be reused soon after close connection
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
# bind the ip address and port number to socket with socket descriptor
serverSocket.bind(SERVER_IP,SERVER_PORT)
# listen for clients' request; the parameter controls the number of concurrent connections that have not been accept()
serverSocket.listen(5)







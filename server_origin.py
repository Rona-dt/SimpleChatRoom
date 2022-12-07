from socket import *
import threading
import traceback

SERVER_IP = "127.0.0.1"
SERVER_PORT = 1240
# Dictionary of accounts and password
accounts = {}
# List of logged-in user_name
user_logged = []
# List of client connections
connections = []
# Buffer to store and synchronize
recv_buf = []
# Mutex to synchronize the access to the buffer
mutex = threading.Lock()
# File to store the chat history
CHAT_FILE = "chat_history.txt"


def authentication(sock, addr):
    while True:
        try:
            data = sock.recv(4096).decode("utf-8")
            if not data:
                return
            log_option, username, password = data.strip().split("+")

            if log_option == "signin":
                if username in accounts:
                    if accounts[username] == password:
                        sock.send("Succeed_1:Successfully log in!".encode("utf-8"))
                        user_logged.append(username)
                        connections.append(sock)
                        # Start message-handling thread
                        threading.Thread(target=handle_message, args=(sock, addr, username), daemon=True).start()
                        return
                    else:
                        sock.send("Error:Incorrect password.\nTry again".encode("utf-8"))
                        continue
                else:
                    sock.send("Error:Incorrect username.\nTry again or sign up first".encode("utf-8"))
                    continue

            elif log_option == "signup":
                if username in accounts:
                    sock.send("Error:The username has already been used.\nplease use another one.".encode("utf-8"))
                    continue
                else:
                    accounts[username] = password
                    sock.send("Succeed_2:Now you can log in!".encode("utf-8"))
                    continue
        except Exception as msg_1:
            traceback.print_exc()
            sock.close()


def handle_message(sock, addr, username):
    while True:
        try:
            data = sock.recv(4096).decode("utf-8")
            if not data:
                return

            # Acquire the mutex lock before accessing the buffer
            with mutex:
                recv_buf.append((username, data))

                # Write the message to the chat history file
                with open(CHAT_FILE, "a") as file:
                    file.write(f"{username} from {addr}: {data}\n")

                # Broadcast the message to all connected clients
                broadcast_message(f"{username} from {addr}: {data}")

        except Exception as msg_2:
            print("Handling message in server:" + str(msg_2))
            sock.close()


# Function to broadcast a message to all connected clients
def broadcast_message(msg):
    print("broadcast")
    for conn in connections:
        conn.send(msg.encode("utf-8"))


try:
    # Creat a server socket
    serverSocket = socket(AF_INET, SOCK_STREAM)
    # Keep the port ready to be reused soon after close connection
    serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    # Bind the ip address and port number to socket with socket descriptor
    serverSocket.bind((SERVER_IP, SERVER_PORT))
    # Listen for clients' request; the parameter controls the number of concurrent connections not accepted yet
    serverSocket.listen(5)
    print("Waiting for connection from clients...")

    while True:
        clientSocket, clientAddr = serverSocket.accept()
        print("Login/Signup page connections established from: ", clientAddr)
        # daemon = True: allow main thread to exit any time without waiting other threads to exit
        thread = threading.Thread(target=authentication, args=(clientSocket, clientAddr), daemon=True)
        thread.start()
except Exception as msg_3:
    print("Connection establishment in server: " + str(msg_3))
from socket import *
import threading


SERVER_IP = "127.0.0.1"
SERVER_PORT = "5000"
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


def create_connection(sock, addr):
    while True:
        try:
            data = sock.recv(4096).decode("utf-8")
            if not data:
                return
            log_option, username, password = data.decode().strip("+")

            if log_option == "LOGIN":
                if username in accounts:
                    if accounts[username] == password:
                        sock.send("Successfully log in!".encode("utf-8"))
                        user_logged.append(username)
                        connections.append(sock)
                        # Start message-handling thread
                        threading.Thread(target=handle_message, args=(sock, addr, username), daemon=True).start()
                        # return??
                    else:
                        sock.send("Error: Incorrect password. Try again".encode("utf-8"))
                        continue
                else:
                    sock.send("Error: Incorrect username. Try again or sign up first".encode("utf-8"))
                    continue

            elif log_option == "SIGNUP":
                if username in accounts:
                    sock.send("Error: The username has already been used, please use another one.".encode("utf-8"))
                    continue
                else:
                    accounts[username] = password
                    sock.send("User account has been successfully created! Now you can log in!")
                    continue

        except Exception as msg:
            print(msg)
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

        except Exception as msg:
            print(msg)
            sock.close()


# Function to broadcast a message to all connected clients
def broadcast_message(msg):
    for conn in connections:
        conn.send(msg.encode("utf-8"))


# Creat a server socket
serverSocket = socket(AF_INET, SOCK_STREAM)
# Keep the port ready to be reused soon after close connection
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
# Bind the ip address and port number to socket with socket descriptor
serverSocket.bind((SERVER_IP, SERVER_PORT))
# Listen for clients' request; the parameter controls the number of concurrent connections that have not been accept()
serverSocket.listen(5)
print("Waiting for connection from clients...")

while True:
    clientSocket, clientAddr = serverSocket.accept()
    print("Login/Signup page connections established from: ", clientAddr)
    # daemon = True: allow main thread to exit any time without waiting other threads to exit
    threading.Thread(target=create_connection, args=(clientSocket, clientAddr), daemon=True).start()

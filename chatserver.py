from socket import *
import threading
import traceback
import errno
import time
import json


# class of user
class User:
    def __init__(self, sock, username, password):
        self.sock = sock
        self.username = username
        self.password = password


# class of user list with related methods
class UserLis:
    def __init__(self) -> None:
        self.mutex = threading.Lock()
        self.lis: list[User] = []
        self.cur_name = []

    # add user to database when signup
    def add(self, user):
        with self.mutex:
            self.lis.append(user)

    # private function
    def find(self, name):
        with self.mutex:
            for u in self.lis:
                if name == u.username:
                    return u
            return None

    # remove user from the database when cancellation
    def rm(self, name):
        with self.mutex:
            user = self.find(name)
            self.lis.remove(user)
    
    # login credential matching
    def match(self, name, passwd):
        user = self.find(name)
        with self.mutex:
            if user == None:
                return ("Not registered", 0)

            if user.password != passwd:
                return ("Incorrect username or password", 0)

            if user.sock != None:
                return ("Already logged in", 0)

            return ("Successfully logged in", 1)
    
    # set the user status to activate (online)
    def activate(self, name, sock):
        print(f'User {name} entered the chatroom')
        with self.mutex:
            for user in self.lis:
                if user.username == name:
                    self.cur_name.append(name)
                    user.sock = sock
                    return
    
    # set the user status to deactivate (offline)
    def deactivate(self, name):
        print(f'User {name} left the chatroom')
        with self.mutex:
            for user in self.lis:
                if user.username == name:
                    self.cur_name.remove(name)
                    user.sock = None
                    return

    # update user list when user activate or deactivate
    def update_usr(self):
        with self.mutex:
            for user in self.lis:
                if user.sock != None:
                    data = {"type": "user_list", "data": self.cur_name}
                    user.sock.send(json.dumps(data).encode('utf-8'))

    # broadcast message to all the active user
    def broadcast(self, msg):
        with self.mutex:
            for user in self.lis:
                if user.sock != None:
                    data = {"type": "message", "data": msg}
                    user.sock.send(json.dumps(data).encode('utf-8'))

# class of chat room server
class ChatroomServer():
    def __init__(self, ip: str, port: int, file: str) -> None:
        self.ip = ip
        self.port = port
        self.file = file
        self.userlis = UserLis()

    # function of authentication process
    def auth(self, sock):
        while True:
            try:
                # receive data from client
                data = sock.recv(4096).decode("utf-8")
                if not data:
                    return
                option, name, passwd = data.strip().split("+")

                # sign in situation
                if option == "signin":
                    print("signin")
                    msg, status = self.userlis.match(name, passwd)
                    if status:
                        sock.send("Succeed_1:You are logged in!".encode("utf-8"))
                        self.userlis.activate(name, sock)
                        self.userlis.update_usr()
                        time.sleep(0.5)
                        self.userlis.broadcast(name + " entered the chatroom")
                        threading.Thread(target=self.handle_msg, args=[sock, name], daemon=True).start()
                        return
                    sock.send(('Error:' + msg).encode('utf-8'))

                # sign up situation
                elif option == "signup":
                    print("signup")
                    if self.userlis.find(name) != None:
                        sock.send("Error:please use another username.".encode("utf-8"))
                    else:
                        self.userlis.add(User(None, name, passwd))
                        print("singup")
                        sock.send("Succeed_2:Now you can log in!".encode("utf-8"))

            except Exception:
                traceback.print_exc()
                sock.close()

    # function to handle message(send and receive)
    def handle_msg(self, sock, name):
        while True:
            try:
                print("data waiting")
                data = sock.recv(4096).decode("utf-8")
                print(data)
                if not data:
                    self.userlis.deactivate(name)
                    return
                self.userlis.broadcast(f"{name}: {data}")

            except error as e:
                traceback.print_exc()
                if e.errno != errno.EPIPE:
                    traceback.print_exc()
                self.userlis.deactivate(name)
                self.userlis.update_usr()
                time.sleep(0.5)
                self.userlis.broadcast(name + " left the chatroom")
                sock.close()
                return

    # socket creation and connection
    def start(self):
        try:
            # Creat a server socket
            serverSocket = socket(AF_INET, SOCK_STREAM)
            # Keep the port ready to be reused soon after close connection
            serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            # Bind the ip address and port number to socket with socket descriptor
            serverSocket.bind((self.ip, self.port))
            # Listen for clients' request; the parameter controls the number of concurrent connections not accepted yet
            serverSocket.listen(5)
            print("Waiting for connection from clients...")

            while True:
                clientSocket, clientAddr = serverSocket.accept()
                print("Login/Signup page connections established from: ", clientAddr)
                # daemon = True: allow main thread to exit any time without waiting other threads to exit
                threading.Thread(target=self.auth, args=[clientSocket], daemon=True).start()
        except Exception as msg_3:
            print("Connection establishment in server: " + str(msg_3))


if __name__ == '__main__':
    server = ChatroomServer("127.0.0.1", 3004, "chat_history.txt")
    server.start()

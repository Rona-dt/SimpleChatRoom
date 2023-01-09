from socket import *
import threading
from tkinter import *
from tkinter import messagebox
import time
import json
import os

SERVER_IP = "127.0.0.1"
SERVER_PORT = 3004


# represents a client
class ChatRoom:
    def __init__(self, rt, sock):
        self.user_count = 0
        self.cur_user = []
        self.user_list_display = None
        self.name = None
        self.msg = None
        self.entryMsg = None
        self.textDisplay = None
        self.msg_2 = None
        self.sock = sock
        self.root = rt
        # Set the format of the root window
        self.root.title("Login Page")
        self.root.geometry("400x300")
        self.root.resizable(width=False, height=False)
        self.root.configure(background="#adcceb")

        # Create a login page
        self.login_page = Frame(root)
        self.login_page.configure(background="#adcceb")

        # Add widgets to the login page
        self.username_label = Label(self.login_page, text="Username:", font=("Times New Roman", 12), foreground="black",
                                    background="#adcceb")
        self.username_entry = Entry(self.login_page)
        self.password_label = Label(self.login_page, text="Password:", font=("Times New Roman", 12), foreground="black",
                                    background="#adcceb")
        self.password_entry = Entry(self.login_page, show="*")
        print(self.login_page)
        self.signin_button = Button(self.login_page, text="Sign In", font=("Times New Roman", 12),
                                    command=lambda: self.log_in("signin"),
                                    activebackground="#adcceb")
        self.signup_button = Button(self.login_page, text="Sign Up", font=("Times New Roman", 12),
                                    command=lambda: self.log_in("signup"),
                                    activebackground="#adcceb")

        # Place the widgets on the login page
        self.username_label.grid(row=0, column=0, padx=40, pady=40, sticky='w')
        self.username_entry.grid(row=0, column=1, ipadx=20, pady=10)
        self.password_label.grid(row=1, column=0, padx=40, pady=10, sticky='w')
        self.password_entry.grid(row=1, column=1, ipadx=20, pady=10)
        self.signup_button.grid(row=2, column=0, columnspan=3, padx=20, pady=20, ipady=5)
        self.signin_button.grid(row=2, column=1, columnspan=3, padx=40, pady=20, ipady=5)

        # Show the login page
        self.login_page.grid()
        self.root.mainloop()

    # handle the authentication communication with server
    def log_in(self, log_option):
        # Get the user's username and password entered
        username = self.username_entry.get()
        password = self.password_entry.get()
        send_msg = ("{}+{}+{}".format(log_option, username, password))
        self.sock.send(send_msg.encode('utf-8'))
        data = self.sock.recv(4096).decode("utf-8")
        if not data:
            return
        status, message = data.strip().split(":")
        print(data)
        # Successfully sign in
        if status == "Succeed_1":
            self.bridge_loginChat(username)
        # Successfully sign up
        elif status == "Succeed_2" or status == "Error":
            # Show the status message
            label = Label(self.login_page, text=message, font=("Times New Roman", 12), foreground="white",
                          background="#adcceb")
            label.grid(row=3, padx=40, column=0, columnspan=3)
        else:
            raise Exception("Not defined status!", status)

    # bridge between authentication GUI and chat page GUI
    def bridge_loginChat(self, username):
        self.login_page.destroy()
        self.chat_page(username)
        threading.Thread(target=self.reader).start()

    # handle the action of quit
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
            os._exit(0)
            # sys.exit(0)

    # the chat page GUI
    def chat_page(self, username):
        self.name = username
        # modify the root windows
        self.root.deiconify()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.title("Chat Room")
        self.root.geometry("600x700")

        # create the window for chat page
        paned_window = PanedWindow(root, background="#d2e3f4")
        # create user list area
        user_area = Frame(paned_window)
        # create chat area
        chat_area = Frame(paned_window)

        # create user count label
        self.user_count = Label(user_area,
                                text="Current user number: " + str(len(self.cur_user)),
                                font=("Times New Roman", 12),
                                width=20,
                                height=2)
        self.user_count.place(relwidth=1)
        # create user listbox
        self.user_list_display = Listbox(user_area,
                                         activestyle='dotbox',
                                         font=("Times New Roman", 12),
                                         bg="#F0F0F0",
                                         height=10, width=20)
        self.user_list_display.place(relheight=1, relwidth=1, rely=0.08)

        # create head label
        head = Label(chat_area,
                     bg="#657f9a",
                     fg="#ffffff",
                     text="User: " + username,
                     font=("Times New Roman", 14),
                     height=2)

        head.place(relwidth=1)
        # create area to display communication message
        self.textDisplay = Text(chat_area,
                                width=20,
                                height=2,
                                bg="#adcceb",
                                fg="#000000",
                                font=("Times New Roman", 12),
                                padx=5,
                                pady=5)
        self.textDisplay.place(relheight=0.745,
                               relwidth=1,
                               rely=0.08)
        # create bottom label
        bottom = Label(chat_area,
                       bg="#657f9a",
                       height=80)

        bottom.place(relwidth=1,
                     rely=0.825)
        # create message input area
        self.entryMsg = Text(bottom,
                             bg="#ffffff",
                             fg="#000000",
                             font=("Times New Roman", 12))
        self.entryMsg.place(relwidth=0.74,
                            relheight=0.06,
                            rely=0.008,
                            relx=0.011)

        self.entryMsg.focus()
        # create a Send Button
        button_msg = Button(bottom,
                            text="Send",
                            font=("Times New Roman", 12),
                            width=20,
                            bg="#c1d5ec",
                            command=lambda: self.sendButton(self.entryMsg.get("1.0", 'end-1c')))

        button_msg.place(relx=0.77,
                         rely=0.008,
                         relheight=0.06,
                         relwidth=0.22)

        self.textDisplay.config(cursor="arrow")

        # create the scroll bar
        scrollbar = Scrollbar(self.textDisplay)
        scrollbar.place(relheight=1,
                        relx=0.974)
        scrollbar.config(command=self.textDisplay.yview)

        self.textDisplay.config(state=DISABLED)

        # place the user area in chat window
        user_area.grid_rowconfigure(0, weight=1)
        user_area.grid_columnconfigure(0, weight=1)
        # place the chat area in chat window
        chat_area.grid_rowconfigure(0, weight=1)
        chat_area.grid_columnconfigure(1, weight=1)
        # display the chat window
        paned_window.add(user_area, sticky='nsew', minsize=180)
        paned_window.add(chat_area, sticky='nsew', padx=2, pady=2)
        paned_window.grid(row=0, column=0, sticky='nsew')
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

    # create function for receiving message
    def reader(self):
        while True:
            try:
                # receive message
                data = self.sock.recv(1024).decode('utf-8')
                if not data:
                    break
                print(data)
                # load json data
                message = json.loads(data)
                # datatype: user list
                if message["type"] == "user_list":
                    self.cur_user = message["data"]
                    threading.Thread(target=self.update_user, args=[self.cur_user], daemon=True).start()
                # datatype: normal message
                elif message["type"] == "message":
                    self.textDisplay.config(state=NORMAL)
                    self.textDisplay.insert(END, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + "\n" + message[
                        "data"] + "\n\n")
                    self.textDisplay.config(state=DISABLED)
                    self.textDisplay.see(END)

            except Exception as msg_5:
                print("An error occurred!" + str(msg_5))
                self.sock.close()
                break

    # function triggered when send button clicking
    def sendButton(self, msg):
        self.textDisplay.config(state=DISABLED)
        self.msg = msg
        self.entryMsg.delete('1.0', END)
        threading.Thread(target=self.sendMessage).start()

    # function to send messages
    def sendMessage(self):
        self.textDisplay.config(state=DISABLED)
        while True:
            message = (f"{self.msg}")
            self.sock.send(message.encode('utf-8'))
            break

    # function to update the user list
    def update_user(self, cur_name):
        print(cur_name)
        self.user_list_display.delete(0, END)
        for name in cur_name:
            self.user_list_display.insert(END, name)
        self.user_count['text'] = str("Current user number: " + str(len(self.cur_user)))


if __name__ == "__main__":
    try:
        # socket creation and connection
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        clientSocket.connect((SERVER_IP, SERVER_PORT))
        root = Tk()
        window = ChatRoom(root, clientSocket)

    except Exception as msg:
        print("Connection establishment in client " + str(msg))
        print(msg)

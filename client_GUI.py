from socket import *
import threading
from tkinter import *
from tkinter import messagebox
import os
import sys

SERVER_IP = "127.0.0.1"
SERVER_PORT = 3002


class ChatRoom:
    def __init__(self, rt, sock):
        self.name = None
        self.msg = None
        self.labelHead = None
        self.labelBottom = None
        self.entryMsg = None
        self.textCons = None
        self.msg_2 = None
        self.sock = sock
        self.root = rt
        # Set the size of the root window
        self.root.title("Login Page")
        self.root.geometry("400x300")
        self.root.resizable(width=False, height=False)
        # Set the background color and font color of the root window
        self.root.configure(background="#aab8da")

        # Create a login page
        self.login_page = Frame(root)
        # Set the background color and font color of the login page
        self.login_page.configure(background="#aab8da")

        # Add widgets to the login page
        self.username_label = Label(self.login_page, text="Username:", font=("Times New Roman", 12), foreground="black",
                                    background="#aab8da")
        self.username_entry = Entry(self.login_page)
        self.password_label = Label(self.login_page, text="Password:", font=("Times New Roman", 12), foreground="black",
                                    background="#aab8da")
        self.password_entry = Entry(self.login_page, show="*")
        print(self.login_page)
        self.signin_button = Button(self.login_page, text="Sign In", font=("Times New Roman", 12), command=lambda: self.log_in("signin"),
                                    activebackground="#e3a996")
        self.signup_button = Button(self.login_page, text="Sign Up", font=("Times New Roman", 12), command=lambda: self.log_in("signup"),
                                    activebackground="#e3a996")

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
            label = Label(self.login_page, text=message, font=("Times New Roman", 12), foreground="white", background="#aab8da")
            label.grid(row=3, padx=40, column=0, columnspan=3)
        else:
            raise Exception("Not defined status!", status)

        # t1 = threading.Thread(target=self.reader, args=[self.sock])
        # t2 = threading.Thread(target=self.writer, args=[self.sock])
        # t1.start()
        # t2.start()
        # t1.join()
        # t2.join()

    def bridge_loginChat(self, username):
        self.login_page.destroy()
        self.chat_page(username)
        thread_recv = threading.Thread(target=self.reader)
        thread_recv.start()

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
            os._exit(0)
            # sys.exit(0)

    def chat_page(self, username):
        self.name = username
        self.root.deiconify()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.title("Chat Room")
        self.root.geometry("400x600")
        self.root.resizable(width=False,
                            height=False)
        self.root.configure(width=470,
                            height=700,
                            bg="#d2e3f4")
        self.labelHead = Label(self.root,
                               bg="#657f9a",
                               fg="#ffffff",
                               text="User: " + username,
                               font=("Times New Roman", 12),
                               pady=5)

        self.labelHead.place(relwidth=1)
        # line = Label(self.root,
        #              width=450,
        #              bg="#d2e3f4")
        #
        # line.place(relwidth=1,
        #            rely=0.07,
        #            relheight=0.012)

        self.textCons = Text(self.root,
                             width=20,
                             height=2,
                             bg="#adcceb",
                             fg="#000000",
                             font=("Times New Roman", 12),
                             padx=5,
                             pady=5)

        self.textCons.place(relheight=0.745,
                            relwidth=1,
                            rely=0.08)

        self.labelBottom = Label(self.root,
                                 bg="#657f9a",
                                 height=80)

        self.labelBottom.place(relwidth=1,
                               rely=0.825)

        self.entryMsg = Text(self.labelBottom,
                              bg="#ffffff",
                              fg="#000000",
                              font=("Times New Roman", 12))

        # place the given widget
        # into the gui window
        self.entryMsg.place(relwidth=0.74,
                            relheight=0.06,
                            rely=0.008,
                            relx=0.011)

        self.entryMsg.focus()

        # create a Send Button
        buttonMsg = Button(self.labelBottom,
                           text="Send",
                           font=("Times New Roman", 12),
                           width=20,
                           bg="#c1d5ec",
                           command=lambda: self.sendButton(self.entryMsg.get("1.0",'end-1c')))

        buttonMsg.place(relx=0.77,
                        rely=0.008,
                        relheight=0.06,
                        relwidth=0.22)

        self.textCons.config(cursor="arrow")

        # create a scroll bar
        scrollbar = Scrollbar(self.textCons)

        # place the scroll bar
        # into the gui window
        scrollbar.place(relheight=1,
                        relx=0.974)

        scrollbar.config(command=self.textCons.yview)

        self.textCons.config(state=DISABLED)

    def reader(self):
        while True:
            try:
                data = self.sock.recv(4096).decode('utf-8')
                if not data:
                    break
                print(data)
                self.textCons.config(state=NORMAL)
                self.textCons.insert(END,
                                     data + "\n\n")

                self.textCons.config(state=DISABLED)
                self.textCons.see(END)

            except Exception as msg_5:
                print("An error occurred!" + str(msg_5))
                self.sock.close()
                break

    def sendButton(self, msg):
        self.textCons.config(state=DISABLED)
        self.msg = msg
        # self.entryMsg.delete(0, END)
        self.entryMsg.delete('1.0', END)
        snd = threading.Thread(target=self.sendMessage)
        snd.start()

    # function to send messages
    def sendMessage(self):
        self.textCons.config(state=DISABLED)
        while True:
            message = (f"{self.msg}")
            self.sock.send(message.encode('utf-8'))
            break

if __name__ == "__main__":
    try:
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        clientSocket.connect((SERVER_IP, SERVER_PORT))
        root = Tk()
        window = ChatRoom(root, clientSocket)

    except Exception as msg:
        print("Connection establishment in client " + str(msg))
        print(msg)

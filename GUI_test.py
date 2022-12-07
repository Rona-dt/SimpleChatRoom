from tkinter import *

# Function to authenticate the user's username and password
def authenticate_user():
    # Get the user's username and password
    username = username_entry.get()
    password = password_entry.get()

    # Authenticate the user's credentials
    if username == "admin" and password == "password":
        # Show the chat page
        login_page.grid_forget()
        chat_page.grid()
    else:
        # Show an error message
        error_label = Label(login_page, text="Invalid username or password", font=("Arial", 12), foreground="white", background="#002366")
        error_label.grid(row=3, padx=40, column=0, columnspan=3)

def send_message():
    print("yes")

# Create the root window
root = Tk()
# Set the size of the root window
root.title("Login Page")
root.geometry("400x300")
# Set the background color and font color of the root window
root.configure(background="#002366")

# Create a login page
login_page = Frame(root)
# Set the background color and font color of the login page
login_page.configure(background="#002366")

# Add widgets to the login page
username_label = Label(login_page, text="Username:", font=("Arial", 12), foreground="white", background="#002366")
username_entry = Entry(login_page)
password_label = Label(login_page, text="Password:", font=("Arial", 12), foreground="white", background="#002366")
password_entry = Entry(login_page, show="*")
signin_button = Button(login_page, text="Sign In", command=authenticate_user)
signup_button = Button(login_page, text="Sign Up", command=authenticate_user)

# Place the widgets on the login page
username_label.grid(row=0, column=0, padx=40, pady=40, sticky='w')
username_entry.grid(row=0, column=1, ipadx=20, pady=10)
password_label.grid(row=1, column=0, padx=40, pady=10, sticky='w')
password_entry.grid(row=1, column=1, ipadx=20, pady=10)
signup_button.grid(row=2, column=0, columnspan=3, padx=20, pady=20, ipady=5)
signin_button.grid(row=2, column=1, columnspan=3, padx=40, pady=20, ipady=5)

# Show the login page
login_page.grid()

# Create a chat page
chat_page = Frame(root)

# Add widgets to the chat page
chat_label = Label(chat_page, text="Chat:")
chat_text = Text(chat_page)
send_button = Button(chat_page, text="Send", command=send_message)

# Place the widgets on the chat page
chat_label.grid(row=0, column=0)
chat_text.grid(row=1, column=0)
send_button.grid(row=2, column=1)

# Hide the chat page by default
chat_page.grid_forget()

# Start the main event loop
root.mainloop()
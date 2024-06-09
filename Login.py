import tkinter as tk
from tkinter import messagebox
import sqlite3

# Database setup
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL
)
''')
conn.commit()

def register_user():
    username = entry_register_username.get()
    password = entry_register_password.get()

    if username == "" or password == "":
        messagebox.showwarning("Registration Failed", "Please fill out all fields")
        return

    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        messagebox.showinfo("Registration Success", "User registered successfully")
        entry_register_username.delete(0, tk.END)
        entry_register_password.delete(0, tk.END)
    except sqlite3.IntegrityError:
        messagebox.showwarning("Registration Failed", "Username already exists")

def login_user():
    username = entry_login_username.get()
    password = entry_login_password.get()

    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()

    if user:
        messagebox.showinfo("Login Success", "Logged in successfully")
        entry_login_username.delete(0, tk.END)
        entry_login_password.delete(0, tk.END)
    else:
        messagebox.showwarning("Login Failed", "Invalid username or password")

def toggle_frame():
    if var_toggle.get() == 1:
        frame_register.pack_forget()
        frame_login.pack(pady=20)
    else:
        frame_login.pack_forget()
        frame_register.pack(pady=20)

# GUI setup
window = tk.Tk()
window.title("Login and Registration System")
window.attributes('-fullscreen', True)
window.configure(bg='#f0f0f0')

# Exit button to close the fullscreen window
def exit_fullscreen(event=None):
    window.attributes('-fullscreen', False)

window.bind("<Escape>", exit_fullscreen)

# Toggle Frame
frame_toggle = tk.Frame(window, bg='#f0f0f0')
frame_toggle.pack(pady=20)

var_toggle = tk.IntVar(value=1)

radio_login = tk.Radiobutton(frame_toggle, text="Login", variable=var_toggle, value=1, command=toggle_frame, font=('Helvetica', 14), bg='#f0f0f0')
radio_login.grid(row=0, column=0, padx=20)

radio_register = tk.Radiobutton(frame_toggle, text="Register", variable=var_toggle, value=2, command=toggle_frame, font=('Helvetica', 14), bg='#f0f0f0')
radio_register.grid(row=0, column=1, padx=20)

# Registration Frame
frame_register = tk.Frame(window, bg='#f0f0f0')

label_register = tk.Label(frame_register, text="Register", font=('Helvetica', 20, 'bold'), bg='#f0f0f0')
label_register.grid(row=0, columnspan=2, pady=10)

label_register_username = tk.Label(frame_register, text="Username", font=('Helvetica', 14), bg='#f0f0f0')
label_register_username.grid(row=1, column=0, pady=5)
entry_register_username = tk.Entry(frame_register, font=('Helvetica', 14), width=25)
entry_register_username.grid(row=1, column=1, pady=5)

label_register_password = tk.Label(frame_register, text="Password", font=('Helvetica', 14), bg='#f0f0f0')
label_register_password.grid(row=2, column=0, pady=5)
entry_register_password = tk.Entry(frame_register, show='*', font=('Helvetica', 14), width=25)
entry_register_password.grid(row=2, column=1, pady=5)

button_register = tk.Button(frame_register, text="Register", command=register_user, font=('Helvetica', 14), bg='#4CAF50', fg='white', width=15)
button_register.grid(row=3, columnspan=2, pady=10)

# Login Frame
frame_login = tk.Frame(window, bg='#f0f0f0')

label_login = tk.Label(frame_login, text="Login", font=('Helvetica', 20, 'bold'), bg='#f0f0f0')
label_login.grid(row=0, columnspan=2, pady=10)

label_login_username = tk.Label(frame_login, text="Username", font=('Helvetica', 14), bg='#f0f0f0')
label_login_username.grid(row=1, column=0, pady=5)
entry_login_username = tk.Entry(frame_login, font=('Helvetica', 14), width=25)
entry_login_username.grid(row=1, column=1, pady=5)

label_login_password = tk.Label(frame_login, text="Password", font=('Helvetica', 14), bg='#f0f0f0')
label_login_password.grid(row=2, column=0, pady=5)
entry_login_password = tk.Entry(frame_login, show='*', font=('Helvetica', 14), width=25)
entry_login_password.grid(row=2, column=1, pady=5)

button_login = tk.Button(frame_login, text="Login", command=login_user, font=('Helvetica', 14), bg='#4CAF50', fg='white', width=15)
button_login.grid(row=3, columnspan=2, pady=10)

# Show the initial frame
frame_login.pack(pady=20)

window.mainloop()

# Close database connection
conn.close()

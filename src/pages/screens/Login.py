from tkinter import messagebox
from src.logger import ERROR_LOG
from src.constants import COLOR_SCHEME, IS_DEBUG
from src.pages.template import BaseTemplate, App
from tkinter import messagebox
import customtkinter as ctk  # type: ignore


class Login(BaseTemplate):
    """Login Page"""

    def __init__(self, outer: App) -> None:
        super().__init__(outer)

        ctk.CTkLabel(
            master=self.frame,
            text="Admin Login Page",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 25, "bold"),
            width=250,
        ).pack(pady=20, padx=10)

        frame = ctk.CTkFrame(master=self.frame, fg_color=COLOR_SCHEME["fg_color"])
        ctk.CTkLabel(
            master=frame,
            text="Username:",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
        ).pack(padx=10, pady=10, side="left")

        self.user_entry = ctk.CTkEntry(
            master=frame,
            placeholder_text="Username",
            width=250,
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
        )
        self.user_entry.pack(padx=10, pady=10, side="left")
        frame.pack()

        frame = ctk.CTkFrame(master=self.frame, fg_color=COLOR_SCHEME["fg_color"])
        ctk.CTkLabel(
            master=frame,
            text="Password:",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
        ).pack(padx=10, pady=10, side="left")
        self.user_password = ctk.CTkEntry(
            master=frame,
            placeholder_text="Password",
            show="*",
            width=250,
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
        )
        self.user_password.pack(padx=10, pady=10, side="left")
        frame.pack()

        ctk.CTkButton(
            master=self.frame,
            text="Login",
            command=self.login,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        ).pack(pady=10, padx=10)
        ctk.CTkButton(
            master=self.frame,
            text="Exit",
            command=self.quit,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        ).pack(pady=10, padx=10)

    def login(self) -> None:
        """Check username and password"""

        from src.pages.screens import Interface

        known_user = "admin"  # actual username
        known_pass = "kjs2024"  # actual password

        username = self.user_entry.get() if not IS_DEBUG else known_user
        password = self.user_password.get() if not IS_DEBUG else known_pass

        if not username or not password:
            messagebox.showwarning(
                title="Empty Field", message="Please fill the all fields"
            )
            return

        if known_user == username and known_pass == password:
            messagebox.showinfo(
                title="Login Successful", message="You have logged in Successfully"
            )

            ERROR_LOG.write_info("User Logged in")

            self.switch_screen(Interface)
        else:
            messagebox.showwarning(
                title="Wrong password", message="Please check your username/password"
            )

    def quit(self):
        if messagebox.askyesnocancel("Confirmation", "Are you sure you want to exit"):
            self.outer.APP.quit()

import os
import re
from pathlib import Path
from tkinter import filedialog, messagebox
import customtkinter as ctk  # type: ignore
from src.constants import APP_PATH, COLOR_SCHEME
from src.pages.template import BaseTemplate, App
from src.utils.guiHandler import GuiHandler
from src.utils.common import email_check, text_clean, year_check
from src.utils.mail import MailingWrapper


class SendMail(BaseTemplate):
    """Page for single mail"""

    chosen_institute = ctk.StringVar(value="Somaiya")
    chosen_type = ctk.StringVar(value="Teaching")
    chosen_month = ctk.StringVar(value="Jan")

    def __init__(self, outer: App):
        super().__init__(outer)

        ctk.CTkLabel(
            master=self.frame,
            text="Single Mail",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 25, "bold"),
            width=250,
        ).pack(pady=20, padx=10)

        frame = ctk.CTkFrame(master=self.frame, fg_color=COLOR_SCHEME["fg_color"])
        ctk.CTkLabel(
            master=frame,
            text="Selected PDF File:",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
        ).pack(padx=10, pady=10, side="left")
        self.file = ctk.CTkEntry(
            master=frame,
            width=100,
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
        )
        self.file.pack(padx=10, pady=10, side="left")
        frame.pack()

        self.browse_button = ctk.CTkButton(
            master=self.frame,
            text="Browse",
            command=self.browse_file,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.browse_button.pack(pady=10)

        frame = ctk.CTkFrame(master=self.frame, fg_color=COLOR_SCHEME["fg_color"])
        ctk.CTkLabel(
            master=frame,
            text="Institute:",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
        ).pack(padx=10, pady=10, side="left")
        self.toggle_institute = ctk.CTkOptionMenu(
            master=frame,
            variable=self.chosen_institute,
            values=list(self.outer.TOGGLE.keys()),
            command=self.changeType,
            button_color=COLOR_SCHEME["button_color"],
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.toggle_institute.pack(pady=10, padx=10)
        frame.pack()

        frame = ctk.CTkFrame(master=self.frame, fg_color=COLOR_SCHEME["fg_color"])
        ctk.CTkLabel(
            master=frame,
            text="Type:",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
        ).pack(padx=10, pady=10, side="left")
        self.toggle_type = ctk.CTkOptionMenu(
            master=frame,
            variable=self.chosen_type,
            values=self.outer.TOGGLE["Somaiya"],
            button_color=COLOR_SCHEME["button_color"],
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.toggle_type.pack(pady=10, padx=10)
        frame.pack()

        frame = ctk.CTkFrame(master=self.frame, fg_color=COLOR_SCHEME["fg_color"])
        ctk.CTkLabel(
            master=frame,
            text="Month:",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
        ).pack(padx=10, pady=10, side="left")
        self.toggle_month = ctk.CTkOptionMenu(
            master=frame,
            variable=self.chosen_month,
            values=[str(i).capitalize() for i in self.outer.MONTH],
            button_color=COLOR_SCHEME["button_color"],
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.toggle_month.pack(pady=10, padx=10)
        frame.pack()

        frame = ctk.CTkFrame(master=self.frame, fg_color=COLOR_SCHEME["fg_color"])
        ctk.CTkLabel(
            master=frame,
            text="Enter Year:",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
        ).pack(side="left", pady=10, padx=10)
        self.year = ctk.CTkEntry(
            master=frame,
            placeholder_text="Eg. 2024",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
            width=100,
        )
        self.year.pack(side="left", pady=10, padx=10)
        frame.pack()

        frame = ctk.CTkFrame(master=self.frame, fg_color=COLOR_SCHEME["fg_color"])
        ctk.CTkLabel(
            master=frame,
            text="Enter Employee ID:",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
        ).pack(side="left", pady=10, padx=10)
        self.emp_id = ctk.CTkEntry(
            master=frame,
            placeholder_text="Eg. 2200317",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
            width=150,
        )
        self.emp_id.pack(side="left", pady=10, padx=10)
        frame.pack()

        frame = ctk.CTkFrame(master=self.frame, fg_color=COLOR_SCHEME["fg_color"])
        ctk.CTkLabel(
            master=frame,
            text="Enter Employee Email:",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
        ).pack(side="left", pady=10, padx=10)
        self.email = ctk.CTkEntry(
            master=frame,
            placeholder_text="Eg. sample@somaiya.edu",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.email.pack(side="left", pady=10, padx=10)
        frame.pack()

        self.send_button = ctk.CTkButton(
            master=self.frame,
            text="Send Mail",
            command=self.send_mail,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.send_button.pack(pady=10, padx=10)

        self.back_button = ctk.CTkButton(
            master=self.frame,
            text="Back",
            command=self.back,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.back_button.pack(pady=10, padx=10)

        self.quit = ctk.CTkButton(
            master=self.frame,
            text="Quit the process",
            command=self.cancel_thread_wrapper,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )

        self.to_disable = list(self.get_widgets_to_disable())

    def cancel_thread_wrapper(self) -> None:
        """Wrapper for cancelling thread and process"""
        self.cancel_thread()

        GuiHandler.unlock_gui_button(self.to_disable)
        GuiHandler.remove_widget(self.quit)
        messagebox.showinfo("Email Status", "Email Sending Stopped")

    def send_mail_thread_wrapper(self) -> None:
        """Handles gui during mailing process"""
        GuiHandler.lock_gui_button(self.to_disable)
        GuiHandler.place_after(self.send_button, self.quit)
        done: bool | None = None

        while True:
            if self.stop_flag:
                break

            if not self.QUEUE.empty():
                done = self.QUEUE.get()
                self.clear_queue()
                break

        if done:
            messagebox.showinfo("Email Status", "Email Send Successfully")
        else:
            messagebox.showinfo("Email Status", "Email was not send successfully")

        GuiHandler.unlock_gui_button(self.to_disable)
        GuiHandler.remove_widget(self.quit)

    def changeType(self, *args, **kwargs):
        """changes type according to institute"""
        institute = self.chosen_institute.get()
        employee_type = self.outer.TOGGLE[institute]
        GuiHandler.setOptions(employee_type, self.toggle_type, self.chosen_type)

    def send_mail(self) -> None:
        """Sends mail"""
        file_path = self.file.get()
        toAddr = text_clean(self.email.get())
        month = self.chosen_month.get()
        year = text_clean(self.year.get())
        emp_id = text_clean(self.emp_id.get())

        if not year_check(year):
            messagebox.showwarning("Year Check", "Improper Year format")
            return

        if not email_check(toAddr):
            messagebox.showwarning("Email Check", "Improper Email Address format")
            return

        if not (re.match(r"^(\w+|\d+)\Z", emp_id)):
            messagebox.showwarning("Employee ID check", "Improper Employee ID format")
            return

        if not os.path.isfile(file_path):
            messagebox.showwarning("File Check", "Selected path is not a file")
            return

        if self.can_start_thread() and self.can_start_process():
            self.parallelize(
                MailingWrapper().change_state(month, year).attempt_mail_process,
                self.send_mail_thread_wrapper,
                process_args={
                    "pdf_path": Path(file_path),
                    "toAddr": toAddr,
                    "id": id,
                    "queue": self.QUEUE,
                },
            )

        else:
            messagebox.showerror(
                "Program Status", "Warning Background Process/Thread is still running"
            )

    def browse_file(self) -> None:
        """Browse for file to send"""
        file_path = filedialog.askopenfilename(
            filetypes=[("PDF Files", ".pdf")], initialdir=APP_PATH
        )

        if file_path:
            GuiHandler.change_file_holder(self.file, file_path)

    def back(self) -> None:
        """Back to MailCover"""
        from src.pages.screens import MailCover

        self.hide()
        self.clear_data()
        self.switch_screen(MailCover)

import os
from typing import Optional
from tkinter import messagebox, filedialog
from pathlib import Path
import customtkinter as ctk  # type: ignore
import pandas as pd  # type: ignore
from src.database import Database
from src.logger import ERROR_LOG
from src.mail import Mailing
from src.constants import APP_PATH, COLOR_SCHEME, MAIL_CRED
from src.pages.template import BaseTemplate, App
from src.utils.guiHandler import GuiHandler
from src.utils.databaseWrapper import DatabaseWrapper
from src.utils.common import year_check, mapping
from src.utils.mail import MailingWrapper


class SendBulkMail(BaseTemplate):
    """Page for Bulk Mailing"""

    chosen_institute = ctk.StringVar(value="Somaiya")
    chosen_type = ctk.StringVar(value="Teaching")
    chosen_month = ctk.StringVar(value="Jan")
    email_server = Mailing(**MAIL_CRED, error_log=ERROR_LOG)

    def __init__(self, outer: App):
        super().__init__(outer)

        ctk.CTkLabel(
            master=self.frame,
            text="Bulk Mail",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 25, "bold"),
            width=250,
        ).pack(pady=20, padx=10)

        frame = ctk.CTkFrame(master=self.frame, fg_color=COLOR_SCHEME["fg_color"])
        ctk.CTkLabel(
            master=frame,
            text="Selected Folder Location:",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
        ).pack(padx=10, pady=10, side="left")
        self.folder = ctk.CTkEntry(
            master=frame,
            width=100,
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
        )
        self.folder.pack(padx=10, pady=10, side="left")
        frame.pack()

        self.browse_button = ctk.CTkButton(
            master=self.frame,
            text="Browse",
            command=self.folder_browse,
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
        self.entry_institute = ctk.CTkOptionMenu(
            master=frame,
            variable=self.chosen_institute,
            values=list(self.outer.TOGGLE.keys()),
            command=self.changeType,
            button_color=COLOR_SCHEME["button_color"],
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.entry_institute.pack(pady=10, padx=10, side="left")
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
            values=self.outer.TOGGLE[list(self.outer.TOGGLE.keys())[0]],
            button_color=COLOR_SCHEME["button_color"],
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.toggle_type.pack(pady=10, padx=10, side="left")
        frame.pack()

        frame = ctk.CTkFrame(master=self.frame, fg_color=COLOR_SCHEME["fg_color"])
        ctk.CTkLabel(
            master=frame,
            text="Month:",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
        ).pack(padx=10, pady=10, side="left")
        self.entry_month = ctk.CTkOptionMenu(
            master=frame,
            variable=self.chosen_month,
            values=[str(i).capitalize() for i in self.outer.MONTH],
            button_color=COLOR_SCHEME["button_color"],
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.entry_month.pack(pady=10, padx=10, side="left")
        frame.pack()

        frame = ctk.CTkFrame(master=self.frame, fg_color=COLOR_SCHEME["fg_color"])
        ctk.CTkLabel(
            master=frame,
            text="Enter Year:",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
        ).pack(side="left", pady=10, padx=10)
        self.entry_year = ctk.CTkEntry(
            master=frame,
            placeholder_text="Eg. 2024",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
            width=100,
        )
        self.entry_year.pack(side="left", pady=10, padx=10)
        frame.pack()

        self.exists_table = ctk.CTkButton(
            master=self.frame,
            text="Check Database",
            command=self.table_exists,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.exists_table.pack(pady=10, padx=10)

        self.mail_button = ctk.CTkButton(
            master=self.frame,
            text="Send Emails",
            command=self.send_mail,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )

        self.back = ctk.CTkButton(
            master=self.frame,
            text="Back",
            command=self.button_mailing,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.back.pack(pady=10, padx=10)

        self.quit = ctk.CTkButton(
            master=self.frame,
            text="Quit the process",
            command=self.cancel_thread_wrapper,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )

        self.to_disable = list(self.get_widgets_to_disable())

    def changeType(self, *args, **kwargs):
        """changes type according to institute"""
        institute = self.chosen_institute.get()
        employee_type = self.outer.TOGGLE[institute]
        GuiHandler.setOptions(employee_type, self.toggle_type, self.chosen_type)

    def cancel_thread_wrapper(self) -> None:
        """Wrapper for cancelling thread and process"""
        self.cancel_thread()

        GuiHandler.unlock_gui_button(self.to_disable)
        GuiHandler.remove_widget(self.quit)
        messagebox.showinfo("Email Status", "Email Sending Stopped")

    def send_mail_thread_wrapper(self) -> None:
        """You know the drill"""
        GuiHandler.lock_gui_button(self.to_disable)
        GuiHandler.place_after(self.mail_button, self.quit)
        GuiHandler.changeCommand(self.quit, self.cancel_thread_wrapper)

        count, total = 0, 0

        while True:
            if self.stop_flag:
                break

            if not self.QUEUE.empty():
                curr = self.QUEUE.get()

                if curr == "Done":
                    self.clear_queue()
                    break

                elif isinstance(curr, tuple) and len(curr) == 2:
                    count, total = curr

        GuiHandler.unlock_gui_button(self.to_disable)
        GuiHandler.remove_widget(self.quit)
        self.email_result(count, total)

    def email_result(self, count: int, total: int) -> None:
        """Shows result after mailing is complete"""

        if (not self.stop_flag) and count > 0:
            messagebox.showinfo(
                "Email Status", f"{count}/{total} emails were send successfully"
            )
        elif (not self.stop_flag) and total > 0:
            messagebox.showinfo("Email Status", "No emails were send")

    def send_mail(self) -> None:
        """See name"""
        file_path = self.folder.get()
        month = self.chosen_month.get()
        year = self.entry_year.get()
        institute = self.chosen_institute.get()
        employee_type = self.chosen_type.get()

        if BaseTemplate.data is None:
            messagebox.showwarning(
                "Data Status",
                f"Data for {institute.capitalize()} {employee_type.capitalize()} {month.capitalize()}/{year} was not found. Please do the necessary",
            )
            return

        if not isinstance(BaseTemplate.data, pd.DataFrame):
            messagebox.showwarning("Invalid Data", "Invalid data present")
            return

        code_col = mapping(list(BaseTemplate.data.columns), "HR EMP CODE")
        email_col = None
        all_columns = list(BaseTemplate.data.columns)

        for i in all_columns:
            if "mail" in i.lower():
                email_col = i
                break

        if code_col is None or email_col is None:
            messagebox.showwarning(
                "Column Missing", "HR EMP CODE or Mail Column was not found"
            )
            return

        if not year_check(year):
            messagebox.showwarning("Year Check", "Improper Year format")
            return

        if not file_path:
            messagebox.showwarning("File Path Check", "File Path is empty")
            return

        if not os.path.isdir(file_path):
            messagebox.showwarning("File Check", "Selected path is not a directory")
            return

        if self.can_start_thread() and self.can_start_process():
            self.parallelize(
                MailingWrapper().change_state(month, year).massMail,
                self.send_mail_thread_wrapper,
                process_args={
                    "data": BaseTemplate.data,
                    "code_column": code_col,
                    "email_col": email_col,
                    "dir_path": Path(file_path),
                    "queue": self.QUEUE,
                },
            )

        else:
            messagebox.showerror(
                "Program Status", "Warning Background Process/Thread is still running"
            )

    def folder_browse(self) -> None:
        current_dir = os.path.dirname(APP_PATH)
        entry_folder = filedialog.askdirectory(initialdir=current_dir)

        if entry_folder:
            GuiHandler.change_file_holder(self.folder, entry_folder)

    def table_exists_thread(self) -> None:
        GuiHandler.lock_gui_button(self.to_disable)
        GuiHandler.changeCommand(self.quit, self.table_exists_cancel_thread)
        GuiHandler.place_after(self.exists_table, self.quit)

        data: Optional[pd.DataFrame] = None

        while True:
            if self.stop_flag:
                break

            if not self.QUEUE.empty():
                data = self.QUEUE.get()
                self.clear_queue()
                break

        if data is not None and not data.empty:
            GuiHandler.place_after(self.exists_table, self.mail_button)
            messagebox.showinfo(
                "Database Status",
                f"Table {Database.getTableName(self.chosen_month.get(),self.entry_year.get(),self.chosen_institute.get(),self.chosen_type.get())} exists in database. Mass Mailing available",  # type: ignore
            )
            BaseTemplate.data = data
        else:
            messagebox.showinfo(
                "Database Status",
                f"Table {
                    Database.getTableName(self.chosen_month.get(),self.entry_year.get(),self.chosen_institute.get(),self.chosen_type.get())} doesn't exist in database. Please upload data to database",  # type: ignore
            )

        GuiHandler.unlock_gui_button(self.to_disable)
        GuiHandler.remove_widget(self.quit)

    def table_exists_cancel_thread(self):
        self.cancel_thread()

        messagebox.showinfo("Database Status", "Process Halted")

        GuiHandler.unlock_gui_button(self.to_disable)
        GuiHandler.remove_widget(self.quit)

    def table_exists(self):
        month = self.chosen_month.get()
        year = self.entry_year.get()

        if not year_check(year):
            messagebox.showwarning("Year Check", "Improper Year format")
            return

        if self.can_start_thread() and self.can_start_process():
            self.parallelize(
                DatabaseWrapper(**self.outer.CRED).get_data,
                self.table_exists_thread,
                process_args={
                    "queue": self.QUEUE,
                    "institute": self.chosen_institute.get(),
                    "type": self.chosen_type.get(),
                    "year": year,
                    "month": month,
                },
            )

        else:
            messagebox.showerror(
                "Program Status", "Warning Background Process/Thread is still running"
            )

    def button_mailing(self) -> None:
        from src.pages.screens import MailCover

        self.clear_data()
        GuiHandler.remove_widget(self.mail_button)
        self.switch_screen(MailCover)

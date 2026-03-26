from tkinter import messagebox
import customtkinter as ctk  # type: ignore
from src.constants import COLOR_SCHEME
from src.pages.template import BaseTemplate, App
from src.utils.databaseWrapper import DatabaseWrapper
from src.utils.guiHandler import GuiHandler


class Interface(BaseTemplate):
    def __init__(self, outer: App) -> None:
        super().__init__(outer)

        ctk.CTkLabel(
            master=self.frame,
            text="Excel-To-PDF Generator",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 25, "bold"),
            width=250,
        ).pack(pady=20, padx=10)

        self.preview_db = ctk.CTkButton(
            master=self.frame,
            text="Preview Existing Data",
            command=self.preview,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.preview_db.pack(pady=10, padx=10)

        self.upload_button = ctk.CTkButton(
            master=self.frame,
            text="Upload Excel data",
            command=self.upload,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.upload_button.pack(pady=10, padx=10)

        self.mail_button = ctk.CTkButton(
            master=self.frame,
            text="Send Mail",
            command=self.mail,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.mail_button.pack(pady=10, padx=10)

        self.delete_button = ctk.CTkButton(
            master=self.frame,
            text="Delete Tables",
            command=self.delete,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.delete_button.pack(pady=10, padx=10)

        self.template_button = ctk.CTkButton(
            master=self.frame,
            text="Generate Salary-Slip Templates",
            command=self.template,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.template_button.pack(pady=10, padx=10)

        self.template_download_button = ctk.CTkButton(
            master=self.frame,
            text="Download Excel Templates",
            command=self.template_download,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.template_download_button.pack(pady=10, padx=10)

        self.back = ctk.CTkButton(
            master=self.frame,
            text="Back",
            command=self.back_to_login,
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

    def back_to_login(self) -> None:
        """back to setup page"""

        from src.pages.screens import Login

        self.switch_screen(Login)

    def upload(self) -> None:
        """proceeds to upload page"""
        from src.pages.screens import (
            FileInput,
        )

        self.switch_screen(FileInput)

    def mail(self) -> None:
        from src.pages.screens import (
            MailCover,
        )

        self.switch_screen(MailCover)

    def check_database_thread(self):
        GuiHandler.lock_gui_button(self.to_disable)
        GuiHandler.place_after(self.preview_db, self.quit)
        table = {}

        while True:
            if self.stop_flag:
                break

            if not self.QUEUE.empty():
                table = self.QUEUE.get()
                self.clear_queue()
                break

        if table:
            from src.pages.screens import DataPreview
            
            view: DataPreview = self.outer.Screens[DataPreview.__name__]  # type: ignore
            view.tables = table
            view.changeData()
            self.switch_screen(DataPreview)
        else:
            messagebox.showerror("SQLITE Error", "No data available to preview")

        GuiHandler.unlock_gui_button(self.to_disable)
        GuiHandler.remove_widget(self.quit)

    def cancel_thread_wrapper(self) -> None:
        self.cancel_thread()

        GuiHandler.unlock_gui_button(self.to_disable)
        GuiHandler.remove_widget(self.quit)
        messagebox.showinfo("Fetch Status", "Data Fetching Stopped")

    # proceeds to pre-existing data page
    def preview(self) -> None:
        if (self.can_start_thread() and self.can_start_process()):
            self.parallelize(
                DatabaseWrapper(**self.outer.CRED).check_table,
                self.check_database_thread,
                process_args={"queue": self.QUEUE},
            )
        else:
            messagebox.showerror(
                "Program Status", "Warning Background Process/Thread is still running"
            )

    def delete_database_thread(self):
        GuiHandler.lock_gui_button(self.to_disable)
        GuiHandler.place_after(self.delete_button, self.quit)
        table = {}

        while True:
            if self.stop_flag:
                break

            if not self.QUEUE.empty():
                table = self.QUEUE.get()
                self.clear_queue()
                break

        if table:
            from src.pages.screens import DataPeek
            
            view: DataPeek = self.outer.Screens[DataPeek.__name__] # type: ignore
            view.tables = table
            view.change_data()
            self.switch_screen(DataPeek)
        else:
            messagebox.showerror("SQLITE Error", "No data available to delete")

        GuiHandler.unlock_gui_button(self.to_disable)
        GuiHandler.remove_widget(self.quit)

    def delete(self) -> None:
        if self.can_start_thread() and self.can_start_process():
            self.parallelize(
                DatabaseWrapper(**self.outer.CRED).check_table,
                self.delete_database_thread,
                process_args={"queue": self.QUEUE},
            )

        else:
            messagebox.showerror(
                "Program Status", "Warning Background Process/Thread is still running"
            )

    def template(self) -> None:
        from src.pages.screens import TemplateInput
        
        self.switch_screen(TemplateInput)

    def template_download(self) -> None:
        from src.pages.screens import TemplateGeneration
        
        self.switch_screen(TemplateGeneration)

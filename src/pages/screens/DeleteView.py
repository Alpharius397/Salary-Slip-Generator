from tkinter import messagebox
import customtkinter as ctk  # type: ignore
from src.constants import COLOR_SCHEME
from src.pages.template import BaseTemplate, App
from src.utils.common import year_check
from src.utils.databaseWrapper import DatabaseWrapper
from src.utils.guiHandler import GuiHandler


class DeleteView(BaseTemplate):
    chosen_month = "None"
    chosen_year = "None"
    chosen_type = "None"
    chosen_institute = "None"

    def __init__(self, outer: App):
        super().__init__(outer)
        self.outer = outer
        master = self.outer.APP

        self.frame = ctk.CTkScrollableFrame(
            master=master,
            fg_color=COLOR_SCHEME["fg_color"],
        )

        self.label_date = ctk.CTkLabel(
            master=self.frame,
            text=f"Confirm Deletion of {self.chosen_institute.capitalize()} {self.chosen_type.capitalize()} {self.chosen_month.capitalize()}/{self.chosen_year.upper()}",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 25, "bold"),
            width=250,
        )
        self.label_date.pack(pady=20, padx=10)

        self.delete_button = ctk.CTkButton(
            master=self.frame,
            text="Delete Table",
            command=self.delete_from_db,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.delete_button.pack(pady=10)

        self.back = ctk.CTkButton(
            master=self.frame,
            text="Back",
            command=self.back_to_view,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.back.pack(pady=10, padx=10)

        self.quit = ctk.CTkButton(
            master=self.frame,
            text="Quit the Process",
            command=self.stop_delete_thread,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.to_disable = list(self.get_widgets_to_disable())

    # back to interface
    def changeHeading(self):
        GuiHandler.changeText(
            self.label_date,
            f"Confirm Deletion of {self.chosen_institute.capitalize()} {self.chosen_type.capitalize()} {self.chosen_month.capitalize()}/{self.chosen_year.upper()}",
        )

    def back_to_view(self) -> None:

        from src.pages.screens import DataPeek

        self.clear_data(True)
        self.clear_queue()
        self.switch_screen(DataPeek)
        view: DataPeek = self.outer.Screens[DataPeek.__name__]  # type: ignore
        view.preview()

    def stop_delete_thread(self):
        self.cancel_thread()
        GuiHandler.unlock_gui_button(self.to_disable)
        GuiHandler.remove_widget(self.quit)

        messagebox.showinfo("Process Status", "PDF Generation Cancelled")

    def delete_thread(self) -> None:
        GuiHandler.lock_gui_button(self.to_disable)
        GuiHandler.place_after(self.delete_button, self.quit)
        result: bool | None = None

        while True:
            if self.stop_flag:
                break

            if not self.QUEUE.empty():
                result = self.QUEUE.get()
                self.clear_queue()
                break

        if result:
            messagebox.showinfo("Database Status", "Table dropped successfully")
        elif result is not None:
            messagebox.showinfo("Database Status", "Table does not exists")
        else:
            messagebox.showinfo("Database Status", "SQLITE Error occurred")

        GuiHandler.unlock_gui_button(self.to_disable)
        GuiHandler.remove_widget(self.quit)

    def delete_from_db(self):
        institute = self.chosen_institute
        employee_type = self.chosen_type
        month = self.chosen_month
        year = self.chosen_year

        if year_check(year):
            if self.can_start_thread() and self.can_start_process() and messagebox.askyesnocancel(
                "Confirmation",
                f"Month: {month}, Year: {year} \n institute:{institute}, Type: {employee_type} \n Are you sure you want to clear this data from DB?",
            ):
                self.parallelize(
                    DatabaseWrapper(**self.outer.CRED).delete_table,
                    self.delete_thread,
                    process_args={
                        "queue": self.QUEUE,
                        "institute": institute,
                        "type": employee_type,
                        "year": year,
                        "month": month,
                    },
                )

            else:
                messagebox.showerror(
                    "Program Status",
                    "Warning Background Process/Thread is still running",
                )

        else:
            messagebox.showwarning("Alert", "Incorrect year format")

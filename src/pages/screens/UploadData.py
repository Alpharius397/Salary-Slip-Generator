from tkinter import Scrollbar, scrolledtext, messagebox
import customtkinter as ctk  # type: ignore
import tkinter as tk  # type: ignore
import pandas as pd
from src.constants import COLOR_SCHEME, MAX_TEXT_SIZE, MIN_TEXT_SIZE
from src.dataTypes import NullStr
from src.database import CreateTable, DeleteTable, UpdateTable
from src.pages.template import BaseTemplate, App
from src.utils.common import year_check
from src.utils.databaseWrapper import DatabaseWrapper
from src.utils.guiHandler import GuiHandler


class UploadData(BaseTemplate):
    size: int = 12
    chosen_institute = ctk.StringVar(value="Somaiya")
    chosen_type = ctk.StringVar(value="Teaching")
    chosen_month = ctk.StringVar(value="Jan")
    sheet: NullStr = None

    def __init__(self, outer: App):
        super().__init__(outer)

        # title
        ctk.CTkLabel(
            master=self.frame,
            text="Data Upload",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 25, "bold"),
            width=250,
        ).pack(pady=20, padx=10)

        # file path input
        ctk.CTkLabel(
            master=self.frame,
            text="Please Enter Details about data",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 18, "bold"),
        ).pack(padx=10, pady=10)

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

        self.create_button = ctk.CTkButton(
            master=self.frame,
            text="Create Table",
            command=self.create_in_db,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.create_button.pack(pady=10, padx=10)

        self.update_button = ctk.CTkButton(
            master=self.frame,
            text="Upload To DB",
            command=self.update_in_db,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )

        self.delete_button = ctk.CTkButton(
            master=self.frame,
            text="Delete from DB",
            command=self.delete_from_db,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.delete_button.pack(pady=10, padx=10)

        self.back = ctk.CTkButton(
            master=self.frame,
            text="Back",
            command=self.back_to_input,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.back.pack(pady=10, padx=10)

        ctk.CTkLabel(
            master=self.frame,
            text="Text Size of Sheet:",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        ).pack(pady=10, padx=10)

        frame = ctk.CTkFrame(master=self.frame, fg_color=COLOR_SCHEME["fg_color"])

        self.size_minus = ctk.CTkButton(
            master=frame,
            text="-",
            command=self.decrease_size,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=50,
        )
        self.size_minus.pack(side="left", padx=10)
        self.font_size = ctk.CTkLabel(
            master=frame,
            text=f"{self.size}",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
            width=100,
        )
        self.font_size.pack(side="left", padx=10)
        self.size_plus = ctk.CTkButton(
            master=frame,
            text="+",
            command=self.increase_size,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=50,
        )
        self.size_plus.pack(side="left", padx=10)
        frame.pack()

        self.text_excel = scrolledtext.ScrolledText(
            master=self.frame,
            width=300,
            height=50,
            bg="black",
            fg="white",
            wrap=tk.NONE,
            font=("Courier", 12),
        )
        x_scrollbar = Scrollbar(
            self.frame, orient="horizontal", command=self.text_excel.xview
        )
        x_scrollbar.pack(side="bottom", fill="x")

        self.text_excel.configure(xscrollcommand=x_scrollbar.set)
        self.text_excel.pack(pady=10, padx=10, fill="both", expand=True)

        self.quit = ctk.CTkButton(
            master=self.frame,
            text="Quit the Process",
            command=self.cancel_thread_wrapper,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.to_disable = list(self.get_widgets_to_disable())

    def back_to_input(self):
        from src.pages.screens import FileInput

        self.clear_data(hard=False)
        GuiHandler.remove_widget(self.update_button)
        GuiHandler.clear_excel(self.text_excel)
        self.switch_screen(FileInput)

    def cancel_thread_wrapper(self):
        self.cancel_thread()
        GuiHandler.unlock_gui_button(self.to_disable)
        GuiHandler.remove_widget(self.quit)

    def decrease_size(self):
        self.font_size.configure(text=max(MIN_TEXT_SIZE, self.size - 1))
        self.size = max(MIN_TEXT_SIZE, self.size - 1)

        GuiHandler.change_text_font(self.text_excel, self.size)
        GuiHandler.unlock_gui_button([self.size_plus])
        if self.size == MIN_TEXT_SIZE:
            GuiHandler.lock_gui_button([self.size_minus])

    def increase_size(self):
        self.font_size.configure(text=max(MAX_TEXT_SIZE, self.size + 1))
        self.size = max(MAX_TEXT_SIZE, self.size + 1)

        GuiHandler.change_text_font(self.text_excel, self.size)
        GuiHandler.unlock_gui_button([self.size_minus])
        if self.size == MAX_TEXT_SIZE:
            GuiHandler.lock_gui_button([self.size_plus])

    def changeType(self, *args, **kwargs):
        institute = self.chosen_institute.get()
        employee_str = self.outer.TOGGLE[institute]
        GuiHandler.setOptions(employee_str, self.toggle_type, self.chosen_type)

    def create_thread(self):
        GuiHandler.lock_gui_button(self.to_disable)
        GuiHandler.place_after(self.create_button, self.quit)
        result: int = 0

        while True:
            if self.stop_flag:
                break

            if not self.QUEUE.empty():
                result = self.QUEUE.get()
                self.clear_queue()
                break

        if result is not None:
            match result:
                case CreateTable.NO_ID:
                    messagebox.showwarning("Column Info", CreateTable.NO_ID)
                case CreateTable.SUCCESS:
                    messagebox.showinfo("Database Status", CreateTable.SUCCESS)
                case CreateTable.COLUMNS_MISMATCH:
                    messagebox.showinfo("Database Status", CreateTable.COLUMNS_MISMATCH)
                case CreateTable.ERROR:
                    messagebox.showerror("Database Status", CreateTable.ERROR)
                case CreateTable.EXISTS:
                    messagebox.showerror("Database Status", CreateTable.EXISTS)

            if result in {CreateTable.EXISTS, CreateTable.SUCCESS}:
                GuiHandler.place_after(self.create_button, self.update_button)

        else:
            messagebox.showinfo("Database Status", "SQLITE Error occurred")

        GuiHandler.unlock_gui_button(self.to_disable)
        GuiHandler.remove_widget(self.quit)

    def create_in_db(self):
        institute = self.chosen_institute.get()
        employee_str = self.chosen_type.get()
        month = self.chosen_month.get()
        year = self.entry_year.get()

        if self.sheet is None:
            messagebox.showwarning("Excel Sheet", "Excel Sheet was not chosen")
            return

        if year_check(year):
            if self.can_start_process() and self.can_start_thread() and messagebox.askyesnocancel(
                "Confirmation",
                f"Month: {month}, Year: {year} \n Institute: {institute}, Type: {employee_str} \n Are you sure details are correct?",
            ):
                if isinstance(BaseTemplate.data, dict):

                    self.parallelize(
                        DatabaseWrapper(**self.outer.CRED).create_table,
                        self.create_thread,
                        process_args={
                            "queue": self.QUEUE,
                            "institute": institute,
                            "type": employee_str,
                            "year": year,
                            "month": month,
                            "data_columns": list(
                                BaseTemplate.data[  # pylint: disable=unsubscriptable-object
                                    self.sheet
                                ].columns
                            ),
                        },
                    )

        else:
            messagebox.showwarning("Alert", "Incorrect year format")

    def update_thread(self):
        GuiHandler.lock_gui_button(self.to_disable)
        GuiHandler.place_after(self.update_button, self.quit)
        result: int = 0

        while True:
            if self.stop_flag:
                break

            if not self.QUEUE.empty():
                result = self.QUEUE.get()
                self.clear_queue()
                break

        if result is not None:
            match result:
                case UpdateTable.COLUMNS_MISMATCH:
                    messagebox.showwarning("Column Info", UpdateTable.COLUMNS_MISMATCH)
                case UpdateTable.NO_ID:
                    messagebox.showwarning("Column Info", UpdateTable.NO_ID)
                case UpdateTable.ERROR:
                    messagebox.showinfo("Database Status", UpdateTable.ERROR)
                case UpdateTable.SUCCESS:
                    messagebox.showinfo("Database Status", UpdateTable.SUCCESS)

        else:
            messagebox.showinfo("Database Status", "SQLITE Error occurred")

        GuiHandler.unlock_gui_button(self.to_disable)
        GuiHandler.remove_widget(self.quit)

    def update_in_db(self):
        institute = self.chosen_institute.get()
        employee_type = self.chosen_type.get()
        month = self.chosen_month.get()
        year = self.entry_year.get()

        if BaseTemplate.data is None or isinstance(BaseTemplate.data, pd.DataFrame):
            return

        if self.sheet is None:
            return

        data = BaseTemplate.data[self.sheet]  # pylint: disable=unsubscriptable-object

        if year_check(year):
            if self.can_start_process() and self.can_start_thread() and messagebox.askyesnocancel(
                "Upload Confirmation",
                "Would you like it upload this data. Any pre-existing data will be updated. Are you sure about this?",
            ):
                self.parallelize(
                    DatabaseWrapper(**self.outer.CRED).fill_table,
                    self.update_thread,
                    process_args={
                        "data": data,
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

        match result:
            case DeleteTable.ERROR:
                messagebox.showwarning("Database Status", DeleteTable.ERROR)
            case DeleteTable.TABLE_NOT_FOUND:
                messagebox.showwarning("Database Status", DeleteTable.TABLE_NOT_FOUND)
            case DeleteTable.SUCCESS:
                messagebox.showinfo("Database Status", DeleteTable.SUCCESS)

        GuiHandler.unlock_gui_button(self.to_disable)
        GuiHandler.remove_widget(self.quit)

    def delete_from_db(self):
        institute = self.chosen_institute.get()
        employee_str = self.chosen_type.get()
        month = self.chosen_month.get()
        year = self.entry_year.get()

        if year_check(year):
            if self.can_start_process() and self.can_start_thread() and messagebox.askyesnocancel(
                "Confirmation",
                f"Month: {month}, Year: {year} \n Institute:{institute}, Type: {employee_str} \n Are you sure you want to clear this data from DB?",
            ):
                self.parallelize(
                    DatabaseWrapper(**self.outer.CRED).delete_table,
                    self.delete_thread,
                    process_args={
                        "queue": self.QUEUE,
                        "institute": institute,
                        "type": employee_str,
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

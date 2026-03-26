from tkinter import messagebox
from typing import Optional
import customtkinter as ctk  # type: ignore
import pandas as pd  # type: ignore
from src.constants import COLOR_SCHEME
from src.pages.template import BaseTemplate, App
from src.utils.common import mapping
from src.utils.databaseWrapper import DatabaseWrapper
from src.utils.guiHandler import GuiHandler
from src.parser import PDF_TEMPLATE


class DataPreview(BaseTemplate):
    """Previews data in database"""

    entry_year = ctk.StringVar(value="2024")
    entry_month = ctk.StringVar(value="Jan")
    entry_institute = ctk.StringVar(value="Somaiya")
    entry_type = ctk.StringVar(value="Teaching")
    tables: dict[str, dict[str, dict[str, set[str]]]] = {}

    def __init__(self, outer: App) -> None:
        super().__init__(outer)

        ctk.CTkLabel(
            master=self.frame,
            text="Data Preview",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 25, "bold"),
            width=250,
        ).pack(pady=20, padx=10)

        frame = ctk.CTkFrame(master=self.frame, fg_color=COLOR_SCHEME["fg_color"])
        ctk.CTkLabel(
            master=frame,
            text="Institute:",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
        ).pack(padx=10, pady=10, side="left")
        self.entry_instituteList = ctk.CTkOptionMenu(
            master=frame,
            variable=self.entry_institute,
            values=[],
            command=self.changeInstitute,
            button_color=COLOR_SCHEME["button_color"],
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=200,
        )
        self.entry_instituteList.pack(padx=10, pady=10, side="left")
        frame.pack()

        frame = ctk.CTkFrame(master=self.frame, fg_color=COLOR_SCHEME["fg_color"])
        ctk.CTkLabel(
            master=frame,
            text="Type:",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
        ).pack(padx=10, pady=10, side="left")
        self.entry_typeList = ctk.CTkOptionMenu(
            master=frame,
            variable=self.entry_type,
            values=[],
            command=self.changeType,
            button_color=COLOR_SCHEME["button_color"],
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=200,
        )
        self.entry_typeList.pack(padx=10, pady=10, side="left")
        frame.pack()

        frame = ctk.CTkFrame(master=self.frame, fg_color=COLOR_SCHEME["fg_color"])
        ctk.CTkLabel(
            master=frame,
            text="Year:",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
        ).pack(padx=10, pady=10, side="left")
        self.entry_yearList = ctk.CTkOptionMenu(
            master=frame,
            variable=self.entry_year,
            values=[],
            command=self.changeYear,
            button_color=COLOR_SCHEME["button_color"],
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=200,
        )
        self.entry_yearList.pack(padx=10, pady=10, side="left")
        frame.pack()

        frame = ctk.CTkFrame(master=self.frame, fg_color=COLOR_SCHEME["fg_color"])
        ctk.CTkLabel(
            master=frame,
            text="Month:",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
        ).pack(padx=10, pady=10, side="left")
        self.entry_monthList = ctk.CTkOptionMenu(
            master=frame,
            variable=self.entry_month,
            values=[],
            button_color=COLOR_SCHEME["button_color"],
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=200,
        )
        self.entry_monthList.pack(padx=10, pady=10, side="left")
        frame.pack()

        self.fetch_data = ctk.CTkButton(
            master=self.frame,
            text="Continue",
            command=self.getData,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.fetch_data.pack(pady=10, padx=10)

        self.back = ctk.CTkButton(
            master=self.frame,
            text="Back",
            command=self.back_to_interface,
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

    def back_to_interface(self) -> None:
        """Moves back to the earlier page"""

        from src.pages.screens import Interface

        self.tables = {}
        self.switch_screen(Interface)

    def changeData(self):
        """Initialization of the optionmenus"""
        curr_institute = list(self.tables.keys())
        curr_type = list(self.tables[curr_institute[0]].keys())
        curr_year = list(self.tables[curr_institute[0]][curr_type[0]].keys())
        curr_month = sorted(
            list(self.tables[curr_institute[0]][curr_type[0]][curr_year[0]]),
            key=lambda x: self.outer.MONTH[x],
        )
        GuiHandler.setOptions(curr_type, self.entry_typeList, self.entry_type)
        GuiHandler.setOptions(
            curr_institute, self.entry_instituteList, self.entry_institute
        )
        GuiHandler.setOptions(curr_year, self.entry_yearList, self.entry_year)
        GuiHandler.setOptions(curr_month, self.entry_monthList, self.entry_month)

    def changeInstitute(self, *args, **kwargs) -> None:
        """Changes Institute Type"""
        curr_institute = self.entry_institute.get()
        curr_type = list(self.tables[curr_institute].keys())
        curr_year = list(self.tables[curr_institute][curr_type[0]].keys())
        curr_month = sorted(
            list(self.tables[curr_institute][curr_type[0]][curr_year[0]]),
            key=lambda x: self.outer.MONTH[x],
        )

        GuiHandler.setOptions(curr_type, self.entry_typeList, self.entry_type)
        GuiHandler.setOptions(curr_year, self.entry_yearList, self.entry_year)
        GuiHandler.setOptions(curr_month, self.entry_monthList, self.entry_month)

    def changeType(self, *args, **kwargs):
        """Changes Type Type"""
        curr_institute = self.entry_institute.get()
        curr_type = self.entry_type.get()
        curr_year = list(self.tables[curr_institute][curr_type].keys())
        curr_month = sorted(
            list(self.tables[curr_institute][curr_type][curr_year[0]]),
            key=lambda x: self.outer.MONTH[x],
        )

        GuiHandler.setOptions(curr_year, self.entry_yearList, self.entry_year)
        GuiHandler.setOptions(curr_month, self.entry_monthList, self.entry_month)

    def changeYear(self, *args, **kwargs) -> None:
        """Changes the year"""
        curr_institute = self.entry_institute.get()
        curr_type = self.entry_type.get()
        curr_year = self.entry_year.get()
        curr_month = sorted(
            list(self.tables[curr_institute][curr_type][curr_year]),
            key=lambda x: self.outer.MONTH[x],
        )

        GuiHandler.setOptions(curr_month, self.entry_monthList, self.entry_month)

    def check_database_thread(self) -> None:
        """Database thread to check database (Might be overkill)"""

        from src.pages.screens import DataView

        GuiHandler.lock_gui_button(self.to_disable)
        GuiHandler.place_after(self.fetch_data, self.quit)
        table: Optional[pd.DataFrame] = None

        while True:
            if self.stop_flag:
                break

            if not self.QUEUE.empty():
                table = self.QUEUE.get()
                self.clear_queue()
                break

        view: DataView = self.outer.Screens[DataView.__name__]  # type: ignore

        if table is not None:
            GuiHandler.view_excel(
                table,
                view.text_excel,
            )
            unique_col = mapping(table.columns, "HR EMP CODE")

            jsons = PDF_TEMPLATE.check_json()
            htmls = PDF_TEMPLATE.check_html()

            if htmls and jsons:
                GuiHandler.setOptions(
                    jsons,
                    view.json_list,
                    view.json,
                )
                GuiHandler.setOptions(
                    htmls,
                    view.html_list,
                    view.html,
                )

                if unique_col is not None:
                    BaseTemplate.data = table
                    view.id_column = unique_col
                    self.switch_screen(DataView)
                    messagebox.showinfo("Fetch Status", "Data Fetched Successfully")
                else:
                    messagebox.showinfo(
                        "Fetch Status", "Data does not have HR EMP Code Column in table"
                    )
            else:
                messagebox.showerror(
                    "Fetch Status", "Template HTML/Mapping JSON files were not found!"
                )

        else:
            messagebox.showinfo("Fetch Status", "Data Does not exists")

        GuiHandler.unlock_gui_button(self.to_disable)
        GuiHandler.remove_widget(self.quit)

    def cancel_thread_wrapper(self) -> None:
        self.cancel_thread()

        GuiHandler.unlock_gui_button(self.to_disable)
        GuiHandler.remove_widget(self.quit)
        messagebox.showinfo("Fetch Status", "Data Fetching Stopped")

    # fetches data from the chosen table
    def getData(self) -> None:

        from src.pages.screens import DataView

        curr_institute = self.entry_institute.get()
        curr_type = self.entry_type.get()
        curr_year = self.entry_year.get()
        curr_month = self.entry_month.get()

        view: DataView = self.outer.Screens[DataView.__name__]  # type: ignore

        view.chosen_month = curr_month
        view.chosen_year = curr_year
        view.chosen_type = curr_type
        view.chosen_institute = curr_institute
        view.changeHeading()

        if self.can_start_thread() and self.can_start_process():
            self.parallelize(
                DatabaseWrapper(**self.outer.CRED).get_data,
                self.check_database_thread,
                process_args={
                    "queue": self.QUEUE,
                    "institute": curr_institute,
                    "type": curr_type,
                    "year": curr_year,
                    "month": curr_month,
                },
            )

        else:
            messagebox.showerror(
                "Processing Error",
                "Cannot fetch data from Database now. Please try again",
            )

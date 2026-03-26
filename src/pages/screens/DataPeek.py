from tkinter import messagebox
import customtkinter as ctk  # type: ignore
from src.constants import COLOR_SCHEME
from src.pages.template import BaseTemplate, App
from src.utils.databaseWrapper import DatabaseWrapper
from src.utils.guiHandler import GuiHandler


class DataPeek(BaseTemplate):
    """Previews data in database"""

    entry_year = ctk.StringVar(value="2024")
    entry_month = ctk.StringVar(value="Jan")
    entry_institute = ctk.StringVar(value="Somaiya")
    entry_type = ctk.StringVar(value="Teaching")
    tables: dict[str, dict[str, dict[str, set[str]]]] = {}

    def __init__(self, outer: App) -> None:
        super().__init__(outer)
        self.outer = outer
        master = self.outer.APP
        self.frame = ctk.CTkScrollableFrame(
            master=master,
            fg_color=COLOR_SCHEME["fg_color"],
        )

        ctk.CTkLabel(
            master=self.frame,
            text="Select Record to Remove",
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

        self.entry_institute_list = ctk.CTkOptionMenu(
            master=frame,
            variable=self.entry_institute,
            values=[],
            command=self.changeInstitute,
            button_color=COLOR_SCHEME["button_color"],
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=200,
        )
        self.entry_institute_list.pack(padx=10, pady=10, side="left")
        frame.pack()

        frame = ctk.CTkFrame(master=self.frame, fg_color=COLOR_SCHEME["fg_color"])
        ctk.CTkLabel(
            master=frame,
            text="Type:",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
        ).pack(padx=10, pady=10, side="left")

        self.entry_type_list = ctk.CTkOptionMenu(
            master=frame,
            variable=self.entry_type,
            values=[],
            command=self.change_type,
            button_color=COLOR_SCHEME["button_color"],
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=200,
        )
        self.entry_type_list.pack(padx=10, pady=10, side="left")
        frame.pack()

        frame = ctk.CTkFrame(master=self.frame, fg_color=COLOR_SCHEME["fg_color"])
        ctk.CTkLabel(
            master=frame,
            text="Year:",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
        ).pack(padx=10, pady=10, side="left")

        self.entry_year_list = ctk.CTkOptionMenu(
            master=frame,
            variable=self.entry_year,
            values=[],
            command=self.change_year,
            button_color=COLOR_SCHEME["button_color"],
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=200,
        )
        self.entry_year_list.pack(padx=10, pady=10, side="left")
        frame.pack()

        frame = ctk.CTkFrame(master=self.frame, fg_color=COLOR_SCHEME["fg_color"])
        ctk.CTkLabel(
            master=frame,
            text="Month:",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
        ).pack(padx=10, pady=10, side="left")

        self.entry_month_list = ctk.CTkOptionMenu(
            master=frame,
            variable=self.entry_month,
            values=[],
            button_color=COLOR_SCHEME["button_color"],
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=200,
        )
        self.entry_month_list.pack(padx=10, pady=10, side="left")
        frame.pack()

        self.fetch_data = ctk.CTkButton(
            master=self.frame,
            text="Continue",
            command=self.go_to_delete,
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

    def change_data(self):
        """Initialization of the option menu"""
        curr_institute = list(self.tables.keys())
        curr_type = list(self.tables[curr_institute[0]].keys())
        curr_year = list(self.tables[curr_institute[0]][curr_type[0]].keys())
        curr_month = sorted(
            list(self.tables[curr_institute[0]][curr_type[0]][curr_year[0]]),
            key=lambda x: self.outer.MONTH[x],
        )

        GuiHandler.setOptions(curr_type, self.entry_type_list, self.entry_type)
        GuiHandler.setOptions(
            curr_institute, self.entry_institute_list, self.entry_institute
        )
        GuiHandler.setOptions(curr_year, self.entry_year_list, self.entry_year)
        GuiHandler.setOptions(curr_month, self.entry_month_list, self.entry_month)

    def changeInstitute(self, *args, **kwargs) -> None:
        """Changes Institute Type"""
        curr_institute = self.entry_institute.get()
        curr_type = list(self.tables[curr_institute].keys())
        curr_year = list(self.tables[curr_institute][curr_type[0]].keys())
        curr_month = sorted(
            list(self.tables[curr_institute][curr_type[0]][curr_year[0]]),
            key=lambda x: self.outer.MONTH[x],
        )

        GuiHandler.setOptions(curr_type, self.entry_type_list, self.entry_type)
        GuiHandler.setOptions(curr_year, self.entry_year_list, self.entry_year)
        GuiHandler.setOptions(curr_month, self.entry_month_list, self.entry_month)

    def change_type(self, *args, **kwargs):
        """Changes Type Type"""
        curr_institute = self.entry_institute.get()
        curr_type = self.entry_type.get()
        curr_year = list(self.tables[curr_institute][curr_type].keys())
        curr_month = sorted(
            list(self.tables[curr_institute][curr_type][curr_year[0]]),
            key=lambda x: self.outer.MONTH[x],
        )

        GuiHandler.setOptions(curr_year, self.entry_year_list, self.entry_year)
        GuiHandler.setOptions(curr_month, self.entry_month_list, self.entry_month)

    def change_year(self, *args, **kwargs) -> None:
        """Changes the year"""
        curr_institute = self.entry_institute.get()
        curr_type = self.entry_type.get()
        curr_year = self.entry_year.get()
        curr_month = sorted(
            list(self.tables[curr_institute][curr_type][curr_year]),
            key=lambda x: self.outer.MONTH[x],
        )

        GuiHandler.setOptions(curr_month, self.entry_month_list, self.entry_month)

    def cancel_thread_wrapper(self) -> None:
        """Cancel Thread"""
        self.cancel_thread()

        GuiHandler.unlock_gui_button(self.to_disable)
        GuiHandler.remove_widget(self.quit)
        messagebox.showinfo("Fetch Status", "Data Fetching Stopped")

    def go_to_delete(self) -> None:
        """fetches data from the chosen table"""

        from src.pages.screens import DeleteView

        curr_institute = self.entry_institute.get()
        curr_type = self.entry_type.get()
        curr_year = self.entry_year.get()
        curr_month = self.entry_month.get()

        view: DeleteView = self.outer.Screens[DeleteView.__name__]  # type: ignore

        view.chosen_month = curr_month
        view.chosen_year = curr_year
        view.chosen_type = curr_type
        view.chosen_institute = curr_institute
        view.changeHeading()

        self.switch_screen(DeleteView)

    def preview(self) -> None:
        """Preview Data"""
        if not self.can_start_thread():
            messagebox.showerror(
                "Program Status", "Warning Background Process/Thread is still running"
            )

        self.parallelize(
            DatabaseWrapper(**self.outer.CRED).check_table,
            self.check_database_thread,
            process_args={"queue": self.QUEUE},
        )

    def check_database_thread(self):
        from src.pages.screens import Interface

        GuiHandler.lock_gui_button(self.to_disable)
        GuiHandler.place_after(self.fetch_data, self.quit)
        table = {}

        while True:
            if self.stop_flag:
                break

            if not self.QUEUE.empty():
                table = self.QUEUE.get()
                self.clear_queue()
                break

        GuiHandler.unlock_gui_button(self.to_disable)
        GuiHandler.remove_widget(self.quit)

        if table:
            self.tables = table
            self.change_data()
        else:
            messagebox.showerror("SQLITE Error", "No Data Available to delete")
            self.switch_screen(Interface)

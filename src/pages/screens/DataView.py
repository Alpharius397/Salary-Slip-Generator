from tkinter import Scrollbar, filedialog, scrolledtext, messagebox
from typing import Optional
from pathlib import Path
import os
import tkinter as tk  # type: ignore
import customtkinter as ctk  # type: ignore
import pyperclip  # type: ignore
import pandas as pd
from src.constants import APP_PATH, COLOR_SCHEME, MAX_TEXT_SIZE, MIN_TEXT_SIZE
from src.dataTypes import NullStr
from src.logger import ERROR_LOG
from src.pages.template import BaseTemplate, App
from src.utils.common import text_clean
from src.utils.guiHandler import GuiHandler
from src.parser import PDF_TEMPLATE
from src.utils.pandasWrapper import PandaWrapper


class DataView(BaseTemplate):
    chosen_month = "None"
    chosen_year = "None"
    chosen_type = "None"
    chosen_institute = "None"
    size: int = 12
    id_column: NullStr = None
    html = ctk.StringVar(value="index.html")
    json = ctk.StringVar(value="index.json")

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
            text=f"Data View for {self.chosen_institute.capitalize()} {self.chosen_type.capitalize()} {self.chosen_month.capitalize()}/{self.chosen_year.upper()}",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 25, "bold"),
            width=250,
        )
        self.label_date.pack(pady=20, padx=10)

        frame = ctk.CTkFrame(master=self.frame, fg_color=COLOR_SCHEME["fg_color"])
        ctk.CTkLabel(
            master=frame,
            text="Enter Employee ID:",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
        ).pack(padx=10, pady=10, side="left")
        self.entry_id = ctk.CTkEntry(
            master=frame,
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.entry_id.pack(padx=10, pady=10, side="left")
        frame.pack()

        self.clipboard = ctk.CTkButton(
            master=self.frame,
            text="Copy Row to Clipboard",
            command=self.copy_row_to_clipboard,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.clipboard.pack(pady=10)

        ctk.CTkLabel(
            master=self.frame,
            text="Choose Template HTML and Mapping JSON: ",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
            width=50,
        ).pack(padx=10)

        frame = ctk.CTkFrame(master=self.frame, fg_color=COLOR_SCHEME["fg_color"])
        ctk.CTkLabel(
            master=frame,
            text="Template HTML:",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
        ).pack(padx=10, pady=10, side="left")
        self.html_list = ctk.CTkOptionMenu(
            master=frame,
            variable=self.html,
            values=[],
            button_color=COLOR_SCHEME["button_color"],
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=200,
        )
        self.html_list.pack(padx=10, pady=10, side="left")
        frame.pack()

        frame = ctk.CTkFrame(master=self.frame, fg_color=COLOR_SCHEME["fg_color"])
        ctk.CTkLabel(
            master=frame,
            text="Mapping JSON:",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
        ).pack(padx=10, pady=10, side="left")
        self.json_list = ctk.CTkOptionMenu(
            master=frame,
            variable=self.json,
            values=[],
            button_color=COLOR_SCHEME["button_color"],
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=200,
        )
        self.json_list.pack(padx=10, pady=10, side="left")
        frame.pack()

        self.single_print = ctk.CTkButton(
            master=self.frame,
            text="Generate Single PDF",
            command=self.single_print_pdf_cover,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.single_print.pack(pady=10)

        self.bulk_print = ctk.CTkButton(
            master=self.frame,
            text="Bulk Print PDFs",
            command=self.bulk_print_pdfs_cover,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.bulk_print.pack(pady=10)

        self.back = ctk.CTkButton(
            master=self.frame,
            text="Back",
            command=self.back_to_preview,
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

        self.minus = ctk.CTkButton(
            master=frame,
            text="-",
            command=self.decrease_size,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=50,
            state="disabled",
        )
        self.minus.pack(side="left", padx=10)

        self.row = ctk.CTkLabel(
            master=frame,
            text=f"{self.size}",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
            width=100,
        )
        self.row.pack(side="left", padx=10)

        self.plus = ctk.CTkButton(
            master=frame,
            text="+",
            command=self.increase_size,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=50,
        )
        self.plus.pack(side="left", padx=10)

        frame.pack()

        self.text_excel = scrolledtext.ScrolledText(
            master=self.frame,
            width=90,
            height=25,
            bg="black",
            fg="white",
            wrap=tk.NONE,
            font=("Courier", 12),
        )
        x_scrollbar = Scrollbar(
            self.frame, orient="horizontal", command=self.text_excel.xview
        )
        self.text_excel.pack(pady=10, padx=10, fill="both", expand=True)
        x_scrollbar.pack(side="bottom", fill="x")

        self.text_excel.configure(xscrollcommand=x_scrollbar.set)
        self.quit = ctk.CTkButton(
            master=self.frame,
            text="Quit the Process",
            command=self.stop_pdf_thread,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.to_disable = list(self.get_widgets_to_disable())

    # back to interface
    def changeHeading(self):
        GuiHandler.changeText(
            self.label_date,
            f"Data View for {self.chosen_institute.capitalize()} {self.chosen_type.capitalize()} {self.chosen_month.capitalize()}/{self.chosen_year}",
        )

    def back_to_preview(self) -> None:
        from src.pages.screens import DataPreview

        self.clear_data()
        self.clear_queue()
        GuiHandler.clear_excel(self.text_excel)
        self.switch_screen(DataPreview)

    def decrease_size(self) -> None:
        self.row.configure(text=max(MIN_TEXT_SIZE, self.size - 1))
        self.size = max(MIN_TEXT_SIZE, self.size - 1)

        GuiHandler.change_text_font(self.text_excel, self.size)
        GuiHandler.unlock_gui_button([self.plus])
        if self.size == MIN_TEXT_SIZE:
            GuiHandler.lock_gui_button([self.minus])

    def increase_size(self) -> None:
        self.row.configure(text=min(MAX_TEXT_SIZE, self.size + 1))
        self.size = min(MAX_TEXT_SIZE, self.size + 1)

        GuiHandler.change_text_font(self.text_excel, self.size)
        GuiHandler.unlock_gui_button([self.minus])
        if self.size == MAX_TEXT_SIZE:
            GuiHandler.lock_gui_button([self.plus])

    def copy_to_clipboard_thread(self, emp_id: str) -> None:
        GuiHandler.lock_gui_button(self.to_disable)
        GuiHandler.place_after(self.clipboard, self.quit)

        if BaseTemplate.data is None:
            messagebox.showwarning("Data Error", "Data was not found")
            return

        if not isinstance(BaseTemplate.data, pd.DataFrame):
            messagebox.showwarning("Data Error", "Data was not found")
            return

        search_result = BaseTemplate.data[  # pylint: disable=unsubscriptable-object
            BaseTemplate.data[  # pylint: disable=unsubscriptable-object
                str(self.id_column)
            ]
            == emp_id
        ]

        if not search_result.empty:
            pyperclip.copy(
                ",".join(map(text_clean, search_result.iloc[[0]].to_numpy()))
            )
            messagebox.showinfo(
                "ClipBoard Status", "Employee data copied to clipboard."
            )
        else:
            messagebox.showwarning("Error", "Employee ID was not found.")

        GuiHandler.unlock_gui_button(self.to_disable)
        GuiHandler.remove_widget(self.quit)

    def copy_row_to_clipboard(self) -> None:
        emp_id = text_clean(self.entry_id.get())

        if emp_id:
            if self.can_start_thread():
                self.parallelize_thread(
                    self.copy_to_clipboard_thread,
                    {"emp_id": emp_id},
                )

            else:
                messagebox.showerror(
                    "Program Status", "Warning Background Thread is still running"
                )
        else:
            messagebox.showerror("Empty Data", "Empty Search String Detected")

    def single_pdf_thread(self) -> None:
        GuiHandler.lock_gui_button(self.to_disable)
        GuiHandler.place_after(self.single_print, self.quit)
        status: bool | NullStr = None
        msg: NullStr = None

        while True:
            if self.stop_flag:
                break

            if not self.QUEUE.empty():
                curr = self.QUEUE.get()

                if isinstance(curr, tuple) and len(curr) == 2:
                    status, msg = curr

                self.clear_queue()
                break

        if status and msg:
            messagebox.showinfo("Single PDF Status", msg)
        elif msg:
            messagebox.showwarning("Single PDF Status", msg)
        else:
            messagebox.showwarning(
                "Single PDF Status", "Something went wrong. Please try again"
            )

        GuiHandler.unlock_gui_button(self.to_disable)
        GuiHandler.remove_widget(self.quit)

    def stop_pdf_thread(self):
        self.cancel_thread()
        GuiHandler.unlock_gui_button(self.to_disable)
        GuiHandler.remove_widget(self.quit)

        messagebox.showinfo("Process Status", "PDF Generation Cancelled")

    # cover for extract_data
    def single_print_pdf_cover(self) -> None:
        month = self.chosen_month
        year = self.chosen_year
        emp_id = text_clean(self.entry_id.get())
        json = self.json.get()
        html = self.html.get()

        if not emp_id:
            messagebox.showerror("Empty Data", "Empty Search String Detected")
            return

        if BaseTemplate.data is None:
            messagebox.showerror("Data Error", "Data is Unavailable")
            return

        file: NullStr = None

        try:
            _file = filedialog.asksaveasfile(
                initialfile=f"employee_{emp_id}",
                defaultextension=".pdf",
                initialdir=APP_PATH,
                filetypes=[("PDF File", "*.pdf")],
            )

            if _file is not None:
                file = _file.name
                _file.close()

        except Exception as e:
            ERROR_LOG.write_error(ERROR_LOG.get_error_info(e))
            messagebox.showwarning("Error", f"Some error has occurred: {e}")
            file = None

        if not isinstance(BaseTemplate.data, pd.DataFrame):
            return

        if file:
            os.remove(file)
            if self.can_start_thread() and self.can_start_process():
                PDF_TEMPLATE.chosen_json = Path(json)
                PDF_TEMPLATE.chosen_html = Path(html)
                self.parallelize(
                    PandaWrapper(
                        BaseTemplate.data,
                        str(self.id_column),
                        PDF_TEMPLATE,
                    ).litany_of_scroll,
                    self.single_pdf_thread,
                    process_args={
                        "queue": self.QUEUE,
                        "data_slate_path": Path(file),
                        "month": month,
                        "year": year,
                        "emp_id": emp_id,
                    },
                )

            else:
                messagebox.showerror(
                    "Program Status",
                    "Warning Background Process/Thread is still running",
                )

        else:
            messagebox.showerror("File Error", "File was not found")

    def bulk_print_pdfs_thread(self) -> None:
        GuiHandler.lock_gui_button(self.to_disable)
        GuiHandler.place_after(self.bulk_print, self.quit)
        done: int = 0
        total: int = 0

        while True:
            if self.stop_flag:
                break

            if not self.QUEUE.empty():
                hot = self.QUEUE.get()

                if isinstance(hot, tuple) and len(hot) == 2:
                    done, total = hot

                self.clear_queue()
                break

        if (not self.stop_flag) and total:
            messagebox.showinfo(
                "Bulk PDF Status", f"Generated {done} PDFs out of {total} records"
            )
        elif not self.stop_flag:
            messagebox.showwarning("Bulk PDF Status", "No PDFs were generated")

        GuiHandler.unlock_gui_button(self.to_disable)
        GuiHandler.remove_widget(self.quit)

    def bulk_print_pdfs_cover(self) -> None:
        month = self.chosen_month
        year = self.chosen_year
        institute = self.chosen_institute
        employee_type = self.chosen_type
        json = self.json.get()
        html = self.html.get()
        where: Optional[Path] = None

        try:
            where = APP_PATH

            where = where.joinpath("pdfs", institute, employee_type, year, month)
            os.makedirs(where.resolve(), exist_ok=True)

        except OSError as e:
            ERROR_LOG.write_error(ERROR_LOG.get_error_info(e))

        if where is None:
            messagebox.showerror("Program Status", "File path was invalid")
            return

        if not isinstance(BaseTemplate.data, pd.DataFrame):
            return 
        
        if self.can_start_thread() and self.can_start_process():
            PDF_TEMPLATE.chosen_html = Path(html)
            PDF_TEMPLATE.chosen_json = Path(json)

            self.parallelize(
                PandaWrapper(
                    BaseTemplate.data, 
                    str(self.id_column),
                    PDF_TEMPLATE,
                ).litany_of_scrolls,
                self.bulk_print_pdfs_thread,
                process_args={
                    "queue": self.QUEUE,
                    "dropzone": where,
                    "month": month,
                    "year": year,
                },
            )

        else:
            messagebox.showerror(
                "Program Status", "Warning Background Process/Thread is still running"
            )

from tkinter import Scrollbar, filedialog, scrolledtext, messagebox
from typing import Optional
from pathlib import Path
import tkinter as tk
import customtkinter as ctk  # type: ignore
import pandas as pd  # type: ignore
from src.constants import (
    APP_PATH,
    COLOR_SCHEME,
    MAX_TEXT_SIZE,
    MIN_TEXT_SIZE,
    TEMPLATE_COLUMN,
    TEMPLATE_SHEET,
)
from src.pages.template import BaseTemplate, App
from src.utils.guiHandler import GuiHandler
from src.utils.common import checkColumns, file_clean
from src.utils.decryption import Decryption
from src.utils.templateGenerator import TemplateGenerator


class TemplateInput(BaseTemplate):
    sheet = ctk.StringVar(value="Sheet1")
    row_index: int = 0
    size: int = 12
    max_row: int = 0
    encryption: bool = False
    prev_password: str = ""

    def __init__(self, outer: App):
        super().__init__(outer)

        # title
        ctk.CTkLabel(
            master=self.frame,
            text="Template Generator",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 25, "bold"),
            width=250,
        ).pack(pady=20, padx=10)

        # file path input
        frame = ctk.CTkFrame(master=self.frame, fg_color=COLOR_SCHEME["fg_color"])
        ctk.CTkLabel(
            master=frame,
            text="Select Excel File:",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
        ).pack(padx=10, pady=10, side="left")
        self.file = ctk.CTkEntry(
            master=frame,
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.file.pack(padx=10, pady=10, side="left")
        frame.pack()

        # browse button
        self.browse_button = ctk.CTkButton(
            master=self.frame,
            text="Browse",
            command=self.select_file,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.browse_button.pack(pady=10)

        self.upload_button = ctk.CTkButton(
            master=self.frame,
            text="Upload",
            command=self.load_decrypted_file,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.back = ctk.CTkButton(
            master=self.frame,
            text="Back",
            command=self.back_to_interface,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.back.pack(pady=10, padx=10)

        # password frame
        self.password_frame = ctk.CTkFrame(
            master=self.frame, fg_color=COLOR_SCHEME["fg_color"]
        )
        ctk.CTkLabel(
            master=self.password_frame,
            text="Enter Password for File:",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
        ).pack(padx=10, pady=10, side="left")
        self.password_box = ctk.CTkEntry(
            master=self.password_frame,
            show="*",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.password_box.pack(padx=10, pady=10, side="left")

        self.variable_frame = ctk.CTkFrame(
            master=self.frame, fg_color=COLOR_SCHEME["fg_color"]
        )
        """ frames are added after file is uploaded """

        frame = ctk.CTkFrame(
            master=self.variable_frame, fg_color=COLOR_SCHEME["fg_color"]
        )
        ctk.CTkLabel(
            master=frame,
            text="Sheet Present:",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
        ).pack(padx=10, pady=10, side="left")
        self.sheetList = ctk.CTkOptionMenu(
            master=frame,
            variable=self.sheet,
            values=[],
            command=self.changeView,
            button_color=COLOR_SCHEME["button_color"],
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=200,
        )
        self.sheetList.pack(side="left", pady=10, padx=10)
        frame.pack(pady=10, padx=10)

        ctk.CTkLabel(
            master=self.variable_frame,
            text="Row Change:",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        ).pack(pady=10, padx=10)

        frame = ctk.CTkFrame(
            master=self.variable_frame, fg_color=COLOR_SCHEME["fg_color"]
        )
        self.row_minus = ctk.CTkButton(
            master=frame,
            text="-",
            command=self.prev_row,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=50,
        )
        self.row_minus.pack(side="left", padx=10)
        self.row = ctk.CTkLabel(
            master=frame,
            text=f"{self.row_index}",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
            width=150,
        )
        self.row.pack(side="left", padx=10)
        self.row_plus = ctk.CTkButton(
            master=frame,
            text="+",
            command=self.next_row,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=50,
        )
        self.row_plus.pack(side="left", padx=10)
        frame.pack(pady=10, padx=10)

        frame = ctk.CTkFrame(
            master=self.variable_frame, fg_color=COLOR_SCHEME["fg_color"]
        )
        ctk.CTkLabel(
            master=frame,
            text="Enter Template Name:",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
        ).pack(side="left", pady=10, padx=10)
        self.template = ctk.CTkEntry(
            master=frame,
            placeholder_text="Eg. Somaiya_Template",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
            width=200,
        )
        self.template.pack(side="left", pady=10, padx=10)
        frame.pack(pady=10, padx=10)

        self.upload = ctk.CTkButton(
            master=self.variable_frame,
            text="Generate Template",
            command=self.generate_template,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.upload.pack(pady=10)
        self.variable_back = ctk.CTkButton(
            master=self.variable_frame,
            text="Back",
            command=self.back_to_interface,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        )
        self.variable_back.pack(pady=10, padx=10)

        ctk.CTkLabel(
            master=self.variable_frame,
            text="Text Size of Sheet:",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        ).pack(pady=10, padx=10)

        frame = ctk.CTkFrame(
            master=self.variable_frame, fg_color=COLOR_SCHEME["fg_color"]
        )

        self.size_minus = ctk.CTkButton(
            master=frame,
            text="-",
            command=self.decrease_size,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=50,
            state="disabled",
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
            master=self.variable_frame,
            width=300,
            height=50,
            bg="black",
            fg="white",
            wrap=tk.NONE,
            font=("Courier", 12),
        )
        x_scrollbar = Scrollbar(
            self.variable_frame, orient="horizontal", command=self.text_excel.xview
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

    def back_to_interface(self):
        from src.pages.screens import Interface

        GuiHandler.clear_excel(self.text_excel)
        self.set_for_file_upload_state()
        self.clear_data()
        self.switch_screen(Interface)

    def generate_template(self):
        """passing data"""

        file_name = self.template.get()

        if not file_name:
            messagebox.showerror("Template Generation", "File Name cannot be empty!")
            return

        if BaseTemplate.data is None:
            messagebox.showerror("Template Generation", "Data is Unavailable")
            return

        if self.can_start_thread() and self.can_start_process():
            self.parallelize(
                TemplateGenerator.make_template,
                self.go_to_generate_template_thread,
                process_args={
                    "file_name": file_clean(file_name),
                    "data": BaseTemplate.data,
                    "queue": self.QUEUE,
                },
            )
        else:
            messagebox.showerror(
                "Program Status", "Warning Background Thread is still running"
            )

    def go_to_generate_template_thread(self) -> None:
        GuiHandler.lock_gui_button(self.to_disable)
        GuiHandler.place_after(self.upload, self.quit)

        status: Optional[bool] = None

        while True:
            if self.stop_flag:
                break

            if not self.QUEUE.empty():
                result = self.QUEUE.get()

                if isinstance(result, tuple):
                    status, error = result

                    if status:
                        messagebox.showinfo(
                            "Salary Slip Template Generation",
                            "Salary Slip Template Generation Successful",
                        )
                    else:
                        messagebox.showinfo(
                            "Salary Slip Template Generation",
                            f"Salary Slip Template Generation Failed! {error}",
                        )

                break

        GuiHandler.unlock_gui_button(self.to_disable)
        GuiHandler.remove_widget(self.quit)

    def cancel_thread_wrapper(self):
        self.cancel_thread()
        GuiHandler.unlock_gui_button(self.to_disable)
        GuiHandler.remove_widget(self.quit)

    def next_row(self):
        if not isinstance(BaseTemplate.data, pd.DataFrame):
            return

        max_row = BaseTemplate.data[  # pylint: disable=unsubscriptable-object
            self.sheet.get()
        ].shape[0]

        self.row_index = min(max_row, self.row_index + 1)

        GuiHandler.changeText(self.row, str(self.row_index))
        if self.row_index == max_row:
            GuiHandler.lock_gui_button([self.row_plus])
        else:
            self.get_data()
            GuiHandler.unlock_gui_button([self.row_minus])

    def prev_row(self):
        self.row_index = max(0, self.row_index - 1)
        GuiHandler.changeText(self.row, str(self.row_index))

        if self.row_index == 0:
            GuiHandler.lock_gui_button([self.row_minus])
        else:
            self.get_data()
            GuiHandler.unlock_gui_button([self.row_plus])

    def get_data(self):
        file_path = self.file.get()
        password = self.prev_password

        if file_path:
            if self.encryption and password:
                if self.can_start_thread() and self.can_start_process():
                    self.parallelize(
                        Decryption.fetch_encrypted_file,
                        self.change_row_thread,
                        process_args={
                            "queue": self.QUEUE,
                            "file_path": Path(file_path),
                            "password": password,
                            "skip": self.row_index,
                        },
                    )

                else:
                    messagebox.showerror(
                        "Program Status",
                        "Warning Background Process/Thread is still running",
                    )

            elif self.encryption:
                messagebox.showinfo(
                    "Encryption Status",
                    f"File '{file_path}' is encrypted. Please enter the password",
                )

            elif not self.encryption:
                if self.can_start_thread() and self.can_start_process():
                    self.parallelize(
                        Decryption.fetch_decrypted_file,
                        self.change_row_thread,
                        process_args={
                            "queue": self.QUEUE,
                            "file_path": Path(file_path),
                            "skip": self.row_index,
                        },
                    )

                else:
                    messagebox.showerror(
                        "Program Status",
                        "Warning Background Process/Thread is still running",
                    )
        else:
            messagebox.showerror("File Status", "Empty file path was detected")

    def decrease_size(self):
        self.font_size.configure(text=max(MIN_TEXT_SIZE, self.size - 1))
        self.size = max(MIN_TEXT_SIZE, self.size - 1)

        GuiHandler.change_text_font(self.text_excel, self.size)
        GuiHandler.unlock_gui_button([self.size_plus])
        if self.size == MIN_TEXT_SIZE:
            GuiHandler.lock_gui_button([self.size_minus])

    def increase_size(self) -> None:
        self.font_size.configure(text=min(MAX_TEXT_SIZE, self.size + 1))
        self.size = min(MAX_TEXT_SIZE, self.size + 1)

        GuiHandler.change_text_font(self.text_excel, self.size)
        GuiHandler.unlock_gui_button([self.size_minus])
        if self.size == MAX_TEXT_SIZE:
            GuiHandler.lock_gui_button([self.size_plus])

    def encryption_check_thread(self):
        """Locks present GUI and places quit button after browse button"""
        GuiHandler.lock_gui_button(self.to_disable)
        GuiHandler.place_after(self.browse_button, self.quit)

    def set_after_upload_state(self):
        """Places variable frame and removes upload and password frame"""
        GuiHandler.remove_widget(self.upload_button)
        GuiHandler.remove_widget(self.password_frame)
        GuiHandler.place_after(self.browse_button, self.variable_frame)
        GuiHandler.remove_widget(self.back)

    def set_after_file_is_encrypted_state(self):
        """Places password frame before upload button"""
        GuiHandler.place_before(self.upload_button, self.password_frame)

    def set_for_file_upload_state(self):
        """Removes password and variable frame"""
        GuiHandler.remove_widget(self.variable_frame)
        GuiHandler.remove_widget(self.password_frame)
        GuiHandler.remove_widget(self.upload_button)
        GuiHandler.place_after(self.browse_button, self.back)
        GuiHandler.clear_entry(self.file)
        GuiHandler.clear_entry(self.password_box)

    def is_encrypted_thread(self) -> None:
        GuiHandler.lock_gui_button(self.to_disable)
        GuiHandler.place_after(self.browse_button, self.quit)
        self.set_for_file_upload_state()
        GuiHandler.changeCommand(self.upload_button, self.load_decrypted_file)

        is_encrypted: bool | None = None

        while True:
            if self.stop_flag:
                break

            if not self.QUEUE.empty():
                is_encrypted = self.QUEUE.get()
                self.clear_queue()
                break

        self.encryption = bool(is_encrypted)

        if is_encrypted is not None:
            GuiHandler.place_after(self.browse_button, self.upload_button)

            if is_encrypted:
                self.set_after_file_is_encrypted_state()
                GuiHandler.changeCommand(self.upload_button, self.load_encrypted_file)

                messagebox.showinfo(
                    "Encrypted Status",
                    f"Excel File '{self.file.get()}' is encrypted. Please provide the password",
                )
        else:
            messagebox.showerror(
                "File Status", f"File '{self.file.get()}' was not found"
            )

        GuiHandler.unlock_gui_button(self.to_disable)
        GuiHandler.remove_widget(self.quit)

    def select_file(self) -> None:
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel Files", ".xlsx;.xls")], initialdir=APP_PATH
        )

        if file_path:
            GuiHandler.change_file_holder(self.file, file_path)

            if self.can_start_thread() and self.can_start_process():
                self.parallelize(
                    Decryption.is_encrypted_wrapper,
                    self.is_encrypted_thread,
                    process_args={"queue": self.QUEUE, "file_path": Path(file_path)},
                )

            else:
                messagebox.showerror(
                    "Program Status",
                    "Warning Background Process/Thread is still running",
                )

        else:
            messagebox.showerror("File Status", "Empty file_path was detected")

    def load_unprotected_data_thread(self) -> None:
        GuiHandler.lock_gui_button(self.to_disable)
        GuiHandler.place_after(self.upload_button, self.quit)
        self.set_for_file_upload_state()

        try:
            sheets: list[str] = []
            data: Optional[dict[str, pd.DataFrame]] = None

            while True:
                if self.stop_flag:
                    break

                if not self.QUEUE.empty():
                    sheets, data = self.QUEUE.get()
                    self.clear_queue()
                    break

            if (sheets) and (data is not None):
                if not checkColumns(sheets, list(TEMPLATE_SHEET)):
                    messagebox.showwarning(
                        "File Status",
                        f"Excel File '{self.file.get()}' requires all the following sheets: {', '.join(TEMPLATE_SHEET)}",
                    )
                    return

                if not all(
                    checkColumns(list(_data.columns), list(TEMPLATE_COLUMN))
                    for _data in data.values()
                ):
                    messagebox.showwarning(
                        "File Status",
                        f"Excel File '{self.file.get()}' requires all the following columns in all sheets: {', '.join(TEMPLATE_COLUMN)}",
                    )
                    return

                BaseTemplate.data = data
                GuiHandler.setOptions(sheets, self.sheetList, self.sheet)
                self.set_after_upload_state()
                if isinstance(BaseTemplate.data, dict):
                    GuiHandler.view_excel(
                        BaseTemplate.data[  # pylint: disable=unsubscriptable-object
                            sheets[0]
                        ],
                        self.text_excel,
                    )

                messagebox.showinfo(
                    "Upload Status", f"Excel File '{self.file.get()}' was loaded"
                )
            else:
                messagebox.showwarning(
                    "File Status",
                    f"Excel File '{self.file.get()}' could not be loaded. Please ensure file",
                )
        finally:
            GuiHandler.unlock_gui_button(self.to_disable)
            GuiHandler.remove_widget(self.quit)

    def load_decrypted_file(self):
        file_path = self.file.get()

        if file_path:
            if self.can_start_thread() and self.can_start_process():
                self.parallelize(
                    Decryption.fetch_decrypted_file,
                    self.load_unprotected_data_thread,
                    process_args={
                        "queue": self.QUEUE,
                        "file_path": Path(file_path),
                        "skip": self.row_index,
                    },
                )

            else:
                messagebox.showerror(
                    "Program Status",
                    "Warning Background Process/Thread is still running",
                )

        else:
            messagebox.showerror("File Status", "Empty file_path was detected")

    def load_protected_data_thread(self) -> None:
        GuiHandler.lock_gui_button(self.to_disable)
        GuiHandler.place_after(self.upload_button, self.quit)

        try:
            sheets: list[str] = []
            data: Optional[dict[str, pd.DataFrame]] = None

            while True:
                if self.stop_flag:
                    return None

                if not self.QUEUE.empty():
                    sheets, data = self.QUEUE.get()
                    self.clear_queue()
                    break

            if (sheets) and (data is not None):
                if not checkColumns(sheets, list(TEMPLATE_SHEET)):
                    messagebox.showwarning(
                        "File Status",
                        f"Excel File '{self.file.get()}' requires all the following sheets: {', '.join(TEMPLATE_SHEET)}",
                    )
                    return

                if not all(
                    checkColumns(list(_data.columns), list(TEMPLATE_COLUMN))
                    for _data in data.values()
                ):
                    messagebox.showwarning(
                        "File Status",
                        f"Excel File '{self.file.get()}' requires all the following columns in all sheets: {', '.join(TEMPLATE_COLUMN)}",
                    )
                    return

                BaseTemplate.data = data
                GuiHandler.setOptions(sheets, self.sheetList, self.sheet)
                self.set_after_upload_state()
                GuiHandler.view_excel(data[sheets[0]], self.text_excel)

                self.prev_password = self.password_box.get()
                messagebox.showinfo(
                    "Upload Status", f"Excel File '{self.file.get()}' was loaded"
                )
            else:
                messagebox.showwarning(
                    "File Status",
                    f"Excel File '{self.file.get()}' could not be loaded. Please check the password",
                )

        finally:
            GuiHandler.unlock_gui_button(self.to_disable)
            GuiHandler.remove_widget(self.quit)

    def load_encrypted_file(self):
        file_path = self.file.get()
        password = self.password_box.get()

        if file_path:
            if self.encryption and (not password):
                messagebox.showinfo(
                    "Encryption Status",
                    f"File '{file_path}' is encrypted. Please enter the password",
                )
                return None

            if self.can_start_thread() and self.can_start_process():
                self.parallelize(
                    Decryption.fetch_encrypted_file,
                    self.load_protected_data_thread,
                    process_args={
                        "queue": self.QUEUE,
                        "file_path": Path(file_path),
                        "password": password,
                        "skip": self.row_index,
                    },
                )

            else:
                messagebox.showerror(
                    "Program Status",
                    "Warning Background Process/Thread is still running",
                )

        else:
            messagebox.showerror("File Status", "Empty file_path was detected")

    def change_view_thread(self):
        GuiHandler.lock_gui_button(self.to_disable)
        current_sheet = self.sheet.get()

        if isinstance(BaseTemplate.data, dict):
            current_data = BaseTemplate.data[  # pylint: disable=unsubscriptable-object
                current_sheet
            ]
            GuiHandler.view_excel(current_data, self.text_excel)
        GuiHandler.unlock_gui_button(self.to_disable)

    def change_row_thread(self) -> None:
        GuiHandler.lock_gui_button(self.to_disable)
        GuiHandler.place_before(self.text_excel, self.quit)  # type: ignore
        current_sheet = self.sheet.get()
        data: Optional[dict[str, pd.DataFrame]] = None

        while True:
            if self.stop_flag:
                break

            if not self.QUEUE.empty():
                _, data = self.QUEUE.get()
                self.clear_queue()
                break

        if (current_sheet is not None) and (data is not None):
            BaseTemplate.data = data
            self.set_after_upload_state()
            GuiHandler.view_excel(data[current_sheet], self.text_excel)
            self.prev_password = self.password_box.get()
        else:
            messagebox.showwarning(
                "File Status",
                f"Excel File '{self.file.get()}' could not be loaded. Please check the password",
            )

        if isinstance(BaseTemplate.data, dict):
            GuiHandler.view_excel(
                BaseTemplate.data[  # pylint: disable=unsubscriptable-object
                    self.sheet.get()
                ],
                self.text_excel,
            )
        GuiHandler.unlock_gui_button(self.to_disable)
        GuiHandler.remove_widget(self.quit)

    def changeView(self, *args, **kwargs):
        sheet = self.sheet.get()

        if sheet:
            if self.can_start_thread():
                self.parallelize_thread(self.change_view_thread)
            else:
                messagebox.showerror(
                    "Program Status", "Warning Background Thread is still running"
                )

        else:
            messagebox.showerror("File Status", "Empty file_path was detected")

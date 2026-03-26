from tkinter import scrolledtext
import tkinter as tk
from typing import Any, Callable, Iterator
import pandas as pd  # type: ignore
import customtkinter as ctk  # type: ignore
from src.utils.common import text_clean


class GuiHandler:
    """Handles GUI"""

    @staticmethod
    def view_excel(data: pd.DataFrame, text_excel: scrolledtext.ScrolledText) -> None:
        """Changes the text on the text excel thing"""

        text = [[str(i) for i in data.columns]]
        col_widths = {i: len(str(j)) for i, j in enumerate(data.columns)}

        for row in data.itertuples(index=False):
            row_data = []

            for idx, cell in enumerate(row):
                row_data.append(cell)
                col_widths[idx] = max(col_widths[idx], len(str(cell)))

            text.append(row_data)

        formatted_data = "\n".join(
            [
                " "
                + " | ".join(
                    [
                        f"{text_clean(cell):^{col_widths[i]}}"
                        for i, cell in enumerate(row)
                    ]
                )
                + " "
                for row in text
            ]
        )

        text_excel.delete(1.0, tk.END)
        text_excel.insert(tk.END, formatted_data)

        text_excel.tag_config(
            "highlight", font=("Courier", 12, "bold"), foreground="yellow"
        )
        text_excel.tag_add("highlight", "1.0", "1.end")

    @staticmethod
    def clear_excel(text_excel: scrolledtext.ScrolledText) -> None:
        text_excel.delete(1.0, tk.END)

    @staticmethod
    def change_text_font(text_excel: scrolledtext.ScrolledText, size: int = 15) -> None:
        """Change the size of text"""
        text_excel.configure(font=("Courier", size))

    @staticmethod
    def lock_gui_button(
        buttons: (
            Iterator[ctk.CTkButton | ctk.CTkEntry | ctk.CTkOptionMenu]
            | list[ctk.CTkButton | ctk.CTkEntry | ctk.CTkOptionMenu]
        ),
    ) -> None:
        """Disable buttons"""
        for button in buttons:
            button.configure(state="disabled")

    @staticmethod
    def unlock_gui_button(
        buttons: (
            Iterator[ctk.CTkButton | ctk.CTkEntry | ctk.CTkOptionMenu]
            | list[ctk.CTkButton | ctk.CTkEntry | ctk.CTkOptionMenu]
        ),
    ) -> None:
        """Enable buttons"""
        for button in buttons:
            button.configure(state="normal")

    @staticmethod
    def change_file_holder(file_path_holder: ctk.CTkEntry, new_path: str) -> None:
        """Change the file path holders"""
        file_path_holder.delete(0, tk.END)
        file_path_holder.insert(0, new_path)
        file_path_holder.configure(width=7 * len(new_path))

    @staticmethod
    def place_after(
        anchor: ctk.CTkBaseClass,
        to_place: ctk.CTkBaseClass,
        padx: int = 10,
        pady: int = 10,
    ) -> None:
        """Places widget after the anchor widgets"""
        to_place.pack_configure(after=anchor, padx=padx, pady=pady)

    @staticmethod
    def place_before(
        anchor: ctk.CTkBaseClass,
        to_place: ctk.CTkBaseClass,
        padx: int = 10,
        pady: int = 10,
    ) -> None:
        """Places widget before the anchor widgets"""
        to_place.pack_configure(before=anchor, padx=padx, pady=pady)

    @staticmethod
    def remove_widget(this_widget: ctk.CTkBaseClass) -> None:
        """Remove widget from frame"""
        this_widget.pack_forget()

    @staticmethod
    def setOptions(
        new_values: list[str] | tuple[str, ...],
        optionMenu: ctk.CTkOptionMenu,
        new_variable: ctk.StringVar,
    ):
        """Changes values of optionMenu and  set the corresponding variable to the options"""
        optionMenu.configure(values=new_values)
        new_variable.set(new_values[0])

    @staticmethod
    def changeOptions(options: list[str], OptionList: ctk.CTkOptionMenu) -> None:
        """Updates optionmenu with options"""
        OptionList.configure(values=options)

    @staticmethod
    def changeCommand(
        widgets: ctk.CTkBaseClass, new_command: Callable[..., Any]
    ) -> None:
        """Changes command of a widget"""
        widgets.configure(command=new_command)

    @staticmethod
    def changeText(widgets: ctk.CTkLabel, text: str) -> None:
        """Changes text of widgets"""
        widgets.configure(text=text)

    @staticmethod
    def place(widget: ctk.CTkBaseClass, padx: int = 10, pady: int = 10) -> None:
        """Places widget after the last widget present on frame"""
        widget.pack(padx=padx, pady=pady)

    @staticmethod
    def clear_entry(widget: ctk.CTkEntry) -> None:
        """Clears entry widget"""
        widget.delete(0, tk.END)

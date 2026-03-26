import customtkinter as ctk  # type: ignore
from src.constants import COLOR_SCHEME
from src.pages.template import BaseTemplate, App


class MailCover(BaseTemplate):
    """Mailing Cover to choose either single-mailing / bulk-mailing"""

    def __init__(self, outer: App):
        super().__init__(outer)

        ctk.CTkLabel(
            master=self.frame,
            text="Mailing Option",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 25, "bold"),
            width=250,
        ).pack(pady=20, padx=10)
        ctk.CTkLabel(
            master=self.frame,
            text="Select mailing option",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        ).pack(pady=10)
        ctk.CTkButton(
            master=self.frame,
            text="Single Mail",
            command=self.single,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        ).pack(pady=10, padx=10)
        ctk.CTkButton(
            master=self.frame,
            text="Bulk Mail",
            command=self.many,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        ).pack(pady=10, padx=10)
        ctk.CTkButton(
            master=self.frame,
            text="Back",
            command=self.back_to_landing,
            fg_color=COLOR_SCHEME["button_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        ).pack(pady=10, padx=10)

    def single(self) -> None:
        """Redirect to Single Mailing"""
        from src.pages.screens import SendMail

        self.switch_screen(SendMail)

    def many(self) -> None:
        """Redirect to Bulk Mailing"""
        from src.pages.screens import SendBulkMail

        self.switch_screen(SendBulkMail)

    def back_to_landing(self) -> None:
        """Returns back to Interface"""
        from src.pages.screens import Interface

        self.clear_data()
        self.clear_queue()
        self.switch_screen(Interface)

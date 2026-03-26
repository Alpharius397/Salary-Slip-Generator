import gc
from multiprocessing import Process, Queue
from threading import Thread
from typing import Optional, Callable, Mapping, Any
from PIL import Image, ImageFile
import pandas as pd  # type: ignore
import customtkinter as ctk  # type: ignore
from src.constants import COLOR_SCHEME, SQLITE_CRED
from src.logger import ERROR_LOG
from src.utils.common import load_file


class BaseTemplate:
    """Base Template for all tkinter frames"""

    process: Optional[Process] = None
    """ All frames will have 1 common process to run big task """

    thread: Optional[Thread] = None
    """ All frames gets 1 common thread to process gui changes """

    QUEUE: Queue = Queue()
    """ A queue for communication between thread and process """

    stop_flag: bool = False
    """ A stop flag for thread to stop """

    data: Optional[pd.DataFrame | dict[str, pd.DataFrame]] = None
    """ A shared data storage """

    def __init__(self, outer: "App") -> None:
        self.outer = outer
        self.visible: bool = False
        self.to_disable: list[ctk.CTkButton | ctk.CTkOptionMenu | ctk.CTkEntry] = []
        self.frame: ctk.CTkScrollableFrame = ctk.CTkScrollableFrame(
            master=self.outer.APP, fg_color=COLOR_SCHEME["fg_color"]
        )

    def switch_screen(self, next_frame: type["BaseTemplate"]):
        self.outer.switch_screen(self.__class__, next_frame)

    def appear(self) -> None:
        """Add frame to the tkinter app"""

        if not self.visible:
            self.outer.start_frame.pack(pady=0)
            self.frame.pack(pady=5, padx=20, fill="both", expand=True)
            self.outer.credit_frame.pack(pady=5, padx=20, fill="both")
            self.outer.end_frame.pack(pady=0)
            self.visible = True

    def hide(self) -> None:
        """Hides the current frame"""

        if self.visible:
            self.frame.pack_forget()
            self.outer.start_frame.pack_forget()
            self.outer.end_frame.pack_forget()
            self.outer.credit_frame.pack_forget()
            self.visible = False

    def cancel_thread(self) -> None:
        """Basic function to cancel/quit out of process and thread (using flags)"""

        if self.thread and self.thread.is_alive():
            BaseTemplate.stop_flag = True

        if BaseTemplate.process and BaseTemplate.process.is_alive():
            BaseTemplate.process.terminate()

        self.clear_queue()

    def can_start_process(self) -> bool:
        """Check if process can begin"""

        can_we_start = bool(
            (self.process is None) or (self.process and (not self.process.is_alive()))
        )

        return can_we_start

    def can_start_thread(self) -> bool:
        """Check if threading can begin"""

        can_we_start = bool(
            (self.thread is None) or (self.thread and (not self.thread.is_alive()))
        )

        if can_we_start:
            BaseTemplate.stop_flag = False

        return can_we_start

    def get_widgets_to_disable(self):
        """Finds widgets to disable"""

        all_attribute = dir(self)

        for attr in all_attribute:
            if "quit" in attr:
                continue

            widget = getattr(self, attr)

            if isinstance(widget, (ctk.CTkButton, ctk.CTkOptionMenu, ctk.CTkEntry)):
                yield widget

    def clear_queue(self):
        """Clear the queue"""
        while not self.QUEUE.empty():
            self.QUEUE.get()

    def clear_data(self, hard=True):
        """Clear Shared Data"""

        if hard:
            BaseTemplate.data = None

        erased = gc.collect()
        ERROR_LOG.write_info(f"{erased} Variables Cleared")

    def parallelize(
        self,
        process_fn: Callable[..., None],
        thread_fn: Callable[..., None],
        /,
        *,
        process_args: Optional[Mapping[str, Any]] = None,
        thread_args: Optional[Mapping[str, Any]] = None,
    ):

        self.parallelize_process(process_fn, process_args)
        self.parallelize_thread(thread_fn, thread_args)

    def parallelize_process(
        self,
        process_fn: Callable[..., None],
        process_args: Optional[Mapping[str, Any]],
    ):
        if not self.can_start_process():
            return

        args = {} if process_args is None else process_args
        self.process = Process(
            target=process_fn,
            kwargs=args,
            daemon=True,
        )
        self.process.start()

    def parallelize_thread(
        self,
        thread_fn: Callable[..., None],
        thread_args: Optional[Mapping[str, Any]] = None,
    ):
        if not self.can_start_thread():
            return

        self.thread = Thread(target=thread_fn, kwargs=thread_args, daemon=True)
        self.thread.start()


class App:
    """Main class representing the application"""

    APP: ctk.CTk = ctk.CTk()
    TOGGLE: dict[str, list[str]] = {
        "Somaiya": ["Teaching", "Non Teaching", "Temporary"],
        "SVV": [
            "svv",
        ],
    }

    CRED = SQLITE_CRED

    img_data: Optional[ImageFile.ImageFile] = None

    MONTH: dict[str, int] = {
        "jan": 1,
        "feb": 2,
        "mar": 3,
        "apr": 4,
        "may": 5,
        "jun": 6,
        "jul": 7,
        "aug": 8,
        "sept": 9,
        "oct": 10,
        "nov": 11,
        "dec": 12,
    }

    credit_frame = ctk.CTkFrame(
        master=APP, height=10, fg_color=COLOR_SCHEME["fg_color"]
    )
    start_frame = ctk.CTkLabel(text="", master=APP, height=10)
    end_frame = ctk.CTkLabel(text="", master=APP, height=10)

    def __init__(self, width: int, height: int, title: str) -> None:
        self.APP.geometry(f"{width}x{height}")
        self.APP.title(title)

        self.Screens: dict[str, "BaseTemplate"] = {}

    def start_app(self, first: type["BaseTemplate"]):
        """To start application run this"""
        self.switch_screen(first, first)
        self.credits()
        self.APP.mainloop()

    def exit_app(self):
        try:
            self.APP.destroy()
        except Exception:
            pass
        finally:
            ERROR_LOG.write_info("User Logged Out")

    def register(self, classObj: type["BaseTemplate"]):
        self.Screens[classObj.__name__] = classObj(self)

    def switch_screen(
        self, current: type["BaseTemplate"], next_frame: type["BaseTemplate"]
    ):
        if current.__name__ in self.Screens:
            self.Screens[current.__name__].hide()

        if next_frame.__name__ in self.Screens:
            self.Screens[next_frame.__name__].appear()

    def credits(self) -> None:
        if self.img_data is None:
            if (img := load_file("images", "kjsit-logo.png")) is not None:
                self.img_data = Image.open(img)

        if self.img_data is not None:
            img = ctk.CTkImage(self.img_data, self.img_data, (243, 65))
            ctk.CTkLabel(
                master=self.credit_frame,
                image=img,
                text="",
                text_color=COLOR_SCHEME["text_color"],
                font=("Ubuntu", 16, "bold"),
                width=250,
            ).pack(pady=5, padx=10, side="left")

        ctk.CTkLabel(
            master=self.credit_frame,
            text="",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        ).pack(pady=5, padx=10, side="right")

        ctk.CTkLabel(
            master=self.credit_frame,
            text="Under Guidance of: Dr. Sarita Ambadekar and Dr. Abhijit Patil",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        ).pack(pady=5, padx=10)

        ctk.CTkLabel(
            master=self.credit_frame,
            text="First developed by: Raj More, Pranav Lohar, Aryan Mandke",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        ).pack(pady=5, padx=10)

        ctk.CTkLabel(
            master=self.credit_frame,
            text="Department of Computer Engineering",
            text_color=COLOR_SCHEME["text_color"],
            font=("Ubuntu", 16, "bold"),
            width=250,
        ).pack(pady=5, padx=10)

from multiprocessing import freeze_support
import sys
import tkinter as tk  # type: ignore
import traceback
import types  # type: ignore
import customtkinter as ctk  # type: ignore
from src.constants import APP_PATH
from src.dataTypes import NullStr
from src.logger import ERROR_LOG
from src.pages.template import App
from src.pages.screens import (
    SendMail,
    SendBulkMail,
    Login,
    Interface,
    DataPreview,
    MailCover,
    FileInput,
    UploadData,
    DataView,
    DataPeek,
    DeleteView,
    TemplateInput,
    TemplateGeneration,
)
from src.utils.common import load_folder

ctk.set_appearance_mode("light")


class TkErrorCatcher:
    """Logging Tkinter Loops errors"""

    def __init__(self, func, subst, widget):
        self.func = func
        self.subst = subst
        self.widget = widget

    def __call__(self, *args):
        try:
            if self.subst:
                args = self.subst(*args)
            return self.func(*args)

        except SystemExit as msg:
            raise msg

        except Exception as e:
            ERROR_LOG.write_error(ERROR_LOG.get_error_info(e))
            raise e


def show_error(
    exctype: type[Exception],
    excvalue: Exception,
    tb: types.TracebackType,
    thread: NullStr = None,
):
    if issubclass(exctype, KeyboardInterrupt):
        sys.__excepthook__(exctype, excvalue, tb)
        return

    err = "{} \n {}".format(
        ERROR_LOG.get_error_info(exctype(excvalue)),
        "\n".join(traceback.format_exception(exctype, excvalue, tb)),
    )  # type: ignore

    if thread is None:
        ERROR_LOG.write_error(err)
    else:
        ERROR_LOG.write_error(err, "APPLICATION:THREAD")


sys.excepthook = show_error  # type: ignore
excepthook = show_error  # type: ignore

if __name__ == "__main__":
    print(APP_PATH)
    # initialize main app
    freeze_support()
    tk.CallWrapper = TkErrorCatcher  # type: ignore
    app = App(500, 500, "Excel-To-Pdf Generator")

    app.register(SendMail)
    app.register(SendBulkMail)
    app.register(Login)
    app.register(Interface)
    app.register(DataView)
    app.register(DataPreview)
    app.register(MailCover)
    app.register(FileInput)
    app.register(UploadData)
    app.register(DataPeek)
    app.register(DeleteView)
    app.register(TemplateInput)
    app.register(TemplateGeneration)

    app.APP.report_callback_exception = show_error  # type: ignore

    load_folder("doc")
    load_folder("json")
    load_folder("html")
    load_folder("excel")

    app.start_app(Login)
    app.exit_app()

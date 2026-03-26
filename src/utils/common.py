import os
import io
from pathlib import Path
import re
import shutil
import sys
from typing import Iterable
from src.constants import APP_PATH, IS_EXE
from src.logger import ERROR_LOG


def email_check(x: str):
    """a helper function for email validation"""
    return re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\Z", x) is not None


def year_check(x: str):
    """a helper function for year validation"""
    return re.match(r"^(\d){4}\Z", x) is not None


def text_clean(x: str):
    """a helper function for text validation"""
    return str(x).replace("\n", " ").strip()


def file_clean(x: str):
    """a helper function for file path validation"""

    def _clean(string: str, not_allowed: str) -> str:
        deny = set(not_allowed)
        new_string: str = "".join([i for i in string if i not in deny])

        return "none" if (not new_string) else new_string

    return _clean(x, """<>:"/\\?*'\n""")


def mapping(pd_columns: Iterable[str], columns: str) -> str | None:
    column = columns.lower()

    for i in sorted(pd_columns, key=len):
        if column in i.lower():
            return i

    return None


def checkColumns(present_col: list[str], needed_col: list[str]) -> bool:
    seen = set()
    for i in present_col:
        if mapping(needed_col, i) is not None:
            seen.add(i)
    return len(needed_col) == len(seen)


def load_folder(folder: str) -> None:
    """Find the bundled folder and recursive copies them outside"""
    root = str(getattr(sys, "_MEIPASS")) if IS_EXE else os.getcwd()

    try:
        exe_path = Path(root).joinpath(folder)
        real_path = APP_PATH.joinpath(folder)

        if exe_path.exists():
            os.makedirs(real_path, exist_ok=True)

            if str(real_path.resolve()) == str(exe_path.resolve()):
                return

            shutil.copytree(exe_path, real_path, dirs_exist_ok=True)

    except (IOError, FileNotFoundError, Exception) as e:
        ERROR_LOG.write_error(ERROR_LOG.get_error_info(e), "DOC")


def load_file(*file: str):
    """Find the bundled file and return io.BytesIO of file data"""
    root = str(getattr(sys, "_MEIPASS")) if IS_EXE else os.getcwd()

    try:
        exe_path = Path(root).joinpath(*file)

        if exe_path.exists():
            with open(exe_path.resolve(), "rb") as f:
                byte = io.BytesIO()
                byte.write(f.read())
                return byte

    except (IOError, FileNotFoundError, Exception) as e:
        ERROR_LOG.write_error(ERROR_LOG.get_error_info(e), "DOC")

    return None

from pathlib import Path
import sys
import os
from src.creds import PROD_CREDS, TEST_CREDS
from src.dataTypes import DB_CRED

IS_EXE = bool(getattr(sys, 'frozen', False)) and hasattr(sys, '_MEIPASS')

IS_DEBUG = True and (not IS_EXE)
""" for testing set to true. Defaults to False in exe """

APP_PATH = Path(sys.executable).parent if (IS_EXE) else Path(os.getcwd())

SQLITE_CRED = DB_CRED(
    db_name="secure", key="do-not-change-this-ever"
)

MAIL_CRED = PROD_CREDS if not IS_DEBUG else TEST_CREDS

FILE_REGEX = r"employee_(\w+|\d+).pdf\Z"

CODE_COL = "__id__"

TEMPLATE_SHEET = (
    "Personal Left",
    "Personal Right",
    "Earning",
    "Deductions",
    "Salary Left",
    "Salary Right",
)

TEMPLATE_COLUMN = ("Name", "Column")

MIN_TEXT_SIZE: int = 12
MAX_TEXT_SIZE: int = 25

COLOR_SCHEME = {
    "fg_color": "white",
    "button_color": "dark red",
    "text_color": "black",
    "combo_box_color": "white",
}
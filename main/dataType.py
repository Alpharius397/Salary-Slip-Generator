"""Util Data Types"""

from typing import TypedDict, Literal, Optional


class SMTP_CRED(TypedDict):
    """SMTP Credentials Template"""

    email: str
    key: str


class DB_CRED(TypedDict):
    """DB Credentials Template"""

    host: str
    user: str
    password: str
    database: str


type NullStr = Optional[str]
type NullInt = Optional[int]

type MonthList = Literal[
    "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sept", "oct", "nov", "dec"
]
type InstituteList = Literal["Somaiya", "SVV"]
type TypeList = Literal["Teaching", "Non-Teaching", "Temporary"]

monthList = (
    "jan",
    "feb",
    "mar",
    "apr",
    "may",
    "jun",
    "jul",
    "aug",
    "sept",
    "oct",
    "nov",
    "dec",
)

instituteList = ("Somaiya", "SVV")

typeList = ("Teaching", "Non-Teaching", "Temporary", "SVV")

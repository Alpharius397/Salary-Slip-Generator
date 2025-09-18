import types
from typing import (
    Any,
    Callable,
    Generator,
    Hashable,
    Iterable,
    Iterator,
    Literal,
    Optional,
    TypedDict,
    Union,
)


class SMTP_CRED(TypedDict):
    email: str
    key: str


class DB_CRED(TypedDict):
    host: str
    user: str
    password: str
    database: str


type NullStr = str | None
type NullInt = str | None

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

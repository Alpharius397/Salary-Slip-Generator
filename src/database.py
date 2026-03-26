from datetime import datetime
import sys
import typing
import re
from typing import Iterable, Optional
from pathlib import Path
import numpy as np
import pandas as pd  # type: ignore
import pysqlite3  # type: ignore
from src.constants import APP_PATH
from src.logger import ERROR_LOG, Logger
from src.dataTypes import NullStr, TypeList, InstituteList, MonthList

sys.modules["sqlite3"] = pysqlite3
import sqlite3

ERROR = "SQLITE Connection Failed! Please try again"
NO_ID = "HR Emp Code column was not found!"

INSTITUTE = ("somaiya", "svv")
TYPE = ("teaching", "nonteaching", "temporary", "svv")
MONTH = (
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


def join(l: tuple):
    return "|".join(l)


TABLE_FORMAT = rf"^({join(INSTITUTE)})_({join(TYPE)})_({join(MONTH)})_(\d{{4}})\Z"


class CreateTable:
    SUCCESS = "Table Generated Successfully"
    EXISTS = "Table Already Exists"
    COLUMNS_MISMATCH = "Table exists, but columns do not match to those in database"
    ERROR = ERROR
    NO_ID = NO_ID


class UpdateTable:
    ERROR = ERROR
    COLUMNS_MISMATCH = "Table exists, but columns do not match to those in database"
    SUCCESS = "Records were successfully inserted or updated!"
    NO_ID = NO_ID


class DeleteTable:
    ERROR = ERROR
    SUCCESS = "Table was successfully deleted!"
    TABLE_NOT_FOUND = "Table does not exists!"


def sanitize_column(txt: str) -> str:
    """Sanitizing identifiers"""

    def func(txt: str):
        return str(txt).replace("`", "``").replace("\n", "").strip()

    return f"`{func(txt)}`"


def sanitize_value(txt: str) -> str:
    """Sanitizing values"""
    return f"""'{str(txt).replace("'", "''").replace("\n", "").strip()}'"""


def dataRefine(data: pd.DataFrame) -> None:
    """refines columns for sql in place"""
    data.rename(
        columns={col: str(col).strip().replace("\n", "") for col in data.columns},
        inplace=True,
    )


def cleanData(val: typing.Any) -> str:
    try:
        if isinstance(val, (np.integer, np.floating, int, float)):
            return str(int(val))

        if isinstance(val, datetime):
            return val.strftime("%d-%m-%Y")

        return str(val)

    except ValueError:
        return str(val)


def mapping(pd_columns: Iterable[str], columns: str) -> str | None:
    column = columns.lower()

    for i in sorted(pd_columns, key=len):
        if column in i.lower():
            return i

    return None


def check_column(col: str, pd_Data: pd.DataFrame) -> NullStr:
    pred_col = mapping(pd_Data.columns, col)

    if pred_col is None:
        return None

    if data := pd_Data[pred_col].to_numpy(str):
        return data[0]

    return None


class Database:
    def __init__(self, root_dir: Path, error_logger: Logger) -> None:
        self.db: Optional[sqlite3.Connection] = None
        self.logger = error_logger
        self.root_dir = root_dir

    @staticmethod
    def getTableName(
        month: MonthList,
        year: int,
        insti: InstituteList,
        employee_employee_type: TypeList,
    ) -> str:
        return sanitize_column(
            f"{insti.lower()}_{employee_employee_type.lower()}_{month.lower()}_{year}"
        ).replace(" ", "")

    def connectDatabase(self, db_name: str, key: str):

        try:
            self.db = sqlite3.connect(
                self.root_dir.joinpath(f"{db_name}.sqlite").resolve()
            )
            self.db.execute(f"PRAGMA key='{key}';")
            self.db.commit()

            self.add_sqlite_info(f"Connected to Database {db_name}.sqlite")

        except Exception as e:
            self.add_sqlite_error(self.logger.get_error_info(e))

        return self

    def isConnected(self):
        return self.db is not None

    def column_check(
        self,
        month: MonthList,
        year: int,
        columns: Iterable[str],
        insti: InstituteList,
        employee_type: TypeList,
    ) -> bool:
        db_columns = set(self.getColumns(month, year, insti, employee_type))
        seen: set[str] = set()

        for col in columns:
            if (col in seen) or (col not in db_columns):
                return False

            seen.add(col)

        return True

    def createData(
        self,
        month: MonthList,
        year: int,
        columns: list[str],
        insti: InstituteList,
        employee_type: TypeList,
    ) -> str:
        """create a table from month and year if it does not exist"""

        columns = sorted(columns)

        code_col = mapping(columns="hr emp code", pd_columns=columns)

        if not code_col:
            return CreateTable.NO_ID

        if self.db is None:
            return CreateTable.ERROR

        try:
            cursor = self.db.cursor()

            table_name = self.getTableName(month, year, insti, employee_type)

            sql = f"""CREATE TABLE {table_name}(
                {
                ",".join(
                    [
                        f"{sanitize_column(col)} TEXT PRIMARY KEY"
                        if (col == code_col)
                        else f"{sanitize_column(col)} TEXT"
                        for col in columns
                    ]
                )
            }
            )"""

            cursor.execute(sql)
            self.add_sqlite_info(f"Created table {table_name}")
            self.db.commit()

            return CreateTable.SUCCESS

        except sqlite3.OperationalError as e:
            self.add_sqlite_error(self.logger.get_error_info(e))

            if sorted(self.getColumns(month, year, insti, employee_type)) != sorted(
                columns
            ):
                return CreateTable.COLUMNS_MISMATCH

            return CreateTable.EXISTS

        except Exception as e:
            self.add_sqlite_error(self.logger.get_error_info(e))
            return CreateTable.ERROR

    def updateData(
        self,
        data: pd.DataFrame,
        month: MonthList,
        year: int,
        insti: InstituteList,
        employee_type: TypeList,
    ) -> str:
        """updates existing data or inserts new data"""

        idx = mapping(pd_columns=data.columns, columns="HR EMP CODE")

        columns = {j: i for i, j in enumerate(data.columns)}

        if not self.column_check(month, year, data.columns, insti, employee_type):
            return UpdateTable.COLUMNS_MISMATCH

        if not idx:
            return UpdateTable.NO_ID

        if self.db is None:
            return UpdateTable.ERROR

        keys = ",".join(map(sanitize_column, list(columns.keys())))
        table_name = self.getTableName(month, year, insti, employee_type)

        placeholders = ", ".join(["?" for _ in range(len(data.columns))])

        try:
            cursor = self.db.cursor()

            cursor.execute("BEGIN")

            cursor.executemany(
                f"INSERT OR REPLACE INTO {table_name} ({keys}) VALUES ({placeholders})",
                [
                    [cleanData(row[columns[col]]) for col in data.columns]
                    for row in data.itertuples(index=False)
                ],
            )

            cursor.execute("END")

            self.db.commit()

        except Exception as e:
            self.add_sqlite_error(self.logger.get_error_info(e))
            return UpdateTable.ERROR

        self.add_sqlite_info(f"Inserting data into {table_name}")

        return UpdateTable.SUCCESS

    def dropTable(
        self, month: MonthList, year: int, insti: InstituteList, employee_type: TypeList
    ) -> str:
        """Drops the table"""

        if self.db is None:
            return DeleteTable.ERROR

        table_name = self.getTableName(month, year, insti, employee_type)

        try:
            self.db.execute(f"drop table {table_name}")

            self.add_sqlite_info(
                f"Deleting data from {table_name} (Hope you have backup!)"
            )

            self.db.commit()
            return DeleteTable.SUCCESS

        except sqlite3.OperationalError as f:
            self.add_sqlite_error(self.logger.get_error_info(f))
            return DeleteTable.TABLE_NOT_FOUND

        except Exception as e:
            self.add_sqlite_error(self.logger.get_error_info(e))
            return DeleteTable.ERROR

    def showTables(self) -> dict[str, dict[str, dict[str, set[str]]]]:
        """Show all tables"""

        memo: dict[str, dict[str, dict[str, set[str]]]] = {}
        tables: list[str] = []

        if self.db is None:
            return memo

        try:
            cursor = self.db.cursor()
            cursor.execute("PRAGMA main.table_list")
            tables = [str(col[1]) for col in cursor.fetchall()]
            self.add_sqlite_info("Fetching table(s) info")

        except Exception as e:
            self.add_sqlite_error(self.logger.get_error_info(e))
            return memo

        for table in tables:
            if (table_data := re.match(TABLE_FORMAT, table)) is not None:
                insti, employee_type, month, year = table_data.groups()

                if insti not in memo:
                    memo[insti] = {}
                if employee_type not in memo[insti]:
                    memo[insti][employee_type] = {}
                if year not in memo[insti][employee_type]:
                    memo[insti][employee_type][year] = set()

                memo[insti][employee_type][year].add(month)

            else:
                self.add_sqlite_error(
                    f"Unexpected table name format: {table}. {TABLE_FORMAT}"
                )

        return memo

    def getColumns(
        self, month: MonthList, year: int, insti: InstituteList, employee_type: TypeList
    ) -> list[str]:
        """fetches all columns of a table"""
        if self.db is None:
            return []

        try:
            cursor = self.db.cursor()

            cursor.execute(
                f"PRAGMA table_info({Database.getTableName(month, year, insti, employee_type)})"
            )
            self.add_sqlite_info(
                f"Checking table {Database.getTableName(month, year, insti, employee_type)} info"
            )

            return [str(col_data[1]) for col_data in cursor.fetchall()]

        except Exception as e:
            self.add_sqlite_error(self.logger.get_error_info(e))
            return []

    def fetchAll(
        self, month: MonthList, year: int, insti: InstituteList, employee_type: TypeList
    ) -> pd.DataFrame | None:
        """fetches all data from table month_year"""

        data = pd.DataFrame()

        if self.db is None:
            return data

        table_name = Database.getTableName(month, year, insti, employee_type)

        try:
            columns = self.getColumns(month, year, insti, employee_type)
            cursor = self.db.cursor()

            cursor.execute(f"SELECT * FROM {table_name}")
            self.add_sqlite_info(f"Fetching data from table {table_name}")

            result = cursor.fetchall()

            return pd.DataFrame(result, columns=columns, dtype=str)

        except Exception as e:
            self.add_sqlite_error(self.logger.get_error_info(e))
            return data

    def endDatabase(self):
        """end database. RIP"""
        if self.db is None:
            return self

        try:
            self.db.close()
            self.db = None
            self.add_sqlite_info("Closing connection o7")

        except Exception as e:
            self.add_sqlite_error(self.logger.get_error_info(e))

        return self

    def add_sqlite_error(self, msg: str):
        self.logger.write_error(msg, "SQLITE")

    def add_sqlite_info(self, msg: str):
        self.logger.write_info(msg, "SQLITE")


DATABASE = Database(APP_PATH, ERROR_LOG)

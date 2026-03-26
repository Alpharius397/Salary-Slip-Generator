from multiprocessing import Queue
import pandas as pd  #  type: ignore
from src.dataTypes import InstituteList, MonthList, TypeList
from src.database import DATABASE, Database


class DatabaseWrapper:
    """Wrapper for DataBase"""

    def connectToDatabase(self) -> Database:
        """Connect to database"""
        return DATABASE.connectDatabase(self.db_name, self.key)

    def __init__(self, db_name: str, key: str):
        self.db_name = db_name
        self.key = key

    def check_table(self, queue: Queue) -> None:
        """Wrapper for showTables"""
        queue.put(self.connectToDatabase().showTables())
        self.endThis()

    def get_data(
        self,
        queue: Queue,
        institute: InstituteList,
        type: TypeList,
        year: int,
        month: MonthList,
    ) -> None:
        """Wrapper for fetchAll"""
        queue.put(self.connectToDatabase().fetchAll(month, year, institute, type))
        self.endThis()

    def create_table(
        self,
        queue: Queue,
        institute: InstituteList,
        type: TypeList,
        year: int,
        month: MonthList,
        data_columns: list[str],
    ) -> None:
        """Wrapper for create table"""
        create_result = self.connectToDatabase().createData(
            month, year, data_columns, institute, type
        )
        queue.put(create_result)
        self.endThis()

    def fill_table(
        self,
        queue: Queue,
        institute: InstituteList,
        type: TypeList,
        year: int,
        month: MonthList,
        data: pd.DataFrame,
    ):
        """Attempts to insert data or update data in db (Doesn't ask for updation)"""
        upsert_result = self.connectToDatabase().updateData(
            data, month, year, institute, type
        )
        queue.put(upsert_result)
        self.endThis()

    def delete_table(
        self,
        queue: Queue,
        institute: InstituteList,
        type: TypeList,
        year: int,
        month: MonthList,
    ):
        """Delete Table"""
        delete_result = self.connectToDatabase().dropTable(month, year, institute, type)
        queue.put(delete_result)
        self.endThis()

    def endThis(self):
        """End connection"""
        DATABASE.endDatabase()

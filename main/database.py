import mysql.connector as mysql
import pandas as pd
from collections import defaultdict
import re
import numpy as np
from logger import Logger

class Database():
    def __init__(self,error_logger:Logger) -> None:
        self.status = False
        self.db = None
        self.logger = error_logger
        
    def connectDatabase(self,host:str,user:str,password:str,database:str):
        if host and user and password and database:
            try:
                self.db = mysql.connect(    # Attempts sql connection
                            host=host,
                            user=user,
                            password=password,
                            database=database
                        )
                
                self.status = True
                self.add_mysql_info(f'Connected to Database {database}')
            except Exception as e:
                self.add_mysql_error(self.logger.get_error_info(e))
                print('No connection')
        else:
            print("Invalid Creds")
            
        return self

    # create a table from month and year if it does not exist
    def createData(self,month:str,year:int,columns:list[str],insti:str,type:str) -> int:
        columns = sorted(columns)
        
        code_col = mapping(columns='hr emp code',pd_columns=columns)

        if(not self.status) or (not code_col): 
            print(" HR EMP CODE not found or mysql connection failed ")
            return 0
        
        cursor = self.db.cursor()
        
        try:
            
            sql = f"CREATE TABLE {sanitize_column(f'{insti.lower()}_{type.lower()}_{month.lower()}_{year}')}({','.join([ f'{sanitize_column(col)} VARCHAR(225) PRIMARY KEY' if (col==code_col) else f'{sanitize_column(col)} VARCHAR(225)' for col in columns])})"
            cursor.execute(sql)

            self.add_mysql_info(f'Created table {sanitize_column(f"{insti.lower()}_{type.lower()}_{month.lower()}_{year}")}')
            self.db.commit()
            return 1

        except mysql.errors.ProgrammingError as e:
            self.add_mysql_error(self.logger.get_error_info(e))
            if(sorted(self.getColumns(month,year,insti,type))!=sorted(columns)):
                return -2
            else:
                return 2
        
        except Exception as e:
            self.add_mysql_error(self.logger.get_error_info(e))
            print(e)
            return 3
        
        finally:
            cursor.close()
        

    # updates existing data or inserts new data
    def updateData(self,data:pd.DataFrame,month:str,year:int,insti:str,type:str) -> int:
        id = mapping(data.columns,'HR EMP CODE')
        columns = {j:i for i,j in enumerate(data.columns)}
        
        if (sorted(self.getColumns(month,year,insti,type))!=sorted(data.columns)):
            return -1

        
        if (not id) or (not self.status): 
            return 0
            
        for _,row in data.iterrows():
            row_data = row.to_numpy()
            new = {col:cleanData(row_data[columns[col]]) for col in data.columns}
            query =','.join([f"{sanitize_column(col)}={sanitize_value(new[col])}" for col in new])
            keys = ','.join(map(sanitize_column,list(new.keys())))
            values = ','.join(map(sanitize_value,list(new.values())))

            cursor = self.db.cursor()
            try:

                cursor.execute(f"INSERT INTO {sanitize_column(f'{insti.lower()}_{type.lower()}_{month.lower()}_{year}')} ({keys}) VALUE ({values});")    
                self.add_mysql_info(f"Inserting data into {sanitize_column(f'{insti.lower()}_{type.lower()}_{month.lower()}_{year}')}")

            except mysql.errors.IntegrityError as e:
                self.add_mysql_error(self.logger.get_error_info(e))
                
                try:
                    cursor.execute(f"UPDATE {sanitize_column(f'{insti.lower()}_{type.lower()}_{month.lower()}_{year}')} SET {query} WHERE {sanitize_column(id)}={sanitize_value(new[id])};")
                    self.add_mysql_info(f"Updating data into {sanitize_column(f'{insti.lower()}_{type.lower()}_{month.lower()}_{year}')}")
                    
                except Exception as f:
                    self.add_mysql_error(self.logger.get_error_info(f))
                    return 0
                
            except Exception as g:
                self.add_mysql_error(self.logger.get_error_info(g))
                print(g)
                return 
                
            finally:
                cursor.close()
        
            self.db.commit()
        return 1
    
    # drops a table {insti}_{type}_{month}_{year}
    def dropTable(self,insti:str,type:str,month:str,year:int) -> bool | None:
        
        if(not self.status): return None

        cursor = self.db.cursor()
        try:
            cursor.execute(f'drop table {sanitize_column(f"{insti.lower()}_{type.lower()}_{month.lower()}_{year}")}')
            self.add_mysql_info(f'Deleting data from {sanitize_column(f"{insti.lower()}_{type.lower()}_{month.lower()}_{year}")} (Hope you have backup!)')
            
            self.db.commit()

            return True
        except mysql.ProgrammingError as f:
            self.add_mysql_error(self.logger.get_error_info(f))
            return False
        
        except Exception as e:
            self.add_mysql_error(self.logger.get_error_info(e))
            return None
        
    # shows all tables
    def showTables(self) -> dict[str,dict[str,dict[str,set[str]]]]:

        memo = {}
        {'Somaiya':['Teaching','NonTeaching','Temporary'],'SVV':['svv']}
        {"jan":1, "feb":2, "mar":3, "apr":4, "may":5, "jun":6, "jul":7, "aug":8, "sept":9, "oct":10, "nov":11, "dec":12}
        table_format = r'^(somaiya|svv)_(teaching|nonteaching|temporary|svv)_(jan|feb|mar|apr|may|jun|jul|aug|sept|oct|nov|dec)_(\d{4})\Z' # insti_type_month_year
    
        if(not self.status): return memo
        
        cursor = self.db.cursor()
        try:
            cursor.execute('SHOW TABLES')
            tables = [i[0] for i in cursor.fetchall()]
            self.add_mysql_info(f'Fetching table(s) info')
            
        except Exception as e:
            self.add_mysql_error(self.logger.get_error_info(e))    
            return memo

        for table in tables:
            is_table = re.findall(table_format,table)
            if is_table:
                _insti, _type, _month, _year = is_table[0]
                
                if _insti not in memo: 
                    memo[_insti] = {}
                if _type not in memo[_insti]: 
                    memo[_insti][_type] = {}
                if _year not in memo[_insti][_type]: 
                    memo[_insti][_type][_year] = set()
        
                memo[_insti][_type][_year].add(_month)

            else:
                expected_format = "Expected table name format as '^(somaiya|svv)_(teaching|nonteaching|temporary|svv)_(jan|feb|mar|apr|may|jun|jul|aug|sept|oct|nov|dec)_(\d{4})\Z"
                self.add_mysql_error(f"Unexpected table name format: {table}. {expected_format}")

        return memo

    # fetches all columns of a table
    def getColumns(self,month:str,year:int,insti:str,type:str) -> list[str]:
        
        if(not self.status): return []
        
        cursor = self.db.cursor(buffered=True)

        try:
            cursor.execute(f'desc {sanitize_column(f"{insti.lower()}_{type.lower()}_{month.lower()}_{year}")}')
            self.add_mysql_info(f'Checking table {sanitize_column(f"{insti.lower()}_{type.lower()}_{month.lower()}_{year}")} info')
            
        except Exception as e:
            self.add_mysql_error(self.logger.get_error_info(e))    
            print('MySQL Error Occured! (Tables does not exist)')
            return []
        
        return [col_data[0] for col_data in cursor.fetchall()]


    # fetches all data from table month_year  
    def fetchAll(self,month:str,year:int,insti:str,type:str) -> pd.DataFrame|None:
        
        if(not self.status): return pd.DataFrame({},columns=columns,dtype=str)
        
        cursor = self.db.cursor(buffered=True)

        try:
            cursor.execute(f"SELECT * FROM {sanitize_column(f'{insti.lower()}_{type.lower()}_{month.lower()}_{year}')}")
            self.add_mysql_info(f"Fetching data from table {sanitize_column(f'{insti.lower()}_{type.lower()}_{month.lower()}_{year}')}")
            result = cursor.fetchall()
            
        except Exception as e:
            self.add_mysql_error(self.logger.get_error_info(e))    
            return None
        
        columns = self.getColumns(month,year,insti,type)
        print(columns)
        return pd.DataFrame(result,columns=columns,dtype=str)
    
    # end database. RIP
    def endDatabase(self):
        try:
            if self.db: self.db.close()
            self.add_mysql_info(f'Closing connection o7')
            
        except Exception as e:
            self.add_mysql_error(self.logger.get_error_info(e))    
            
        return self
    
    def add_mysql_error(self, msg:str):
        self.logger.write_error(msg,'MySQL')
            
    def add_mysql_info(self, msg:str):
        self.logger.write_info(msg,'MySQL')        


def sanitize_column(txt:str) -> str:
    """ Sanitizing identifiers """
    def func(txt:str): return str(txt).replace('`','``').replace('\n','').strip()
    return f"`{func(txt)}`"

def sanitize_value(txt:str) -> str:
    """ Sanitizing values """
    return f"""'{str(txt).replace("'","''").replace('\n','').strip()}'"""

# refines columns for sql in place
def dataRefine(data:pd.DataFrame) -> None:
    rename = lambda x: x.strip().replace('\n','')

    data.rename(columns={col:rename(str(col)) for col in data.columns},inplace=True)

def cleanData(val:str|int|float) -> str:
    
    try:
        val = int(val) if ((type(val)==np.int64) or (type(val)==np.float64) or (type(val)==float) or (type(val)==int)) else str(val)
    except:
        val = str(val)
    val = str(val)
    txt = re.findall(r"(\d{4})[-,/](\d{1,2})[-,/](\d{1,2})",val)
    val='-'.join([i for i in txt[0][::-1]]) if txt else val

    return str(val).replace('"',"'")

# tries to find columns based on the frequency of word in column
def mapping(pd_columns:list[str],columns:str) -> str | None:
    if(columns in pd_columns):
        return columns
    elif (columns.lower() in pd_columns):
        return columns.lower()
    elif (columns.upper() in pd_columns):
        return columns.upper()
    elif (columns.capitalize() in pd_columns):
        return columns.capitalize()
    else:
        return None

def check_column(col:str,pd_columns:list[str],pd_Data:pd.DataFrame) -> str:
    pred_col = mapping(pd_columns,col)

    if pred_col is not None:
        return None if (not pd_Data[pred_col].values) else pd_Data[pred_col].values[0]
    else: 
        return None

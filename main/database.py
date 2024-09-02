import mysql.connector
import pandas as pd
from collections import defaultdict

class Database():
    def __init__(self,host:str,user:str,password:str,database:str) -> None:
        self.status = False
        if host and user and password and database:
            try:
                self.db = mysql.connector.connect(    # Attempts sql connection
                            host=host,
                            user=user,
                            password=password,
                            database=database
                        )
                
                self.status = True
            except:
                self.status = False
                print('No connection')

    
    # create a table from month and year if it does not exist
    def createData(self,month:str,year:int,columns:list[str],insti:str,type:str) -> int:
        code_col = mapping(columns='hr emp code',pd_columns=columns)

        if(not self.status) or (not code_col): 
            print(" HR EMP CODE not found or mysql connection failed ")
            return -1
        
        cursor = self.db.cursor()
        
        try:
            
            sql = f"CREATE TABLE {insti}_{type}_{month}_{year}({','.join([ col + ' VARCHAR(225) PRIMARY KEY' if col==code_col else col + ' VARCHAR(225)' for col in columns])})"
            cursor.execute(sql)

            print('Table Created')
            self.db.commit()
            return 1
        
        except:
            print('Table Exists')
            return 0

    # updates existing data or inserts new data
    def updateData(self,data:pd.DataFrame,month:str,year:int,insti:str,type:str) -> int:
        id = mapping(data.columns,'hr emp code')

        if sorted(self.getColumns(month,year,insti,type))!=sorted(list(data.columns)):
            return -1
        
        if (not id) or (not self.status): 
            print(" HR EMP CODE not found or mysql connection failed ")
            return None
        
        for i in data[id]:
            new = {col:data[data[id]==i][col].values[0] for col in data.columns}
            query =','.join([f"{col}='{new[col]}'" for col in new if col!=id])
            keys = ','.join(new.keys())
            values = ','.join([ f"'{i}'" for i in new.values()])

            cursor = self.db.cursor()
            try:

                cursor.execute(f"INSERT INTO {insti}_{type}_{month}_{year} ({keys}) VALUE ({values})")    

            except mysql.connector.errors.IntegrityError as e:
                cursor.execute(f'UPDATE {insti}_{type}_{month}_{year} SET {query} WHERE {id}={i}')

            except mysql.connector.errors.ProgrammingError as f:
                return 0

            self.db.commit()
        return 1
    
    # drops a table {insti}_{type}_{month}_{year}
    def dropTable(self,insti:str,type:str,month,year) -> int:
        
        if(not self.status): return 0

        cursor = self.db.cursor()
        try:
            cursor.execute(f'drop table {insti}_{type}_{month}_{year}')
            self.db.commit()

            return 1
        except mysql.connector.errors.ProgrammingError as f:
            return 0
        
    # shows all tables
    def showTables(self) -> dict[str,dict[str,list[str]]]:

        memo = {}
        if(not self.status): return memo
        
        cursor = self.db.cursor()
        try:
            cursor.execute('SHOW TABLES')
        except:
            print('MySQL Error Occured!')
            return memo

        temp = cursor.fetchall()
        year = [table[0].split('_') for table in temp]

        for parts in year:
            if len(parts) == 4:
                i, j, k, l = parts
                if i not in memo:
                    memo[i] = {}
                if j not in memo[i]:
                    memo[i][j] = defaultdict(list)

                memo[i][j][l] += [k] if k not in memo[i][j][l] else []

            else:
                print(f"Unexpected table name format: {'_'.join(parts)}")

        return memo

    # fetches all columns of a table
    def getColumns(self,month:str,year:int,insti:str,type:str) -> list[str]:
        
        if(not self.status): return []
        
        cursor = self.db.cursor(buffered=True)

        try:
            cursor.execute(f'desc {insti}_{type}_{month}_{year}')
        except:
            print('MySQL Error Occured! (Tables does not exist)')
            return []
        
        return [col_data[0] for col_data in cursor.fetchall()]


    # fetches all data from table month_year  
    def fetchAll(self,month:str,year:int,insti:str,type:str) -> pd.DataFrame:
        
        if(not self.status): return pd.DataFrame({},columns=columns,dtype=str)
        
        cursor = self.db.cursor()
        cursor = self.db.cursor(buffered=True)

        try:
            cursor.execute(f"SELECT * FROM {insti}_{type}_{month}_{year}")

        except:
            print('Table does not exists')
            return None
        
        columns = self.getColumns(month,year,insti,type)
        return pd.DataFrame(cursor.fetchall(),columns=columns,dtype=str)
    
    # end database. RIP
    def endDatabase(self) -> None:
        self.db.close()

# refines columns for sql in place
def dataRefine(data:pd.DataFrame) -> None:
    rename = lambda x: x.strip().replace('[','_').replace(']','_').replace('{','_').replace('}','_').replace('(','_').replace(')','_').replace('  ',' ').replace(' ','_').replace('-','').replace('.','').replace('\n','').replace('/','_or_').replace('%','').replace('&','_and_').replace(',','').replace(':','').replace('__','_').lower()

    data.rename(columns={col:rename(str(col)) for col in data.columns},inplace=True)

# tries to find columns based on the frequency of word in column
def mapping(pd_columns:list[str],columns:str) -> dict[str,str]:

    check_columns = columns.lower().split(' ')

    memo=defaultdict(lambda: {'count':0,'col':None})
    to_check = [col for col in pd_columns if any(word in col.lower() for word in check_columns)]

    for col in to_check:
        asq = 0
        for check in check_columns:
            
            if check in col.lower():
                asq += 1
                
        if memo[columns]['count']<asq:
            memo[columns]['col']=col
            memo[columns]['count']=asq
            
    return memo[columns]['col'] 

# checks for word and returns the value of column (that matches word) if present, else None
def check_column(col:str,pd_columns:list[str],pd_Data:pd.DataFrame) -> str:
    pred_col = mapping(pd_columns,col)

    if pred_col is not None:
        return pd_Data[pred_col].values[0]
    else: 
        return None
    
"""
Optimized Gemini Code

import pandas as pd
from fuzzywuzzy import fuzz

def check_column_efficient(col: str, pd_columns: list[str], pd_data: pd.DataFrame) -> str:

    col_lower = col.lower() 

    filtered_cols = [c for c in pd_columns if any(w in c.lower() for w in col_lower.split())]

    if filtered_cols:

        distances = {c: fuzz.ratio(col_lower, c.lower()) for c in filtered_cols}

        best_match = max(distances, key=distances.get)

        return pd_data[best_match].values[0]

    else:
        return 'None'
        
"""
"""# Must do these 3 steps
pde = pd.read_excel("Excel-to-Pdf-Generator\sample_data\Sample sheet for salary calculation and salary slip (1).xlsx")
dataRefine(pde)

b = Database(
        host="localhost",
        user="root",
        password="1234",
        database="somaiya_salary"
    )"""




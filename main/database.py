import mysql.connector as mysql
import pandas as pd
from collections import defaultdict
import re
from datetime import date,datetime
import numpy as np

class Database():
    def __init__(self) -> None:
        self.status = False
        self.db = None
        
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
            except:
                print('No connection')
        else:
            print("Invalid Creds")
            
        return self

    # create a table from month and year if it does not exist
    def createData(self,month:str,year:int,columns:list[str],insti:str,type:str) -> int:
        code_col = mapping(columns='hr emp code',pd_columns=columns)

        if(not self.status) or (not code_col): 
            print(" HR EMP CODE not found or mysql connection failed ")
            return 0
        
        if(len(set(columns))<len(columns)):
            return -1
        
        cursor = self.db.cursor()
        
        try:
            
            sql = f"CREATE TABLE {insti.lower()}_{type.lower()}_{month.lower()}_{year}({','.join([ col + ' VARCHAR(225) PRIMARY KEY' if col==code_col else col + ' VARCHAR(225)' for col in columns])})"
            cursor.execute(sql)

            print('Table Created')
            self.db.commit()
            return 1

        except mysql.errors.ProgrammingError:
            print('Table Exists')
            return 2
        
        except Exception as f:
            print(f)
            return 3
        

    # updates existing data or inserts new data
    def updateData(self,data:pd.DataFrame,month:str,year:int,insti:str,type:str) -> int:
        id = mapping(data.columns,'hr emp code')

        if (sorted(self.getColumns(month,year,insti,type))!=sorted(data.columns)):
            return -1

        
        if (not id) or (not self.status): 
            print(" HR EMP CODE not found or MySQL connection failed ")
            return 0
            
        for i in PandaGenerator(data,id):
            
            new = {col:cleanData(i[col].values) for col in i.columns}
            query =','.join([f"{col}='{new[col]}'" for col in new])
            keys = ','.join(new.keys())
            values = ','.join([ f"'{i}'" for i in new.values()])

            cursor = self.db.cursor()
            try:

                cursor.execute(f"INSERT INTO {insti.lower()}_{type.lower()}_{month.lower()}_{year} ({keys}) VALUE ({values});")    

            except mysql.errors.IntegrityError as e:
                try:
                    cursor.execute(f"UPDATE {insti.lower()}_{type.lower()}_{month.lower()}_{year} SET {query} WHERE {id}={new[id]};")
                except Exception as e:
                    print(e,f"UPDATE {insti.lower()}_{type.lower()}_{month.lower()}_{year} SET {query} WHERE {id}={new[id]};")
                    return 0
            except Exception as e:
                print(e)
                return 0

            self.db.commit()
        return 1
    
    # drops a table {insti}_{type}_{month}_{year}
    def dropTable(self,insti:str,type:str,month:str,year:int) -> bool | None:
        
        if(not self.status): return None

        cursor = self.db.cursor()
        try:
            cursor.execute(f'drop table {insti.lower()}_{type.lower()}_{month.lower()}_{year}')
            self.db.commit()

            return True
        except mysql.ProgrammingError as f:
            print("Table doesn't exists")
            return False
        
        except Exception as e:
            return None
        
    # shows all tables
    def showTables(self) -> dict[str,dict[str,dict[str,set[str]]]]:

        memo = {}
        {'Somaiya':['Teaching','NonTeaching','Temporary'],'SVV':['svv']}
        {"jan":1, "feb":2, "mar":3, "apr":4, "may":5, "jun":6, "jul":7, "aug":8, "sept":9, "oct":10, "nov":11, "dec":12}
        table_format = r'^(somaiya|svv)_(teaching|nonteaching|temporary|svv)_(jan|feb|mar|apr|may|jun|jul|aug|sept|oct|nov|dec)_(\d{4})$' # insti_type_month_year
        
        if(not self.status): return memo
        
        cursor = self.db.cursor()
        try:
            cursor.execute('SHOW TABLES')
            tables = [i[0] for i in cursor.fetchall()]
        except:
            print('MySQL Error Occured!')
            return memo

        print(tables)

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
                print(f"Unexpected table name format: {table}")

        return memo

    # fetches all columns of a table
    def getColumns(self,month:str,year:int,insti:str,type:str) -> list[str]:
        
        if(not self.status): return []
        
        cursor = self.db.cursor(buffered=True)

        try:
            cursor.execute(f'desc {insti.lower()}_{type.lower()}_{month.lower()}_{year}')
        except:
            print('MySQL Error Occured! (Tables does not exist)')
            return []
        
        return [col_data[0] for col_data in cursor.fetchall()]


    # fetches all data from table month_year  
    def fetchAll(self,month:str,year:int,insti:str,type:str) -> pd.DataFrame|None:
        
        if(not self.status): return pd.DataFrame({},columns=columns,dtype=str)
        
        cursor = self.db.cursor()
        cursor = self.db.cursor(buffered=True)

        try:
            cursor.execute(f"SELECT * FROM {insti.lower()}_{type.lower()}_{month.lower()}_{year}")
            result = cursor.fetchall()
        except:
            print('Table does not exists')
            return None
        
        columns = self.getColumns(month,year,insti,type)
        return pd.DataFrame(result,columns=columns,dtype=str)
    
    # end database. RIP
    def endDatabase(self):
        try:
            if self.db: self.db.close()
        except:
            pass
        return self
            
# refines columns for sql in place
def dataRefine(data:pd.DataFrame) -> None:
    rename = lambda x: x.strip().replace('[','_').replace(']','_').replace('{','_').replace('}','_').replace('(','_').replace(')','_').replace('  ',' ').replace(' ','_').replace('-','').replace('.','').replace('\n','').replace('/','_or_').replace('%','').replace('&','_and_').replace(',','').replace(':','').replace('__','_').lower()

    data.rename(columns={col:rename(str(col)) for col in data.columns},inplace=True)

def cleanData(val:str|int|float) -> str:
    
    if len(val)==0:
        return ""
    val = val[0]
    try:
        val = int(val) if ((type(val)==np.int64) or (type(val)==np.float64) or (type(val)==float) or (type(val)==int)) else str(val)
    except:
        val = str(val)
    val = str(val)
    txt = re.findall(r"(\d{4})[-,/](\d{1,2})[-,/](\d{1,2})",val)
    val='-'.join([i for i in txt[0][::-1]]) if txt else val

    return str(val)

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

class PandaGenerator:
    def __init__(self,data: pd.DataFrame,unique_column:str) -> None:
        self.data = data
        self.unique = unique_column
        self.columns = self.data.columns
        self.memo = self._make_memo()
        self.keys = list(self.memo.keys())
        self.idx = -1

    def _make_memo(self):
        memo = {}
        
        row,col = self.data.shape
        
        for i in range(row):
            idx = self.data.iloc[i,:][self.unique]
            memo[idx] = i
            
        return memo
    def __iter__(self): return self
    
    def __next__(self):
        if(self.idx>len(self.keys)-2): raise StopIteration
    
        self.idx+=1
        return pd.DataFrame([self.data.iloc[self.memo[self.keys[self.idx]]]],columns=self.columns)
    
    def __getitem__(self,index):
        if(index not in self.memo):
            raise KeyError(f"Key: {index} not found")
        return pd.DataFrame([self.data.iloc[self.memo[index]]],columns=self.columns)
    
# Optimized Gemini Code
# import pandas as pd
# from fuzzywuzzy import fuzz
# def check_column_efficient(col: str, pd_columns: list[str], pd_data: pd.DataFrame) -> str:
#     col_lower = col.lower() 
#     filtered_cols = [c for c in pd_columns if any(w in c.lower() for w in col_lower.split())]
#     if filtered_cols:
#         distances = {c: fuzz.ratio(col_lower, c.lower()) for c in filtered_cols}
#         best_match = max(distances, key=distances.get)
#         return pd_data[best_match].values[0]
#     else:
#         return 'None'
        

# # Must do these 3 steps
# # pde = pd.read_excel("Excel-to-Pdf-Generator\sample_data\Sample sheet for salary calculation and salary slip (1).xlsx")
# # dataRefine(pde)

# b = Database().connectDatabase(
#         host="localhost",
#         user="root",
#         password="1234",
#         database="somaiya_salary"
# )

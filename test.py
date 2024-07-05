import mysql.connector
import pandas as pd
from collections import defaultdict

class Database():
    def __init__(self,host:str,user:str,password:str,database:str) -> None:
        self.db = mysql.connector.connect(    # Attempts sql connection
                    host=host,
                    user=user,
                    password=password,
                    database=database
                )
    
    # create a table from month and year if it does not exist
    def createData(self,month:str,year:int,columns:list[str],insti:str,type:str) -> int:
        cursor = self.db.cursor()

        try:
            sql = f"CREATE TABLE {insti}_{type}_{month}_{year}({','.join([ col + ' VARCHAR(225) PRIMARY KEY' if col=='HR_EMP_CODE' else col + ' VARCHAR(225)' for col in columns])})"
            cursor.execute(sql)

            print('Table Created')
            self.db.commit()

            return 1
        except:
            print('Table Exists')
            return 0

    # updates existing data or inserts new data
    def updateData(self,data,month:str,year:int,insti:str,type:str) -> None:
        cursor = self.db.cursor()

        for i in data['HR_EMP_CODE']:
            new = {col:data[(data['HR_EMP_CODE']==i)][[col]].iloc[0,0] for col in data.columns}
            query =','.join([f"{col}='{new[col]}'" for col in new if col!='HR_EMP_CODE'])
            
            try:
                cursor.execute(f"INSERT INTO {insti}_{type}_{month}_{year} ({','.join(new.keys())}) VALUE ({','.join([str(i) for i in new.values()])})")

            except mysql.connector.errors.ProgrammingError as e:
                cursor.execute(f'UPDATE {insti}_{type}_{month}_{year} SET {query} WHERE HR_EMP_CODE={i}')
            except:
                print('Not MySQL Error!')
                return None
            
            self.db.commit()

    # shows all tables
    def showTables(self) -> list[tuple[str]]:

        def contains(list:list,char:str) -> int:
            try:
                temp = list.index('_')
                return True
            except ValueError:
                return False
         
        cursor = self.db.cursor()
        memo = {}
        try:
            cursor.execute('show tables')
        except:
            print('MySQL Error Occured!')
            return None

        temp = cursor.fetchall()
        print(temp)
        year =  [table[0].split('_') for table in temp]
        
        for i,j,k,l in year:
            if i not in memo:
                memo[i] = {}
            if j not in memo[i]:
                memo[i][j] = defaultdict(list)

            memo[i][j][l] += memo[i][j][l] + [k]

        return memo

    def getColumns(self,month,year,insti:str,type:str):
        cursor = self.db.cursor(buffered=True)

        try:
            cursor.execute(f'desc {insti}_{type}_{month}_{year}')
        except:
            print('MySQL Error Occured!')
            return None
        
        return [col_data[0] for col_data in cursor.fetchall()]


    # fetches data for That guy from table month_year
    def fetchThat(self,month:str,year:int,emp_id:int,insti:str,type:str) -> tuple[list[str]]:
        cursor = self.db.cursor(buffered=True)

        try:
            cursor.execute(f" SELECT * FROM {insti}_{type}_{month}_{year} where HR_EMP_CODE={emp_id}")
        except:
            print('MySQL Error Occured!')
            return None
        
        columns = self.getColumns(month,year,insti,type)
        return pd.DataFrame(cursor.fetchall(),columns=columns)

    # fetches all data from table month_year  
    def fetchAll(self,month:str,year:int,insti:str,type:str) -> dict[str,list[str]]:
        cursor = self.db.cursor(buffered=True)

        try:
            cursor.execute(f"SELECT * FROM {insti}_{type}_{month}_{year}")

        except:
            print('Table does not exists')
            return None
        
        columns = self.getColumns(month,year,insti,type)
        return pd.DataFrame(cursor.fetchall(),columns=columns)
    
    # end database. RIP
    def endDatabase(self) -> None:
        self.db.close()
    

def dataRefine(data):

    rename = lambda x: x.strip().replace('  ',' ').replace('-','').replace('.','').replace(' ','_').replace('\n','').replace('/','_or_').replace('%','').replace('&','_and_').replace(',','_').replace('__','_')

    data.rename(columns={col:rename(col) for col in data.columns},inplace=True)

# Must do these 3 steps
"""pde = pd.read_excel("front/KJSIT_MAY_2023.xlsx")
dataRefine(pde)

b = Database(
        host="localhost",
        user="root",
        password="1234",
        database="somaiya_salary"
    )"""

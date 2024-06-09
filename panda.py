import pandas as pd
import random
file_path = 'Sample sheet for salary calculation and salary slip (1).xlsx'
ans=[]

res = pd.read_excel(file_path)
res.fillna(random.randint(0,10000),axis=1,inplace=True)
print(res)
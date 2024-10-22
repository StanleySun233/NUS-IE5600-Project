import sqlite3
import pandas as pd

df = pd.read_excel('../data/tras_may.xls').values.tolist()

sheet = []
for i in df:
    for j in i:
        if str(j) != 'nan':
            sheet.append(eval(j))
sheet = pd.DataFrame(sheet, columns=["ts",'u8time','mmsi','lon','lat','speed','course','heading'])
sheet[["ts",'mmsi','lon','lat','speed','heading']].to_sql("ais", sqlite3.Connection("../data/ais.db"), if_exists="replace", index=False)
sheet[["ts",'mmsi','lon','lat','speed','heading']].to_csv("../data/ais.csv",index=False,encoding='utf-8')
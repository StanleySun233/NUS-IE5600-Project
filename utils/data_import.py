import sqlite3

import pandas as pd

df = pd.read_excel('../data/tras_may.xls').values.tolist()

sheet = []
for i in df:
    for j in i:
        if str(j) != 'nan':
            sheet.append(eval(j))
sheet = pd.DataFrame(sheet, columns=["ts", 'u8time', 'mmsi', 'lon', 'lat', 'speed', 'course', 'heading'])
sheet[["mmsi", 'ts', 'lon', 'lat', 'speed', 'heading']].to_sql("ais", sqlite3.Connection("../data/ais.db"),
                                                               if_exists="replace")

sheet[["mmsi", 'ts', 'lon', 'lat', 'speed', 'heading']].to_csv("../data/ais.csv", index=False, encoding='utf-8')

sheet[["mmsi", 'ts', 'lon', 'lat', 'speed', 'heading']][
    (sheet['mmsi'] == '412415970') | (sheet['mmsi'] == '413457740')].to_csv("../data/test.csv", index=False,
                                                                            encoding='utf-8')

# 连接到 SQLite 数据库
conn = sqlite3.connect('../data/ais.db')
cursor = conn.cursor()

# 查询 ais 表中 distinct 的 mmsi
cursor.execute("SELECT DISTINCT mmsi FROM ais")
distinct_mmsis = cursor.fetchall()

# 将 distinct mmsi 插入 ship 表中
cnt = 0
for mmsi in distinct_mmsis:
    # 假设 ship 表有一列 mmsi
    cursor.execute("INSERT INTO ship (id,mmsi) VALUES (?,?)", (cnt, mmsi[0],))
    cnt += 1

# 提交更改
conn.commit()

# 关闭连接
conn.close()

import os
import sqlite3
import pandas as pd

# Check if the database already exists
db_path = './data/ais.db'
if os.path.exists(db_path):
    print("Database already exists. Exiting.")
    exit(0)


# Create the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create tables
cursor.execute('''
    CREATE TABLE ais (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mmsi TEXT,
        ts TEXT,
        lon REAL,
        lat REAL,
        speed REAL,
        heading REAL
    )
''')
cursor.execute('''
    CREATE TABLE ship (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mmsi TEXT UNIQUE
    )
''')

# Read ais.csv into a pandas DataFrame
df = pd.read_csv('./data/ais.csv')

# Insert data into the ais table
for _, row in df.iterrows():
    cursor.execute('''
        INSERT INTO ais (mmsi, ts, lon, lat, speed, heading)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (row['mmsi'], row['ts'], row['lon'], row['lat'], row['speed'], row['heading']))

# Insert unique mmsi values into the ship table
unique_mmsi = df['mmsi'].unique()
for mmsi in unique_mmsi:
    cursor.execute('''
        INSERT INTO ship (mmsi)
        VALUES (?)
    ''', (mmsi,))

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database initialization completed.")

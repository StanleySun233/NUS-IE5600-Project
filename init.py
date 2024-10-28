import os
import sqlite3

import pandas as pd

# Check if the database already exists
db_path = './data/ais.db'
if os.path.exists(db_path):
    os.remove(db_path)

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
        mmsi TEXT
    )
''')

# Process the CSV in chunks
chunk_size = 10000  # Adjust the chunk size based on your available memory
csv_file = './data/ais.csv'

for chunk in pd.read_csv(csv_file, chunksize=chunk_size):
    # Insert data into the ais table
    for _, row in chunk.iterrows():
        cursor.execute('''
            INSERT INTO ais (mmsi, ts, lon, lat, speed, heading)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (row['mmsi'], row['ts'], row['lon'], row['lat'], row['speed'], row['heading']))

    # Insert unique mmsi values into the ship table
    unique_mmsi = chunk['mmsi'].unique()
    for mmsi in unique_mmsi:
        cursor.execute('''
            INSERT INTO ship (mmsi)
            VALUES (?)
        ''', (mmsi,))

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database initialization completed.")

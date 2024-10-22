import sqlite3
from model.Ship import create_ship_by_mmsi

db = sqlite3.connect("./data/ais.db")

ship = create_ship_by_mmsi(412354710, db)
ship.draw_traces()

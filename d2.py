from math import radians, sin, cos, sqrt, atan2
from ShipPoint import ShipPoint
from Ship import Ship
import folium
from folium.plugins import TimeSliderChoropleth
import json
# 计算两点之间的地球表面距离（单位：公里）
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # 地球半径，单位为公里

    lat1, lon1 = radians(lat1), radians(lon1)
    lat2, lon2 = radians(lat2), radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance


import sqlite3  # 假设你使用的是SQLite数据库
from datetime import datetime, timedelta


# 从数据库中提取最新的船舶坐标数据
def get_latest_ship_positions(db_connection):
    query = """
    SELECT mmsi, ts, lon, lat
    FROM ais
    ORDER BY mmsi, ts DESC
    """
    cursor = db_connection.cursor()
    cursor.execute(query)

    ships = {}
    for row in cursor.fetchall():
        mmsi, ts, lon, lat = row
        if mmsi not in ships:
            ships[mmsi] = Ship(mmsi)
        ship_point = ShipPoint(ts, lon, lat, 0, 0, 0)  # 这里只用到经纬度和时间
        ships[mmsi].traces.append(ship_point)

    return ships


# 检查所有船舶的最后位置，触发碰撞警报
def check_for_collisions(ships, distance_threshold=0.2):
    # 获取所有船舶的最后位置
    last_positions = {ship.mmsi: ship.traces[-1] for ship in ships.values() if ship.traces}

    mmsi_list = list(last_positions.keys())
    for i in range(len(mmsi_list)):
        for j in range(i + 1, len(mmsi_list)):
            mmsi1, mmsi2 = mmsi_list[i], mmsi_list[j]
            ship1_point = last_positions[mmsi1]
            ship2_point = last_positions[mmsi2]


            distance = haversine(ship1_point.lat, ship1_point.lon, ship2_point.lat, ship2_point.lon)
            if distance <= distance_threshold and abs(ship1_point.ts - ship2_point.ts) <=timedelta(hours=0.05):
                print(
                    f"Warning: Ships {mmsi1} and {mmsi2} are too close (within {distance_threshold} km) at {ship1_point.ts}!")
                print()




conn = sqlite3.connect('./data/ais.db')
ships = get_latest_ship_positions(conn)
check_for_collisions(ships)

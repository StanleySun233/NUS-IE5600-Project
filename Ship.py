import sqlite3

import pandas as pd
import folium
from ShipPoint import ShipPoint
# Ship 类定义
class Ship:
    def __init__(self, mmsi):
        self.mmsi = mmsi
        self.traces = []

    def add_trace(self, shipPoint: ShipPoint):
        # 插入时保持 traces 按时间顺序
        if not self.traces:
            self.traces.append(shipPoint)
        else:
            inserted = False
            for i in range(len(self.traces)):
                if shipPoint < self.traces[i]:
                    self.traces.insert(i, shipPoint)
                    inserted = True
                    break
            if not inserted:
                self.traces.append(shipPoint)

    def get_earliest_trace(self):
        if self.traces:
            return self.traces.pop(0)
        else:
            return None

    def print_all_traces(self):
        for point in self.traces:
            print(f'Time: {point.t}, Latitude: {point.lat}, Longitude: {point.lon}')

    def draw_traces(self, output_file="ship_trace_map.html"):
        # 创建地图对象，默认以第一个轨迹点为中心
        if not self.traces:
            print("No traces available to draw.")
            return

        # 使用第一个轨迹点的经纬度创建地图
        start_lat = self.traces[0].lat
        start_lon = self.traces[0].lon
        ship_map = folium.Map(location=[start_lat, start_lon], zoom_start=12)

        # 创建一个列表来保存所有轨迹点的坐标
        points = [(point.lat, point.lon) for point in self.traces]

        # 使用 PolyLine 将轨迹点连接成线
        folium.PolyLine(points, color="blue", weight=2.5, opacity=1).add_to(ship_map)

        # 使用 CircleMarker 绘制每个轨迹点
        for point in self.traces:
            folium.CircleMarker(
                location=(point.lat, point.lon),
                radius=5,  # 圆点的半径
                color='red',
                fill=True,
                fill_color='red',
                fill_opacity=0.6,
                popup=f"Time: {point.ts}, Lat: {point.lat}, Lon: {point.lon}"
            ).add_to(ship_map)

        # 保存地图为 HTML 文件
        ship_map.save(output_file)
        print(f"Map saved to {output_file}")

def create_ship_by_mmsi(mmsi:str,db:sqlite3.Connection) -> Ship:
    df = pd.read_sql_query(f'SELECT ts,lon,lat,speed,course,heading FROM AIS where mmsi = {mmsi}', db)
    s = [ShipPoint(*df.values.tolist()[i]) for i in range(len(df))]
    ship = Ship(mmsi)
    for i in s:
        ship.add_trace(i)
    return ship
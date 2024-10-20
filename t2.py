import folium
import pandas as pd
from folium.plugins import TimestampedGeoJson
import json
from datetime import datetime
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from datetime import datetime
from matplotlib import style

# Connect to the database
db = sqlite3.connect("./data/ais.db")

# Retrieve data from the database (timestamp, longitude, latitude for specified ships)
data = (db.cursor()
        .execute("""SELECT mmsi, ts, lon, lat FROM ais WHERE mmsi IN (412415970, 413457740) ORDER BY ts""")
        .fetchall())

df = pd.DataFrame(data, columns=['mmsi', 'ts', 'lon', 'lat'])
# 确保时间戳是 datetime 格式
df['ts'] = pd.to_datetime(df['ts'])

# 创建Folium地图对象
m = folium.Map(location=[29.7450467, 122.17775], zoom_start=12)

# 创建空的GeoJSON特征集合
features = []

# 为每艘船创建时间序列轨迹
for mmsi in df['mmsi'].unique():
    ship_data = df[df['mmsi'] == mmsi]
    last_index = ship_data.index[-1]  # 找到每艘船的最新位置

    for i, row in ship_data.iterrows():
        if i == last_index:
            # 最新位置用长方形表示
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Polygon',  # 使用Polygon类型创建长方形
                    'coordinates': [[
                        [row['lon'] - 0.0001, row['lat'] - 0.0001],  # 左下角
                        [row['lon'] + 0.0001, row['lat'] - 0.0001],  # 右下角
                        [row['lon'] + 0.0001, row['lat'] + 0.0001],  # 右上角
                        [row['lon'] - 0.0001, row['lat'] + 0.0001],  # 左上角
                        [row['lon'] - 0.0001, row['lat'] - 0.0001]  # 回到左下角闭合
                    ]]
                },
                'properties': {
                    'time': row['ts'].isoformat(),
                    'style': {'color': 'blue' if mmsi == 412415970 else 'red'},
                    'icon': 'square',
                    'iconstyle': {
                        'fillColor': 'blue' if mmsi == 412415970 else 'red',
                        'fillOpacity': 0.6,
                        'stroke': 'true',
                        'radius': 5
                    }
                }
            }
        else:
            # 历史位置用圆点表示
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [row['lon'], row['lat']],
                },
                'properties': {
                    'time': row['ts'].isoformat(),
                    'style': {'color': 'blue' if mmsi == '412415970' else 'red'},
                    'icon': 'circle',
                    'iconstyle': {
                        'fillColor': 'blue' if mmsi == '412415970' else 'red',
                        'fillOpacity': 0.6,
                        'stroke': 'true',
                        'radius': 5
                    }
                }
            }
        features.append(feature)

# 将特征集转换为带时间戳的GeoJSON
timestamped_geojson = TimestampedGeoJson(
    {
        'type': 'FeatureCollection',
        'features': features,
    },
    period='PT10S',  # 每分钟更新一次
    add_last_point=True,
    auto_play=True,
    loop=False,
    max_speed=1,
    loop_button=True,
    date_options='YYYY-MM-DD HH:mm:ss',
    time_slider_drag_update=True
)

# 将动态轨迹添加到地图
timestamped_geojson.add_to(m)

# 保存地图到HTML文件
m.save('dynamic_ship_trajectory.html')
import sqlite3

import folium
from folium.plugins import TimestampedGeoJson
import pandas as pd
db = sqlite3.connect("./data/ais.db")
# 示例数据，假设你的时序数据

data = (db.cursor().
        execute("""select ts,lon,lat from ais where mmsi in (413245110,413426990) """)).fetchall()


# 将数据转换为 GeoJSON 格式
features = []
for entry in data:
    time = entry[0]
    lon = entry[1]
    lat = entry[2]

    feature = {
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': [lon, lat],
        },
        'properties': {
            'time': time,
        }
    }
    features.append(feature)

geojson_data = {
    'type': 'FeatureCollection',
    'features': features
}

# 创建 Folium 地图
m = folium.Map(location=[29.7450467, 122.17775], zoom_start=12)

# 添加带时间滑块的GeoJson数据
TimestampedGeoJson(
    geojson_data,
    transition_time=200,  # 动画每帧之间的延迟，单位毫秒
    add_last_point=True,
    period='PT1M',  # 时间步长为1分钟
    auto_play=False,  # 是否自动播放
    loop=False  # 是否循环播放
).add_to(m)

# 显示地图
m.save("timelapse_map.html")

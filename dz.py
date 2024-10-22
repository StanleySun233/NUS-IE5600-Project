import folium
from folium.plugins import TimestampedGeoJson
import pandas as pd
import json
from datetime import datetime

def plot_ship_trace_with_timeslider_scatter(dates, lats, lons, start_zoom=10):
    # 创建基础地图
    ship_map = folium.Map(location=[lats[0], lons[0]], zoom_start=start_zoom)

    # 创建 GeoJson 格式的数据，用于 CircleMarker
    features = []
    for i in range(len(dates)):
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lons[i], lats[i]]
            },
            "properties": {
                "time": dates[i],  # 使用 ISO 格式的时间
                "style": {
                    "radius": 6,  # 点的大小
                    "color": "blue",  # 点的边框颜色
                    "fillColor": "blue",  # 点的填充颜色
                    "fillOpacity": 0.6,  # 填充透明度
                }
            }
        }
        features.append(feature)

    # 构造 GeoJson 数据对象
    geojson_data = {
        "type": "FeatureCollection",
        "features": features
    }

    # 使用 TimestampedGeoJson 进行时间滑动条的动态展示
    TimestampedGeoJson(
        data=geojson_data,
        transition_time=200,  # 动画的速度（毫秒）
        loop=False,
        auto_play=False,  # 默认不自动播放
        add_last_point=True,  # 在轨迹的最后保留最后一个点
        period='PT1M',  # 时间间隔设置为1分钟的格式
    ).add_to(ship_map)

    return ship_map

# 示例调用
dates = ['2023-10-20T12:00:00', '2023-10-20T12:05:00', '2023-10-20T12:10:00']
lats = [29.7450467, 29.7465000, 29.7480000]
lons = [122.17775, 122.17850, 122.18000]

# 生成带时间滑动条的地图
ship_map = plot_ship_trace_with_timeslider_scatter(dates, lats, lons)
ship_map.save("ship_trace_scatter_with_timeslider.html")  # 保存为html文件

import math
from datetime import datetime, timedelta

import folium
from folium.plugins import TimestampedGeoJson


def str2datetime(s):
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")


def haversine(lon1, lat1, lon2, lat2):
    # Radius of the Earth in kilometers
    R = 6371.0
    # Convert coordinates from degrees to radians
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

    # Difference in coordinates
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    # Haversine formula
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distance in kilometers
    distance = R * c
    return distance


def generate_time_range(beg, end, t):
    result = []
    current_time = beg
    time_delta = timedelta(minutes=t)

    while current_time <= end:
        result.append(current_time)
        current_time += time_delta
    return result


def generate_folium_map(formatted_data, mmsi):
    m = folium.Map(location=[29.7450467, 122.17775], zoom_start=12)
    features = []

    for i, row in enumerate(formatted_data):
        print(row)
        print(formatted_data[i])
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [row[1], row[2]] if len(row) != 6 else [row[2],row[3]],
            },
            'properties': {
                'time': row[0].isoformat() if len(row) !=6 else row[1].isoformat(),
                'style': {'color': 'blue' if row[0] == mmsi else 'red'},
                'icon': 'circle',
                'iconstyle': {
                    'fillColor': 'blue' if row[0] == mmsi else 'red',
                    'fillOpacity': 0.6,
                    'stroke': 'true',
                    'radius': 5
                }
            }
        }
        features.append(feature)

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

    return m._repr_html_()


def relative_velocity(spd1, hed1, spd2, hed2):
    # 计算船1的速度分量
    v1x = spd1 * math.cos(math.radians(hed1))
    v1y = spd1 * math.sin(math.radians(hed1))
    # 计算船2的速度分量
    v2x = spd2 * math.cos(math.radians(hed2))
    v2y = spd2 * math.sin(math.radians(hed2))
    # 计算相对速度
    v_rel_x = v2x - v1x
    v_rel_y = v2y - v1y
    return v_rel_x, v_rel_y

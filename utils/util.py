import math
from datetime import datetime, timedelta

import folium
from folium.plugins import TimestampedGeoJson

import model.AISMap


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
    """
    Generate a list of datetime values between beg and end, spaced by t minutes.

    :param beg: Start datetime.
    :param end: End datetime.
    :param t: Interval in minutes.
    :return: List of datetime values spaced by t minutes.
    """
    result = []
    current_time = beg
    time_delta = timedelta(minutes=t)

    while current_time <= end:
        result.append(current_time)
        current_time += time_delta

    return result


def show_trace_service(data, mmsi):
    # Ensure timestamps are in datetime format
    formatted_data = []
    for row in data:
        # Convert timestamp to datetime format
        ts = str2datetime(row[1])
        formatted_data.append((row[0], ts, row[2], row[3]))  # mmsi, ts, lon, lat

    # Create Folium map centered on a default location
    m = folium.Map(location=[29.7450467, 122.17775], zoom_start=12)

    # Create an empty GeoJSON feature collection
    features = []

    for i, row in enumerate(formatted_data):
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [row[2], row[3]],
            },
            'properties': {
                'time': row[1].isoformat(),
                'style': {'color': 'blue'},
                'icon': 'circle',
                'iconstyle': {
                    'fillColor': 'blue',
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


def show_conj_trace_service(data, mmsi1, mmsi2):
    # Ensure timestamps are in datetime format
    formatted_data = []
    for row in data:
        # Convert timestamp to datetime format
        ts = str2datetime(row[1])
        formatted_data.append((row[0], ts, row[2], row[3]))  # mmsi, ts, lon, lat

    # Create Folium map centered on a default location
    m = folium.Map(location=[29.7450467, 122.17775], zoom_start=12)

    # Create an empty GeoJSON feature collection
    features = []

    for i, row in enumerate(formatted_data):
        print(row[1], row[1].isoformat())

        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [row[2], row[3]],
            },
            'properties': {
                'time': row[1].isoformat(),
                'style': {'color': 'blue' if row[0] == mmsi1 else 'red'},
                'icon': 'circle',
                'iconstyle': {
                    'fillColor': 'blue' if row[0] == mmsi1 else 'red',
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

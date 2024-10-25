import folium
from folium.plugins import TimestampedGeoJson

import model
import utils

def generate_trace_range(ship:model.Ship.Ship,t=0.5):
    traces = [[trace.ts,trace.lat, trace.lon] for trace in ship.traces]
    beg = traces[0][0]
    end = traces[-1][0]
    sheet = []
    ts_range = utils.util.generate_time_range(beg, end, t)
    for i in ts_range:
        trace = ship.get_nearest_trace(i)
        if trace is not None:
            lat = trace[1]
            lon = trace[2]
            sheet.append([i,lat,lon])
    return sheet


def show_trace_service(data,mmsi):
    # Ensure timestamps are in datetime format
    ship = model.Ship.Ship(mmsi)
    for row in data:
        # Convert timestamp to datetime format
        ts = utils.util.str2datetime(row[1])
        ship.add_trace(model.ShipPoint.ShipPoint(ts,row[2],row[3],None,None))

    formatted_data = generate_trace_range(ship)
    # Create Folium map centered on a default location
    m = folium.Map(location=[29.7450467, 122.17775], zoom_start=12)

    # Create an empty GeoJSON feature collection
    features = []

    for i, row in enumerate(formatted_data):
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [row[1], row[2]],
            },
            'properties': {
                'time': row[0].isoformat(),
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



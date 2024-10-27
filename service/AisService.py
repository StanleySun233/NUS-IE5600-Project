import itertools

from numpy.ma.core import resize

import model
import utils


def generate_trace_range(ship: model.Ship.Ship, t=0.5):
    traces = [[trace.ts, trace.lat, trace.lon] for trace in ship.traces]
    beg = traces[0][0]
    end = traces[-1][0]
    sheet = []
    ts_range = utils.util.generate_time_range(beg, end, t)
    for i in ts_range:
        trace = ship.get_nearest_trace(i)
        if trace is not None:
            lat = trace[1]
            lon = trace[2]
            sheet.append([i, lat, lon])
    return sheet


def show_trace_service(data, mmsi):
    # Ensure timestamps are in datetime format
    ship = model.Ship.Ship(mmsi)
    for row in data:
        # Convert timestamp to datetime format
        ts = utils.util.str2datetime(row[1])
        ship.add_trace(model.ShipPoint.ShipPoint(ts, row[2], row[3], None, None))

    formatted_data = generate_trace_range(ship)
    return utils.util.generate_folium_map(formatted_data, mmsi)


def show_conj_trace_service(data, mmsi1, mmsi2):
    ship1 = model.Ship.Ship(mmsi1)
    ship2 = model.Ship.Ship(mmsi2)
    for row in data:
        # Convert timestamp to datetime format
        ts = utils.util.str2datetime(row[1])
        if row[0] == mmsi1:
            ship1.add_trace(model.ShipPoint.ShipPoint(ts, row[2], row[3], None, None))
        else:
            ship2.add_trace(model.ShipPoint.ShipPoint(ts, row[2], row[3], None, None))

    formatted_data = [[mmsi1] + i for i in generate_trace_range(ship1, t=0.5)] + [[mmsi2] + i for i in
                                                                                  generate_trace_range(ship2, t=0.5)]

    return utils.util.generate_folium_map(formatted_data, mmsi1)


def check_is_collision(data, distance,date):
    sheet = {}
    amap = model.AISMap.AisMap()
    for row in data:
        if row[0] not in sheet:
            sheet[row[0]] = model.Ship.Ship(row[0])
        sheet[row[0]].add_trace(model.ShipPoint.ShipPoint(*row[1:]))

    amap.data = {key: value for key, value in sheet.items() if len(value.traces) >= 500}
    result = []

    for i, j in itertools.combinations(amap.data.keys(), 2):
        is_collision = amap.is_collapse(i, j)
        if is_collision <= distance:
            result.append({'mmsi1': i, 'mmsi2': j, 'distance': round(is_collision, 2),'date':date})
    return result

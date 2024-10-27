import itertools
from datetime import datetime, timedelta
from geopy.distance import geodesic
import model
import plot.ship_encounter
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
            speed = trace[3]
            heading = trace[4]
            sheet.append([i, lat, lon,speed,heading])
    return sheet

def generate_trace_range_by_date(ship: model.Ship.Ship,date,t=0.5):
    beg = date-timedelta(minutes=10)
    end = date+timedelta(minutes=10)
    sheet = []
    ts_range = utils.util.generate_time_range(beg, end, t)
    for i in ts_range:
        trace = ship.get_nearest_trace(i)
        if trace is not None:
            lat = trace[1]
            lon = trace[2]
            speed = trace[3]
            heading = trace[4]
            sheet.append([i, lat, lon,speed,heading])
    return sheet

def clear_data(sheet):
    # 设置阈值
    MAX_SPEED = 40  # 单位为节
    MAX_ACCELERATION = 10  # 单位为节/秒
    MAX_HEADING_CHANGE = 45  # 最大允许的方向变化
    MAX_DISTANCE = 0.20  # 单位为公里

    # 用于存储清理后的数据
    filtered_data = []

    # 读取轨迹点数据
    for i in range(1, len(sheet)):
        prev = sheet[i - 1]
        curr = sheet[i]

        # 时间差
        time_diff = (curr[0] - prev[0]).total_seconds()
        if time_diff == 0:
            continue  # 跳过重复的时间点

        # 速度检查
        if curr[3] < 0 or curr[3] > MAX_SPEED:
            continue  # 剔除速度异常的点

        # 加速度检查
        acceleration = abs(curr[3] - prev[3]) / time_diff
        if acceleration > MAX_ACCELERATION:
            continue  # 剔除加速度异常的点

        # 方向变化检查
        heading_change = abs(curr[4] - prev[4])
        if heading_change > MAX_HEADING_CHANGE:
            continue  # 剔除方向突变的点

        # 距离检查
        distance = geodesic((prev[1], prev[2]), (curr[1], curr[2])).km
        if distance > MAX_DISTANCE:
            continue  # 剔除距离异常的点

        # 如果通过所有检查，保留该点
        filtered_data.append(curr)

    return filtered_data


def show_trace_service(data, mmsi):
    # Ensure timestamps are in datetime format
    ship = model.Ship.Ship(mmsi)
    for row in data:
        # Convert timestamp to datetime format
        ts = utils.util.str2datetime(row[1])
        ship.add_trace(model.ShipPoint.ShipPoint(ts, row[2], row[3], None, None))

    formatted_data = generate_trace_range(ship)
    return utils.util.generate_folium_map(formatted_data, mmsi)


def show_plot_detail(data,mmsi1,mmsi2,file):
    ship1 = model.Ship.Ship(mmsi1)
    ship2 = model.Ship.Ship(mmsi2)
    for row in data:
        # Convert timestamp to datetime format
        ts = utils.util.str2datetime(row[1])
        if row[0] == mmsi1:
            ship1.add_trace(model.ShipPoint.ShipPoint(ts, row[2], row[3], row[4], row[5]))
        else:
            ship2.add_trace(model.ShipPoint.ShipPoint(ts, row[2], row[3], row[4], row[5]))

    amap = model.AISMap.AisMap()
    amap.data = {mmsi1:ship1, mmsi2:ship2}
    is_collision, encounter, ts = amap.is_collapse(mmsi1,mmsi2)
    date = ts
    plot.ship_encounter.plot_encounter_video(ship1,ship2,date,file)

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
        is_collision,encounter,ts = amap.is_collapse(i, j)
        if is_collision <= distance:
            result.append({'mmsi1': i, 'mmsi2': j, 'distance': round(is_collision, 2),'date':date,'encounter':encounter,'ts':ts})
    return result
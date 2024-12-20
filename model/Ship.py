from datetime import datetime
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

import model.ShipPoint
import utils.Cubic
from model.ShipPoint import ShipPoint


class Ship:
    def __init__(self, mmsi):
        self.mmsi = mmsi
        self.traces = []

    def add_trace(self, shipPoint: model.ShipPoint.ShipPoint):
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

    def add_traces(self, shipPoints: List[model.ShipPoint.ShipPoint]):
        for i in shipPoints:
            self.add_trace(i)

    def get_nearest_trace(self, ts: datetime, n=5, iter=utils.Cubic.Pchip, plots=False):
        # Step 1: Check if ts is within the time range of the traces
        if not self.traces:
            return None

        times = [trace.ts for trace in self.traces]
        if ts < times[0] or ts > times[-1]:
            return None

        # Step 2: Find the n points before and n points after the given ts
        traces_before = [trace for trace in self.traces if trace.ts <= ts]
        traces_after = [trace for trace in self.traces if trace.ts > ts]

        # if len(traces_before) < n or len(traces_after) < n:
        #     return None  # Not enough points for interpolation

        # Get the n closest points before and after
        closest_traces = traces_before[-n:] + traces_after[:n]
        # Extract the time, lat, lon, speed, and heading for the selected points
        times_nearest = [trace.ts.timestamp() for trace in closest_traces]
        lats = [trace.lat for trace in closest_traces]
        lons = [trace.lon for trace in closest_traces]
        speeds = [trace.speed for trace in closest_traces if trace.speed is not None]
        headings = [trace.heading for trace in closest_traces if trace.heading is not None]

        if len(speeds) == 0:
            speeds = [1]
        if len(headings) == 0:
            headings = [1]

        # Step 3: Fit cubic splines for lat, lon, speed, and heading
        # print(times_nearest)
        try:
            spline_lat = iter(times_nearest, lats)
            spline_lon = iter(times_nearest, lons)
            spline_speed = iter(times_nearest, speeds)
            spline_heading = iter(times_nearest, headings)
            # Step 4: Evaluate the splines at the given time ts
            ts_timestamp = ts.timestamp()
            lat_interp = spline_lat(ts_timestamp)
            lon_interp = spline_lon(ts_timestamp)
            speed_interp = spline_speed(ts_timestamp)
            heading_interp = spline_heading(ts_timestamp)
        except:
            ts_timestamp = ts.timestamp()
            lat_interp = sum(lats) / len(lats)
            lon_interp = sum(lons) / len(lons)
            speed_interp = sum(speeds) / len(speeds)
            heading_interp = sum(headings) / len(headings)

        # Return the interpolated values as a list [ts, lon, lat, speed, heading]
        if plots:
            pred_ts = np.linspace(min(times_nearest), max(times_nearest), 10)
            lat_pred = [spline_lat(i) for i in pred_ts]
            lon_pred = [spline_lon(i) for i in pred_ts]
            plt.plot(lon_pred, lat_pred, label='time-series line')
            plt.scatter(lons, lats, label='used')
            plt.scatter(sum(lons) / len(lons), sum(lats) / len(lats), label='mean')

            spline_lat_linear = interp1d(times_nearest, lats, kind='linear', fill_value="extrapolate")
            spline_lon_linear = interp1d(times_nearest, lons, kind='linear', fill_value="extrapolate")
            lat_interp_linear = spline_lat_linear(ts_timestamp)
            lon_interp_linear = spline_lon_linear(ts_timestamp)
            plt.scatter(lon_interp_linear, lat_interp_linear, label='linear')

            spline_lat_nearest = interp1d(times_nearest, lats, kind='nearest', fill_value="extrapolate")
            spline_lon_nearest = interp1d(times_nearest, lons, kind='nearest', fill_value="extrapolate")
            lat_interp_linear = spline_lat_nearest(ts_timestamp)
            lon_interp_linear = spline_lon_nearest(ts_timestamp)
            plt.scatter(lon_interp_linear, lat_interp_linear, label='nearest')

        return [ts, lon_interp, lat_interp, speed_interp, heading_interp]

    def plot_trace(self, show=True):
        lat = [i.lat for i in self.traces]
        lon = [i.lon for i in self.traces]
        plt.scatter(lon, lat, alpha=0.5, label='origin')
        if show:
            plt.show()


if __name__ == "__main__":
    ais_df = pd.read_csv('../data/ais.csv')
    ais_df = ais_df[ais_df["mmsi"] == 414350530].head(100).values.tolist()
    ship = Ship(414350530)
    for i in ais_df:
        trace = ShipPoint(*i[1:])
        ship.add_trace(trace)
    print(ship.traces[20])
    dt = utils.util.str2datetime('2021-05-06 14:18:51')
    add = ship.get_nearest_trace(dt, plots=True)
    print(add)
    ship.plot_trace(False)
    if add:
        plt.scatter(add[1], add[2], label='Pchip')
    plt.legend()
    plt.show()
    print([i[1] for i in ais_df])

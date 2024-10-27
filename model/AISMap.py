from datetime import datetime
import model
import model.ShipPoint
import utils.CsvReader
import model.Ship
import model.ShipPoint


class AisMap():
    def __init__(self):
        self.data = {}
        self.collapse = []

    def add_ship(self, mmsi):
        self.data[mmsi] = model.Ship.Ship(mmsi)

    def print_ship_line(self, mmsi):
        pass

    def is_collapse(self, mmsi1, mmsi2, date=None, distance=0.2, t=0.5):
        ship1: model.Ship.Ship = self.data[mmsi1]
        ship2: model.Ship.Ship = self.data[mmsi2]
        stss = [1000, 'None', datetime.today().strftime('%Y-%m-%d %H:%M:%S')]
        traces1 = [trace for trace in ship1.traces]
        traces2 = [trace for trace in ship2.traces]

        beg = max([traces1[0].ts, traces2[0].ts])
        end = min([traces1[-1].ts, traces2[-1].ts])
        ts_range = utils.util.generate_time_range(beg, end, t)
        traces1 = [trace for trace in traces1 if beg <= trace.ts <= end]
        traces2 = [trace for trace in traces2 if beg <= trace.ts <= end]
        sp1 = model.Ship.Ship(mmsi1)
        sp2 = model.Ship.Ship(mmsi2)
        sp1.add_traces(traces1)
        sp2.add_traces(traces2)
        sheet = []
        for i in ts_range:
            t1 = sp1.get_nearest_trace(i)
            t2 = sp2.get_nearest_trace(i)
            if t1 is not None and t2 is not None:
                sp1lat = t1[1]
                sp1lon = t1[2]
                sp1hed = t1[4]
                sp2lat = t2[1]
                sp2lon = t2[2]
                sp2hed = t2[4]

                sheet.append([i, sp1lat, sp1lon, sp2lat, sp2lon])
                dist = utils.util.haversine(sp1lon, sp1lat, sp2lon, sp2lat)
                if dist < stss[0]:
                    stss[0] = dist
                    stss[1] = self.encounter_type(sp1hed, sp2hed)
                    stss[2] = i
        return stss

    def encounter_type(self, sp1hed, sp2hed):
        heading_diff = abs(sp1hed - sp2hed)

        if 170 < heading_diff < 190:
            return "Head-on Situation"
        elif 70 < heading_diff < 110:
            return "Crossing Situation"
        elif heading_diff < 20 or heading_diff > 340:
            return "Overtaking Situation"
        elif 10 <= heading_diff <= 30:
            return "Parallel Running Situation"
        else:
            return "Converging Situation"


def create_ais_map(path):
    ais_df = utils.CsvReader.CSVReader(path)
    ais_map = AisMap()

    for i in range(len(ais_df)):
        ais_df.data[i][2] = float(ais_df.data[i][2])
        ais_df.data[i][3] = float(ais_df.data[i][3])
        ais_df.data[i][4] = float(ais_df.data[i][4])
        ais_df.data[i][5] = float(ais_df.data[i][5])

    for i in ais_df.get_unique_by_col("mmsi"):
        ais_map.add_ship(i)

    for i in range(len(ais_df)):
        trace = model.ShipPoint.ShipPoint(*ais_df.get_row(i)[1:])
        ais_map.data[ais_df.get_row(i)[0]].add_trace(trace)

    return ais_map


if __name__ == '__main__':
    ais_map = create_ais_map("../data/test.csv")
    print(ais_map.data.keys())
    print(ais_map.is_collapse("412415970", "413457740", "2021-05-05"))

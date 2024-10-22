from typing import List

from ShipPoint import ShipPoint
# Ship 类定义
class Ship:
    def __init__(self, mmsi):
        self.mmsi = mmsi
        self.traces = []

    def add_trace(self, shipPoint: ShipPoint):
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

    def add_traces(self,shipPoints:List[ShipPoint]):
        for i in shipPoints:
            self.add_trace(i)
from datetime import datetime
from utils import util


class ShipPoint:
    def __init__(self, ts, lon, lat, speed, heading):
        self.ts = util.str2datetime(ts)
        self.lon = lon
        self.lat = lat
        self.speed = speed
        self.heading = heading

    def __repr__(self):
        return (f"ShipPoint(timestamp={self.ts}, "
                f"longitude={self.lon}, latitude={self.lat}, "
                f"speed={self.speed}, heading={self.heading})")

    def __lt__(self, other):
        return self.ts < other.ts

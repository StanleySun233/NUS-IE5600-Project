import utils.util


class ShipPoint:
    def __init__(self, ts, lon, lat, speed, heading):
        try:
            self.ts = utils.util.str2datetime(ts)
        except:
            self.ts = ts
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

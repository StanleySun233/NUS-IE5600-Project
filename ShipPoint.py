from django.utils.datetime_safe import datetime


class ShipPoint:
    def __init__(self, ts, lon, lat, speed, course, heading):
        self.ts = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
        self.lon = lon
        self.lat = lat
        self.speed = speed
        self.course = course
        self.heading = heading

    def __repr__(self):
        """
        返回对象的字符串表示形式，便于打印。
        """
        return (f"ShipPoint(timestamp={self.ts}, "
                f"longitude={self.lon}, latitude={self.lat}, "
                f"speed={self.speed}, course={self.course}, heading={self.heading})")

    def __lt__(self, other):
        # 比较 ShipPoint 对象的时间，确保堆按时间顺序排列
        return self.ts < other.ts
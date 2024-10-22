import math
from datetime import datetime, timedelta

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
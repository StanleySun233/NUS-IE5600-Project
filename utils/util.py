from datetime import datetime


def str2datetime(s):
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
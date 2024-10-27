import plot
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

def plot_rotated_rectangle(lat, lon, heading, a, b,ax):
    # 创建 Rectangle 对象，设置其中心位置和旋转角度
    rectangle = Rectangle(
        (lon - a / 2, lat - b / 2),  # 左下角坐标
        a,  # 长度
        b,  # 宽度
        angle=heading,  # 旋转角度
        linewidth=1,
        edgecolor='blue',
        facecolor='lightblue',
        alpha=0.6
    )
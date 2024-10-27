import os
import sqlite3
from datetime import datetime

import cv2
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.transforms import Affine2D

import model
import utils.util
import service
import matplotlib.ticker as ticker
import math


def plot_encounter(ship1, ship2, date):
    mmsi1, mmsi2 = ship1.mmsi, ship2.mmsi
    # Clean and generate trajectory data
    trace_data1 = [[mmsi1] + i for i in service.AisService.generate_trace_range_by_date(ship1, date)]
    trace_data2 = [[mmsi2] + i for i in service.AisService.generate_trace_range_by_date(ship2, date)]

    lat1 = [i[2] for i in trace_data1]
    lon1 = [i[3] for i in trace_data1]
    hed1 = [i[5] for i in trace_data1]
    lat2 = [i[2] for i in trace_data2]
    lon2 = [i[3] for i in trace_data2]
    hed2 = [i[5] for i in trace_data2]
    prediction_distance = 0.005
    ship_length = 0.0025  # 船的长
    ship_width = 0.001  # 船的宽

    for i in range(len(trace_data1)):
        plt.gca().xaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))
        plt.gca().yaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))

        # 绘制两艘船的轨迹点
        plt.scatter(lon1[:i + 1], lat1[:i + 1], label=mmsi1, color='lightblue')
        plt.scatter(lon2[:i + 1], lat2[:i + 1], label=mmsi2, color='pink')

        # 计算船1的预测点
        end_lon1 = lon1[i] + prediction_distance * math.cos(math.radians(hed1[i] + 180))
        end_lat1 = lat1[i] + prediction_distance * math.sin(math.radians(hed1[i] + 180))
        plt.plot([lon1[i], end_lon1], [lat1[i], end_lat1], linestyle='--', color='blue')

        # 计算船2的预测点
        end_lon2 = lon2[i] + prediction_distance * math.cos(math.radians(hed2[i] + 180))
        end_lat2 = lat2[i] + prediction_distance * math.sin(math.radians(hed2[i] + 180))
        plt.plot([lon2[i], end_lon2], [lat2[i], end_lat2], linestyle='--', color='red')

        # 添加船1的长方体表示，并旋转角度
        rect1 = Rectangle(
            (-ship_length / 2, -ship_width / 2),  # 矩形的起点（相对位置）
            ship_length,
            ship_width,
            color='blue',
            alpha=0.5
        )
        # 使用 Affine2D 实现旋转和平移
        transform1 = (Affine2D()
                      .rotate_deg(hed1[i])  # 旋转到航向角度
                      .translate(lon1[i], lat1[i])  # 平移到当前位置
                      + plt.gca().transData)
        rect1.set_transform(transform1)
        plt.gca().add_patch(rect1)

        # 添加船2的长方体表示，并旋转角度
        rect2 = Rectangle(
            (-ship_length / 2, -ship_width / 2),  # 矩形的起点（相对位置）
            ship_length,
            ship_width,
            color='red',
            alpha=0.5
        )
        transform2 = (Affine2D()
                      .rotate_deg(hed2[i])  # 旋转到航向角度
                      .translate(lon2[i], lat2[i])  # 平移到当前位置
                      + plt.gca().transData)
        rect2.set_transform(transform2)
        plt.gca().add_patch(rect2)

        # 添加图例和展示
        plt.legend()
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.title(f"Simulation of Ship Collision")
        plt.show()


def plot_encounter_video(ship1, ship2, date, output_filename="ship_encounter.mp4"):
    mmsi1, mmsi2 = ship1.mmsi, ship2.mmsi
    trace_data1 = [[mmsi1] + i for i in service.AisService.generate_trace_range_by_date(ship1, date)]
    trace_data2 = [[mmsi2] + i for i in service.AisService.generate_trace_range_by_date(ship2, date)]

    lat1 = [i[2] for i in trace_data1]
    lon1 = [i[3] for i in trace_data1]
    hed1 = [i[5] for i in trace_data1]
    lat2 = [i[2] for i in trace_data2]
    lon2 = [i[3] for i in trace_data2]
    hed2 = [i[5] for i in trace_data2]
    prediction_distance = 0.005
    ship_length = 0.0025
    ship_width = 0.001

    # 设置视频参数
    frame_width, frame_height = 1920, 1080
    fps = 5
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_filename, fourcc, fps, (frame_width, frame_height))

    temp_dir = "frames"
    os.makedirs(temp_dir, exist_ok=True)  # 创建临时文件夹存放帧图片

    for i in range(len(trace_data1)):
        fig, ax = plt.subplots(figsize=(19.2, 10.8))
        ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))
        ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))

        # 绘制轨迹
        ax.scatter(lon1[:i + 1], lat1[:i + 1], label=f"Ship {mmsi1}", color='lightblue')
        ax.scatter(lon2[:i + 1], lat2[:i + 1], label=f"Ship {mmsi2}", color='pink')

        # 绘制预测点
        end_lon1 = lon1[i] + prediction_distance * math.cos(math.radians(hed1[i]))
        end_lat1 = lat1[i] + prediction_distance * math.sin(math.radians(hed1[i]))
        ax.plot([lon1[i], end_lon1], [lat1[i], end_lat1], linestyle='--', color='blue')

        end_lon2 = lon2[i] + prediction_distance * math.cos(math.radians(hed2[i]))
        end_lat2 = lat2[i] + prediction_distance * math.sin(math.radians(hed2[i]))
        ax.plot([lon2[i], end_lon2], [lat2[i], end_lat2], linestyle='--', color='red')

        # 绘制船的矩形
        rect1 = Rectangle(
            (-ship_length / 2, -ship_width / 2),
            ship_length,
            ship_width,
            color='blue',
            alpha=0.5
        )
        transform1 = (Affine2D()
                      .rotate_deg(hed1[i])
                      .translate(lon1[i], lat1[i])
                      + ax.transData)
        rect1.set_transform(transform1)
        ax.add_patch(rect1)

        rect2 = Rectangle(
            (-ship_length / 2, -ship_width / 2),
            ship_length,
            ship_width,
            color='red',
            alpha=0.5
        )
        transform2 = (Affine2D()
                      .rotate_deg(hed2[i])
                      .translate(lon2[i], lat2[i])
                      + ax.transData)
        rect2.set_transform(transform2)
        ax.add_patch(rect2)

        # 设置图例和标签
        ax.legend()
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.set_title("Simulation of Ship Collision")

        # 保存图像
        frame_path = f"{temp_dir}/frame_{i:03d}.png"
        plt.savefig(frame_path)
        plt.close(fig)

        # 读取保存的图像并写入视频
        frame = cv2.imread(frame_path)
        img_resized = cv2.resize(frame, (frame_width, frame_height))
        out.write(img_resized)

    # 释放视频资源
    out.release()

    # 删除临时帧文件
    for file in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, file))
    os.rmdir(temp_dir)

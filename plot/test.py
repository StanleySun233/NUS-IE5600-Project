import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import cv2
from matplotlib.patches import Wedge, Rectangle
import model.Ship
import service.AisService

# Connect to SQLite database and fetch data
conn = sqlite3.connect('../data/ais.db')
cursor = conn.cursor()

mmsi = '412356358'  # Target MMSI
date_filter = '2021-05-05'  # Target date
query = """
SELECT ts, lat, lon, speed, heading
FROM ais 
WHERE mmsi = ? AND DATE(ts) = ?
ORDER BY ts
"""
cursor.execute(query, (mmsi, date_filter))
data = cursor.fetchall()
conn.close()

# Load trajectory data
ship = model.Ship.Ship(mmsi)
for record in data:
    ship.add_trace(model.ShipPoint.ShipPoint(*record))

# Clean and generate trajectory data
trace_data = service.AisService.generate_trace_range(ship)
cleaned_data = service.AisService.clear_data(trace_data)[:300]

# Extract cleaned data
time = [i[0] for i in cleaned_data]  # Time
lat = [i[1] for i in cleaned_data]  # Latitude
lon = [i[2] for i in cleaned_data]  # Longitude
speed = [i[3] for i in cleaned_data]  # Speed
heading = [i[4] for i in cleaned_data]  # Heading

# Set video save parameters
fps = 20
video_name = 'ship_trajectory_with_safety_zones.mp4'
frame_size = (800, 600)
out = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'mp4v'), fps, frame_size)

# Set up the plot
fig, ax = plt.subplots(figsize=(8, 6))
ax.set_xlim(min(lon) - 0.01, max(lon) + 0.01)
ax.set_ylim(min(lat) - 0.01, max(lat) + 0.01)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_title(f"Ship {mmsi} Trajectory Plot")

# Generate and save frames sequentially
for frame in range(len(time)):
    ax.clear()
    ax.set_xlim(min(lon) - 0.01, max(lon) + 0.01)
    ax.set_ylim(min(lat) - 0.01, max(lat) + 0.01)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

    # Plot trajectory up to the current frame
    ax.plot(lon[:frame + 1], lat[:frame + 1], 'bo-', markersize=3, linewidth=0.5, label='Trajectory')
    ax.plot(lon[frame], lat[frame], 'ro', markersize=5, label='Current Position')  # Current frame position

    # Draw half-circle safety zones at the bow and stern
    safety_radius = 0.002  # Safety distance radius
    heading_rad = np.radians(heading[frame])

    # Bow half-circle (safety zone)
    bow_circle = Wedge(
        (lon[frame], lat[frame]),
        safety_radius,
        np.degrees(heading_rad - np.pi / 4),
        np.degrees(heading_rad + np.pi / 4),
        color='red',
        alpha=0.3
    )
    ax.add_patch(bow_circle)

    # Stern half-circle (safety zone)
    stern_circle = Wedge(
        (lon[frame] - 0.0005 * np.cos(heading_rad), lat[frame] - 0.0005 * np.sin(heading_rad)),
        safety_radius,
        np.degrees(heading_rad + 3 * np.pi / 4),
        np.degrees(heading_rad - 3 * np.pi / 4),
        color='blue',
        alpha=0.3
    )
    ax.add_patch(stern_circle)

    # Draw rectangular ship body
    a = 0.005 # Ship length
    b = 0.0015  # Ship width

    # 转换角度为弧度
    theta = np.radians(heading[frame])

    # 矩形的四个顶点（未旋转前，以中心为 (0, 0)）
    corners = np.array([
        [-a / 2, -b / 2],
        [a / 2, -b / 2],
        [a / 2, b / 2],
        [-a / 2, b / 2],
    ])

    # 旋转矩阵
    rotation_matrix = np.array([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta), np.cos(theta)]
    ])

    # 旋转后的顶点
    rotated_corners = corners @ rotation_matrix.T

    # 平移到 (lat, lon) 位置
    rotated_corners[:, 0] += lon[frame]
    rotated_corners[:, 1] += lat[frame]

    ax.plot(*zip(*(rotated_corners.tolist() + [rotated_corners[0]])), '-')

    # Update legend
    ax.legend()

    # Save the current frame as an image
    plt.savefig("temp_frame.png")  # Temporarily save current frame

    # Use cv2 to read the saved frame and write it to the video
    frame_image = cv2.imread("temp_frame.png")
    frame_image = cv2.resize(frame_image, frame_size)
    out.write(frame_image)

# Release video object
out.release()
plt.close()
print(f"Video saved to {video_name}")

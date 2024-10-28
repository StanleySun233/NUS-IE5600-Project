import sqlite3

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cv2
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Wedge

import model
import service

# Connect to SQLite database and fetch data
conn = sqlite3.connect('../data/ais.db')
cursor = conn.cursor()

mmsi = '412415970'  # Target MMSI
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
cleaned_data = service.AisService.clear_data(trace_data)[:200]

# Extract data
time = [record[0] for record in cleaned_data]
lat = [record[1] for record in cleaned_data]
lon = [record[2] for record in cleaned_data]
speed = [record[3] for record in cleaned_data]
heading = [record[4] for record in cleaned_data]

# Set video save parameters
fps = 20
video_name = 'ship_trajectory_with_safety_zones.mp4'
frame_size = (1920, 1080)
out = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'mp4v'), fps, frame_size)

# 设置图形大小以匹配 1920x1080 分辨率
dpi = 100  # 每英寸点数
# 设置 Cartopy 投影的绘图
fig, ax = plt.subplots(figsize=(19.2, 10.8), subplot_kw={'projection': ccrs.PlateCarree()}, frameon=False)

# Add map background features
ax.stock_img()  # Add a global map image
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.LAND)
ax.add_feature(cfeature.OCEAN)
ax.add_feature(cfeature.LAKES)
ax.add_feature(cfeature.RIVERS)
ax.add_feature(cfeature.BORDERS, linestyle=':')
ax.add_feature(cfeature.STATES, linestyle='--')

# Set map extent to focus on ship's trajectory
ax.set_extent([min(lon) - 0.1, max(lon) + 0.1, min(lat) - 0.1, max(lat) + 0.1], crs=ccrs.PlateCarree())
# Generate and save frames sequentially
for frame in range(len(time)):
    ax.clear()

    # Re-add map background features
    ax.stock_img()
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.LAKES)
    ax.add_feature(cfeature.RIVERS)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.STATES, linestyle='--')
    ax.set_extent([min(lon) - 0.1, max(lon) + 0.1, min(lat) - 0.1, max(lat) + 0.1], crs=ccrs.PlateCarree())

    # Plot trajectory up to the current frame
    ax.plot(lon[:frame + 1], lat[:frame + 1], 'bo-', markersize=3, linewidth=0.5, transform=ccrs.PlateCarree())
    ax.plot(lon[frame], lat[frame], 'ro', markersize=5, transform=ccrs.PlateCarree(),
            label='Current Position')  # Current position

    # Draw half-circle safety zones at the bow and stern
    safety_radius = 0.01  # Safety distance radius
    heading_rad = np.radians(heading[frame])

    # Bow half-circle (safety zone)
    bow_circle = Wedge(
        (lon[frame], lat[frame]),
        safety_radius,
        np.degrees(heading_rad - np.pi / 4),
        np.degrees(heading_rad + np.pi / 4),
        color='red',
        alpha=0.3,
        transform=ccrs.PlateCarree()
    )
    ax.add_patch(bow_circle)

    # Stern half-circle (safety zone)
    stern_circle = Wedge(
        (lon[frame] - 0.0005 * np.cos(heading_rad), lat[frame] - 0.0005 * np.sin(heading_rad)),
        safety_radius,
        np.degrees(heading_rad + 3 * np.pi / 4),
        np.degrees(heading_rad - 3 * np.pi / 4),
        color='blue',
        alpha=0.3,
        transform=ccrs.PlateCarree()
    )
    ax.add_patch(stern_circle)

    # Draw rectangular ship body
    a = 0.005  # Ship length
    b = 0.0015  # Ship width
    corners = np.array([
        [-a / 2, -b / 2],
        [a / 2, -b / 2],
        [a / 2, b / 2],
        [-a / 2, b / 2]
    ])
    rotation_matrix = np.array([
        [np.cos(heading_rad), -np.sin(heading_rad)],
        [np.sin(heading_rad), np.cos(heading_rad)]
    ])
    rotated_corners = corners @ rotation_matrix.T
    rotated_corners[:, 0] += lon[frame]
    rotated_corners[:, 1] += lat[frame]

    # Plot ship rectangle
    ax.plot(*zip(*(rotated_corners.tolist() + [rotated_corners[0]])), 'k-', transform=ccrs.PlateCarree())

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

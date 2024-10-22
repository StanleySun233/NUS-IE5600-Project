from folium.plugins import TimestampedGeoJson

import utils.util

from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import folium

app = Flask(__name__)

DATABASE = './data/ais.db'


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# AIS CRUD
@app.route('/ais', methods=['GET'])
def view_ais():
    page = int(request.args.get('page', 1))
    search_mmsi = request.args.get('search_mmsi', '')
    per_page = 50
    offset = (page - 1) * per_page
    conn = get_db()
    cur = conn.cursor()

    # 计算总页数
    if search_mmsi:
        search_query = f'%{search_mmsi}%'
        cur.execute('SELECT COUNT(*) FROM ais WHERE mmsi LIKE ?', (search_query,))
    else:
        cur.execute('SELECT COUNT(*) FROM ais')

    total_items = cur.fetchone()[0]
    total_pages = (total_items + per_page - 1) // per_page  # 向上取整

    if search_mmsi:
        cur.execute('SELECT * FROM ais WHERE mmsi LIKE ? LIMIT ? OFFSET ?', (search_query, per_page, offset))
    else:
        cur.execute('SELECT * FROM ais LIMIT ? OFFSET ?', (per_page, offset))

    ais_data = cur.fetchall()
    conn.close()

    return render_template('ais.html', ais_data=ais_data, page=page, total_pages=total_pages, search_mmsi=search_mmsi)


# 新建 AIS 数据
# 新建 AIS 数据
@app.route('/create_ais', methods=['GET', 'POST'])
def create_ais():
    if request.method == 'POST':
        mmsi = request.form['mmsi']
        ts = request.form['ts']
        lon = float(request.form['lon'])
        lat = float(request.form['lat'])
        speed = float(request.form['speed'])
        heading = float(request.form['heading'])

        conn = get_db()
        cur = conn.cursor()

        # 检查 mmsi 是否存在于 ship 表中
        cur.execute('SELECT * FROM ship WHERE mmsi=?', (mmsi,))
        ship = cur.fetchone()

        if ship:
            # mmsi 存在，允许插入 AIS 数据
            cur.execute('INSERT INTO ais (mmsi, ts, lon, lat, speed, heading) VALUES (?, ?, ?, ?, ?, ?)',
                        (mmsi, ts, lon, lat, speed, heading))
            conn.commit()
            return redirect(url_for('view_ais'))
        else:
            # mmsi 不存在，询问是否创建
            return render_template('confirm_create_ship.html', mmsi=mmsi, ts=ts, lon=lon, lat=lat, speed=speed,
                                   heading=heading)

    return render_template('create_ais.html')


# 创建 ship 并插入 AIS 数据


@app.route('/create_ship_and_ais', methods=['POST'])
def create_ship_and_ais():
    mmsi = request.form['mmsi']
    ts = request.form['ts']
    lon = float(request.form['lon'])
    lat = float(request.form['lat'])
    speed = float(request.form['speed'])
    heading = float(request.form['heading'])

    conn = get_db()
    cur = conn.cursor()

    # 先创建船舶
    cur.execute('INSERT INTO ship (mmsi) VALUES (?)', (mmsi,))

    # 再插入 AIS 数据
    cur.execute('INSERT INTO ais (mmsi, ts, lon, lat, speed, heading) VALUES (?, ?, ?, ?, ?, ?)',
                (mmsi, ts, lon, lat, speed, heading))
    conn.commit()
    conn.close()

    return redirect(url_for('view_ais'))


# 修改 AIS 数据
@app.route('/edit_ais/<int:id>', methods=['GET', 'POST'])
def edit_ais(id):
    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        mmsi = request.form['mmsi']
        ts = request.form['ts']
        lon = float(request.form['lon'])
        lat = float(request.form['lat'])
        speed = float(request.form['speed'])
        heading = float(request.form['heading'])
        cur.execute('UPDATE ais SET mmsi=?, ts=?, lon=?, lat=?, speed=?, heading=? WHERE id=?',
                    (mmsi, ts, lon, lat, speed, heading, id))
        conn.commit()
        return redirect(url_for('view_ais'))

    cur.execute('SELECT * FROM ais WHERE id=?', (id,))
    ais_data = cur.fetchone()
    conn.close()
    return render_template('edit_ais.html.html', ais=ais_data)


# 删除 AIS 数据
@app.route('/delete_ais/<int:id>', methods=['GET'])
def delete_ais(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM ais WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('view_ais'))


# Ship CRUD
@app.route('/ship', methods=['GET'])
def view_ship():
    page = int(request.args.get('page', 1))
    search_mmsi = request.args.get('search_mmsi', '')
    per_page = 50
    offset = (page - 1) * per_page
    conn = get_db()
    cur = conn.cursor()

    # 计算总页数
    if search_mmsi:
        search_query = f'%{search_mmsi}%'
        cur.execute('SELECT COUNT(DISTINCT mmsi) FROM ais WHERE mmsi LIKE ?', (search_query,))
    else:
        cur.execute('SELECT COUNT(DISTINCT mmsi) FROM ais')

    total_items = cur.fetchone()[0]
    total_pages = (total_items + per_page - 1) // per_page  # 向上取整

    if search_mmsi:
        cur.execute(
            'SELECT mmsi, MIN(ts) as start_time, MAX(ts) as end_time, COUNT(*) as count FROM ais WHERE mmsi LIKE ? GROUP BY mmsi LIMIT ? OFFSET ?',
            (search_query, per_page, offset))
    else:
        cur.execute(
            'SELECT mmsi, MIN(ts) as start_time, MAX(ts) as end_time, COUNT(*) as count FROM ais GROUP BY mmsi LIMIT ? OFFSET ?',
            (per_page, offset))

    ship_data = cur.fetchall()
    conn.close()

    return render_template('ship.html', ship_data=ship_data, page=page, total_pages=total_pages,
                           search_mmsi=search_mmsi)


# 新建船舶
@app.route('/create_ship', methods=['GET', 'POST'])
def create_ship():
    if request.method == 'POST':
        mmsi = request.form['mmsi']
        conn = get_db()
        cur = conn.cursor()
        cur.execute('INSERT INTO ship (mmsi) VALUES (?)', (mmsi,))
        conn.commit()
        conn.close()
        return redirect(url_for('view_ship'))
    return render_template('create_ship.html')


@app.route('/ship/<mmsi>', methods=['GET'])
def view_ais_by_ship(mmsi):
    return redirect(url_for('view_ais', mmsi=mmsi))


# 显示与删除 Ship 相关的 AIS 记录，并确认删除
@app.route('/delete_ship/<mmsi>', methods=['GET', 'POST'])
def delete_ship(mmsi):
    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        # 用户确认删除 Ship 和 AIS 记录
        cur.execute('DELETE FROM ais WHERE mmsi=?', (mmsi,))
        cur.execute('DELETE FROM ship WHERE mmsi=?', (mmsi,))
        conn.commit()
        conn.close()
        return redirect(url_for('view_ship'))

    # 获取与该 Ship 相关的 AIS 记录
    cur.execute('SELECT * FROM ais WHERE mmsi=?', (mmsi,))
    ais_data = cur.fetchall()
    conn.close()

    return render_template('confirm_delete_ship.html', ais_data=ais_data, mmsi=mmsi)


def show_trace(mmsi):
    conn = get_db()

    # Retrieve data from the database (timestamp, longitude, latitude for specified ships)
    cursor = conn.cursor()
    cursor.execute("SELECT mmsi, ts, lon, lat FROM ais WHERE mmsi=? ORDER BY ts", (mmsi,))
    data = cursor.fetchall()
    # Close the database connection
    conn.close()

    return utils.util.show_trace_service(data, mmsi)


@app.route('/trace/<mmsi>', methods=['GET'])
def trace_view(mmsi):
    return show_trace(mmsi)


# 查看联合轨迹
@app.route('/conjection_trace', methods=['POST', 'GET'])
def conjection_trace():
    mmsi1 = request.args.get('mmsi1', '')
    mmsi2 = request.args.get('mmsi2', '')
    date = request.args.get('date', '')
    print(mmsi1, mmsi2, date)
    conn = get_db()

    # Retrieve data from the database (timestamp, longitude, latitude for specified ships)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT mmsi, ts, lon, lat 
        FROM ais 
        WHERE mmsi IN (?, ?) AND DATE(ts) = DATE(?)
        ORDER BY ts
        """, (mmsi1, mmsi2, date))
    data = cursor.fetchall()
    # Close the database connection
    conn.close()
    return utils.util.show_conj_trace_service(data, mmsi1, mmsi2)


# 检查碰撞
def check_collapse(date, distance=0.2):
    conn = get_db()
    cur = conn.cursor()
    # 简单模拟：仅根据同一天的船舶位置计算碰撞（这里需要添加更多复杂逻辑）
    cur.execute(
        'SELECT a.mmsi as mmsi1, b.mmsi as mmsi2 FROM ais a, ais b WHERE a.ts LIKE ? AND b.ts LIKE ? AND a.mmsi != b.mmsi AND abs(a.lon - b.lon) < ? AND abs(a.lat - b.lat) < ?',
        (f'{date}%', f'{date}%', distance, distance))
    collision_data = cur.fetchall()
    conn.close()
    return collision_data


@app.route('/check_collapse', methods=['POST'])
def check_collision_view():
    date = request.form['date']
    distance = float(request.form.get('distance', 0.2))
    collision_data = check_collapse(date, distance)
    return render_template('collision.html', collision_data=collision_data)


# 首页
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        mmsi1 = request.form['mmsi1']
        mmsi2 = request.form['mmsi2']
        date = request.form['date']
        distance = float(request.form.get('distance', 0.2))
        return redirect(url_for('conjection_trace', mmsi1=mmsi1, mmsi2=mmsi2, date=date))
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

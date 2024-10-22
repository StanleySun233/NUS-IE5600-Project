from flask import Flask, render_template, request, redirect, url_for
import sqlite3

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
    mmsi_filter = request.args.get('mmsi')
    per_page = 50
    offset = (page - 1) * per_page
    conn = get_db()
    cur = conn.cursor()

    if mmsi_filter:
        cur.execute('SELECT * FROM ais WHERE mmsi=? LIMIT ? OFFSET ?', (mmsi_filter, per_page, offset))
    else:
        cur.execute('SELECT * FROM ais LIMIT ? OFFSET ?', (per_page, offset))

    ais_data = cur.fetchall()
    conn.close()
    return render_template('ais.html', ais_data=ais_data, page=page)


# Ship CRUD
@app.route('/ship', methods=['GET'])
def view_ship():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT mmsi, MIN(ts) as start_time, MAX(ts) as end_time, COUNT(*) as count FROM ais GROUP BY mmsi')
    ship_data = cur.fetchall()
    conn.close()
    return render_template('ship.html', ship_data=ship_data)


@app.route('/ship/<mmsi>', methods=['GET'])
def view_ais_by_ship(mmsi):
    return redirect(url_for('view_ais', mmsi=mmsi))


# 查看轨迹
def show_trace(mmsi):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM ais WHERE mmsi=?', (mmsi,))
    traces = cur.fetchall()
    conn.close()
    # 生成轨迹的HTML表示
    trace_html = f"<h1>轨迹 for {mmsi}</h1>"
    for trace in traces:
        trace_html += f"<p>{trace['ts']} - Lon: {trace['lon']}, Lat: {trace['lat']}, Speed: {trace['speed']}, Heading: {trace['heading']}</p>"
    return trace_html


@app.route('/trace/<mmsi>', methods=['GET'])
def trace_view(mmsi):
    return show_trace(mmsi)


# 查看联合轨迹
@app.route('/conjection_trace', methods=['POST','GET'])
def conjection_trace():
    mmsi1 = request.form['mmsi1']
    mmsi2 = request.form['mmsi2']
    date = request.form['date']
    return f"<h1>联合轨迹 for {mmsi1} and {mmsi2} on {date}</h1>"


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
    app.run(debug=True)

from flask import Flask, jsonify, request, render_template
import datetime
import sqlite3

app = Flask(__name__)


# 假设已经有数据库连接代码
def fetch_ais_data(date):
    conn = sqlite3.connect('./data/ais.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM ais WHERE ts = '{date}' AND mmsi IN (SELECT mmsi FROM ais GROUP BY mmsi HAVING COUNT(*) > 100)"
    query = f""" SELECT *
FROM ais
WHERE ts BETWEEN DATETIME('{date}', '-10 minutes') AND DATETIME('{date}', '+10 minutes')
AND mmsi IN (
    SELECT mmsi 
    FROM ais 
    GROUP BY mmsi 
    HAVING COUNT(*) > 100
)
ORDER BY ABS(strftime('%s', ts) - strftime('%s', '{date}'))
LIMIT 1; """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows


@app.route('/fetch_data', methods=['GET'])
def fetch_data():
    global current_date
    date = request.args.get('date')
    ais_data = fetch_ais_data(date)
    current_date = date
    # 转化为JSON格式返回给前端
    return jsonify(ais_data)


@app.route('/update_map', methods=['GET'])
def update_map():
    time_step = int(request.args.get('time_step'))
    # date = request.args.get('date')
    date = current_date
    print(date)
    print(time_step)
    # 根据时间步长和日期获取相应的AIS数据
    timestamp = datetime.datetime.strptime(date, "%Y-%m-%d") + datetime.timedelta(minutes=time_step)
    print(timestamp)
    ais_data = fetch_ais_data(timestamp.strftime("%Y-%m-%d %H:%M:%S"))

    # 返回船舶最新位置
    return jsonify(ais_data)


@app.route("/", methods=['GET'])
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)

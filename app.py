import service.AisService
from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3

app = Flask(__name__)

DATABASE = './data/ais.db'


def get_db():
    """
    Establishes a connection to the SQLite database and sets the row factory to
    return rows as dictionaries for easy access to column names.
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# AIS CRUD operations
@app.route('/ais', methods=['GET'])
def view_ais():
    """
    Retrieves AIS data with pagination and optional search by MMSI.
    - Retrieves 'page' and 'search_mmsi' parameters from request args.
    - Calculates pagination offset based on current page.
    - Executes SQL query to count total records and determine the total number of pages.
    - Executes SQL query to fetch AIS records with pagination, applying search filter if provided.
    - Closes database connection and renders AIS data in the 'ais.html' template.
    """
    page = int(request.args.get('page', 1))
    mmsi = request.args.get('mmsi', '')
    search_mmsi = request.args.get('search_mmsi', '')
    if mmsi != '':
        search_mmsi = mmsi
    per_page = 50
    offset = (page - 1) * per_page
    conn = get_db()
    cur = conn.cursor()

    # Calculate the total number of pages
    if search_mmsi:
        search_query = f'%{search_mmsi}%'
        cur.execute('SELECT COUNT(*) FROM ais WHERE mmsi LIKE ?', (search_query,))
    else:
        cur.execute('SELECT COUNT(*) FROM ais')

    total_items = cur.fetchone()[0]
    total_pages = (total_items + per_page - 1) // per_page  # Round up

    # Fetch AIS data with pagination, applying search filter if provided
    if search_mmsi:
        cur.execute('SELECT * FROM ais WHERE mmsi LIKE ? LIMIT ? OFFSET ?', (search_query, per_page, offset))
    else:
        cur.execute('SELECT * FROM ais LIMIT ? OFFSET ?', (per_page, offset))

    ais_data = cur.fetchall()
    conn.close()

    # Render the AIS data in the 'ais.html' template with pagination info
    return render_template('ais.html', ais_data=ais_data, page=page, total_pages=total_pages, search_mmsi=search_mmsi)


# Create new AIS data
@app.route('/create_ais', methods=['GET', 'POST'])
def create_ais():
    """
    Creates a new AIS record.
    - If the request method is POST, retrieve data from the form inputs (mmsi, ts, lon, lat, speed, heading).
    - Connects to the database to check if the MMSI exists in the 'ship' table.
    - If MMSI exists, allows insertion of new AIS data for this ship.
    - If MMSI does not exist, prompts the user to confirm creation of a new ship record.
    - Redirects to 'view_ais' page after insertion or displays 'confirm_create_ship.html' template for confirmation.
    """
    if request.method == 'POST':
        mmsi = request.form['mmsi']
        ts = request.form['ts']
        lon = float(request.form['lon'])
        lat = float(request.form['lat'])
        speed = float(request.form['speed'])
        heading = float(request.form['heading'])

        conn = get_db()
        cur = conn.cursor()

        # Check if the MMSI exists in the 'ship' table
        cur.execute('SELECT * FROM ship WHERE mmsi=?', (mmsi,))
        ship = cur.fetchone()

        if ship:
            # MMSI exists, allowing insertion of AIS data
            cur.execute('INSERT INTO ais (mmsi, ts, lon, lat, speed, heading) VALUES (?, ?, ?, ?, ?, ?)',
                        (mmsi, ts, lon, lat, speed, heading))
            conn.commit()
            return redirect(url_for('view_ais'))
        else:
            # MMSI does not exist, prompts user to confirm creation
            return render_template('confirm_create_ship.html', mmsi=mmsi, ts=ts, lon=lon, lat=lat, speed=speed,
                                   heading=heading)

    return render_template('create_ais.html')


# Create a new ship and insert AIS data
@app.route('/create_ship_and_ais', methods=['POST'])
def create_ship_and_ais():
    """
    Creates a new ship record and inserts corresponding AIS data.
    - Retrieves data from the form inputs (mmsi, ts, lon, lat, speed, heading).
    - Connects to the database to first create a new ship record with the given MMSI.
    - Inserts the AIS data associated with the MMSI into the AIS table.
    - Commits changes to the database and closes the connection.
    - Redirects to the 'view_ais' page after completion.
    """
    mmsi = request.form['mmsi']
    ts = request.form['ts']
    lon = float(request.form['lon'])
    lat = float(request.form['lat'])
    speed = float(request.form['speed'])
    heading = float(request.form['heading'])

    conn = get_db()
    cur = conn.cursor()

    # First, create a new ship record
    cur.execute('INSERT INTO ship (mmsi) VALUES (?)', (mmsi,))

    # Then insert the AIS data
    cur.execute('INSERT INTO ais (mmsi, ts, lon, lat, speed, heading) VALUES (?, ?, ?, ?, ?, ?)',
                (mmsi, ts, lon, lat, speed, heading))
    conn.commit()
    conn.close()

    return redirect(url_for('view_ais'))


# Edit AIS data
@app.route('/edit_ais/<int:id>', methods=['GET', 'POST'])
def edit_ais(id):
    """
    Edits an existing AIS record by its ID.
    - If the request method is POST, retrieves the updated data from form inputs (mmsi, ts, lon, lat, speed, heading).
    - Updates the AIS record in the database with the new data where the ID matches.
    - Commits the changes to the database and redirects to the 'view_ais' page after the update.
    - If the request method is GET, fetches the current AIS record by ID and displays it in the 'edit_ais.html' template.
    """
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
    return render_template('edit_ais.html', ais=ais_data)


# Delete AIS data
@app.route('/delete_ais/<int:id>', methods=['GET'])
def delete_ais(id):
    """
    Deletes an AIS record by its ID.
    - Connects to the database and deletes the AIS record where the ID matches.
    - Commits the deletion to the database and closes the connection.
    - Redirects to the 'view_ais' page after the record has been deleted.
    """
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM ais WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('view_ais'))


# Ship CRUD operations
@app.route('/ship', methods=['GET'])
def view_ship():
    """
    Displays a paginated list of ships with an optional search by MMSI.
    - Retrieves 'page' and 'search_mmsi' parameters from request arguments.
    - Calculates pagination offset based on the current page number.
    - Connects to the database and executes a query to count distinct MMSI values to calculate total pages.
    - If a search term (MMSI) is provided, applies a filter to the query and fetches the ship data.
    - Otherwise, retrieves all ships with minimum and maximum timestamps and total AIS records.
    - Closes the database connection and renders the 'ship.html' template with ship data and pagination info.
    """
    page = int(request.args.get('page', 1))
    search_mmsi = request.args.get('search_mmsi', '')
    per_page = 50
    offset = (page - 1) * per_page
    conn = get_db()
    cur = conn.cursor()

    # Calculate total pages
    if search_mmsi:
        search_query = f'%{search_mmsi}%'
        cur.execute('SELECT COUNT(DISTINCT mmsi) FROM ais WHERE mmsi LIKE ?', (search_query,))
    else:
        cur.execute('SELECT COUNT(DISTINCT mmsi) FROM ais')

    total_items = cur.fetchone()[0]
    total_pages = (total_items + per_page - 1) // per_page  # Round up

    # Retrieve ship data with pagination and optional search filter
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

    # Render the ship data in the 'ship.html' template with pagination info
    return render_template('ship.html', ship_data=ship_data, page=page, total_pages=total_pages,
                           search_mmsi=search_mmsi)


# Create a new ship
@app.route('/create_ship', methods=['GET', 'POST'])
def create_ship():
    """
    Creates a new ship record with a given MMSI.
    - If the request method is POST, retrieves the MMSI from the form inputs.
    - Connects to the database and inserts a new record into the 'ship' table with the provided MMSI.
    - Commits the changes to the database, closes the connection, and redirects to the 'view_ship' page.
    - If the request method is GET, renders the 'create_ship.html' template for ship creation.
    """
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
    """
    Redirects to the 'view_ais' page with a filtered view of AIS data for the specified MMSI.
    - Accepts MMSI as a path parameter and redirects to 'view_ais' with MMSI included in the query string.
    """
    return redirect(url_for('view_ais', mmsi=mmsi))


# Display and delete AIS records associated with a specific ship, with confirmation
@app.route('/delete_ship/<mmsi>', methods=['GET', 'POST'])
def delete_ship(mmsi):
    """
    Deletes all AIS records associated with a specific ship and removes the ship record.
    - If the request method is POST, confirms deletion of both the ship and its related AIS records.
    - Connects to the database to delete all AIS records where MMSI matches the specified ship.
    - Deletes the ship record itself from the 'ship' table and commits the changes.
    - Redirects to 'view_ship' after deletion.
    - If the request method is GET, fetches all AIS records related to the specified ship
      and displays them in the 'confirm_delete_ship.html' template for user confirmation.
    """
    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        # User confirms deletion of both ship and AIS records
        cur.execute('DELETE FROM ais WHERE mmsi=?', (mmsi,))
        cur.execute('DELETE FROM ship WHERE mmsi=?', (mmsi,))
        conn.commit()
        conn.close()
        return redirect(url_for('view_ship'))

    # Fetch all AIS records associated with the ship
    cur.execute('SELECT * FROM ais WHERE mmsi=?', (mmsi,))
    ais_data = cur.fetchall()
    conn.close()

    return render_template('confirm_delete_ship.html', ais_data=ais_data, mmsi=mmsi)


@app.route('/trace/<mmsi>', methods=['GET'])
def trace_view(mmsi):
    """
    Displays the trace of a specific ship's location history.
    - Connects to the database and retrieves data (timestamp, longitude, latitude) for the specified MMSI.
    - Sorts the data by timestamp to ensure a chronological view of the ship's trace.
    - Closes the database connection and invokes a service method to display the trace.
    """
    conn = get_db()

    # Retrieve data from the database (timestamp, longitude, latitude for specified ships)
    cursor = conn.cursor()
    cursor.execute("SELECT mmsi, ts, lon, lat FROM ais WHERE mmsi=? ORDER BY ts", (mmsi,))
    data = cursor.fetchall()
    # Close the database connection
    conn.close()

    return service.AisService.show_trace_service(data, mmsi)


# View joint trace of two ships
@app.route('/conjection_trace', methods=['POST', 'GET'])
def conjection_trace():
    """
    Displays the combined trace of two specified ships based on their MMSIs and a specific date.
    - Retrieves 'mmsi1', 'mmsi2', and 'date' from request arguments.
    - Connects to the database and fetches AIS data (timestamp, longitude, latitude, speed, heading) for the specified ships on the given date.
    - Closes the database connection after retrieving data.
    - Generates a video filename based on MMSI and date and calls the 'show_plot_detail' method to create a video of the trace.
    - Calls 'show_conj_trace_service' to display the combined trace of the two ships.
    """
    mmsi1 = request.args.get('mmsi1', '')
    mmsi2 = request.args.get('mmsi2', '')
    date = request.args.get('date', '')
    print(mmsi1, mmsi2, date)
    conn = get_db()

    # Retrieve data from the database (timestamp, longitude, latitude for specified ships)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT mmsi, ts, lon, lat, speed, heading
        FROM ais 
        WHERE mmsi IN (?, ?) AND DATE(ts) = DATE(?)
        ORDER BY ts
        """, (mmsi1, mmsi2, date))
    data = cursor.fetchall()
    # Close the database connection
    conn.close()
    # Generate video filename and show detailed plot for the trace
    video_filename = f"./video/{mmsi1}_{mmsi2}_{date}.mp4"
    service.AisService.show_plot_detail(data, mmsi1, mmsi2, video_filename)
    return service.AisService.show_conj_trace_service(data, mmsi1, mmsi2)


# Check for collisions
def check_collapse(date, distance=0.2):
    """
    Checks for potential collisions between ships on a specified date within a given distance threshold.
    - Connects to the database and retrieves AIS data (timestamp, longitude, latitude, speed, heading) for all ships on the specified date.
    - Passes the retrieved data to the 'check_is_collision' service method, which calculates if any ships are within the collision distance.
    - Returns the collision data (MMSI pairs and distances) for further handling.
    """
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT mmsi, ts, lon, lat, speed, heading
        FROM ais 
        WHERE DATE(ts) = DATE(?)
        ORDER BY ts
        """, (date,))
    collision_data = cur.fetchall()
    conn.close()
    return service.AisService.check_is_collision(collision_data, distance, date)  # mmsi1, mmsi2, distance


@app.route('/check_collapse', methods=['POST'])
def check_collision_view():
    """
    Displays potential collision data on a specified date with a given distance threshold.
    - Retrieves 'date' and 'distance' from the form inputs.
    - Calls the 'check_collapse' function to get collision data for ships on the specified date.
    - Passes the collision data and date to the 'collision.html' template for display.
    """
    date = request.form.get('date', '')
    distance = float(request.form.get('distance', 0.2))
    collision_data = check_collapse(date, distance)
    # Pass the date as a query parameter
    return render_template('collision.html', collision_data=collision_data, date=date)


@app.route('/conjection_trace_video', methods=['POST', 'GET'])
def plot_detail():
    """
    Generates and displays a video of the joint trace of two specified ships.
    - Retrieves 'mmsi1', 'mmsi2', and 'date' from request arguments.
    - Connects to the database and fetches AIS data (timestamp, longitude, latitude, speed, heading) for the specified ships on the given date.
    - Closes the database connection after retrieving the data.
    - Calls 'show_plot_detail' to generate a video file of the trace, with a filename based on MMSI and date.
    - Renders 'conjection_trace_video.html' template with the video file to allow playback within a Bootstrap-enabled page.
    """
    mmsi1 = request.args.get('mmsi1', '')
    mmsi2 = request.args.get('mmsi2', '')
    date = request.args.get('date', '')

    print(mmsi1, mmsi2, date)
    conn = get_db()

    # Retrieve data from the database (timestamp, longitude, latitude for specified ships)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT mmsi, ts, lon, lat, speed, heading
        FROM ais 
        WHERE mmsi IN (?, ?) AND DATE(ts) = DATE(?)
        ORDER BY ts
        """, (mmsi1, mmsi2, date))
    data = cursor.fetchall()
    # Close the database connection
    conn.close()

    # Generate the video file based on MMSI and date
    video_filename = f"./video/{mmsi1}_{mmsi2}_{date}.mp4"
    service.AisService.show_plot_detail(data, mmsi1, mmsi2, video_filename)

    # Render the HTML template with Bootstrap to play the video
    return render_template('conjection_trace_video.html', video_file=video_filename)


# Index page
@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Renders the main page and handles form submission for viewing joint ship traces.
    - If the request method is POST, retrieves 'mmsi1', 'mmsi2', 'date', and 'distance' from form inputs.
    - Redirects to the 'conjection_trace' page with the specified parameters to display the joint trace of two ships.
    - If the request method is GET, renders 'index.html' template for the main page.
    """
    if request.method == 'POST':
        mmsi1 = request.form['mmsi1']
        mmsi2 = request.form['mmsi2']
        date = request.form['date']
        return redirect(url_for('conjection_trace', mmsi1=mmsi1, mmsi2=mmsi2, date=date))
    return render_template('index.html')


if __name__ == '__main__':
    # Run the application on host 0.0.0.0 with debug mode enabled
    app.run(host='0.0.0.0', debug=True)

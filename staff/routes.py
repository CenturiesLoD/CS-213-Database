from flask import Blueprint, render_template, session, redirect, request, url_for
from db import get_db_connection

staff_bp = Blueprint("staff", __name__)

@staff_bp.route("/dashboard")
def dashboard():
    # must be logged in as staff
    if "user_type" not in session or session["user_type"] != "staff":
        return redirect("/login")

    # airline this staff works for
    airline = session.get("airline_name")

    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """
        SELECT 
            flight_num,
            departure_airport,
            departure_time,
            arrival_airport,
            arrival_time,
            status,
            airplane_id
        FROM flight
        WHERE airline_name = %s
          AND departure_time BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 30 DAY)
        ORDER BY departure_time;
    """

    cursor.execute(sql, (airline,))
    flights = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("staff/dashboard.html", flights=flights, airline_name=airline)
@staff_bp.route("/next30")
def next30():
    # must be logged in as staff
    if "user_type" not in session or session["user_type"] != "staff":
        return redirect("/login")

    airline = session.get("airline_name")
    if not airline:
        return "No airline found for this staff member", 400

    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """
        SELECT 
            airline_name,
            flight_num,
            departure_airport,
            departure_time,
            arrival_airport,
            arrival_time,
            status,
            airplane_id
        FROM flight
        WHERE airline_name = %s
        AND departure_time BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 30 DAY)
        ORDER BY departure_time;
    """
    cursor.execute(sql, (airline,))
    flights = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("staff/flights_next30.html", flights=flights, airline_name=airline)

@staff_bp.route("/search", methods=["GET", "POST"])
def search():
    # staff login required
    if "user_type" not in session or session["user_type"] != "staff":
        return redirect("/login")

    airline = session.get("airline_name")
    if not airline:
        return "No airline found for this staff member", 400

    # GET → show empty form
    if request.method == "GET":
        return render_template("staff/flight_search.html", results=None)

    # POST → perform search
    dep = request.form.get("departure", "").strip().lower()
    arr = request.form.get("arrival", "").strip().lower()
    city = request.form.get("city", "").strip().lower()
    date = request.form.get("date", "").strip().lower()

    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """
        SELECT
            f.airline_name,
            f.flight_num,
            f.departure_airport,
            f.departure_time,
            f.arrival_airport,
            f.arrival_time,
            f.status,
            f.airplane_id,
            dep_city.city_name AS dep_city,
            arr_city.city_name AS arr_city
        FROM flight f
        JOIN airport dep
            ON dep.airport_name = f.departure_airport
        JOIN city dep_city
            ON dep.airport_city = dep_city.city_name
        JOIN airport arr
            ON arr.airport_name = f.arrival_airport
        JOIN city arr_city
            ON arr.airport_city = arr_city.city_name
        WHERE f.airline_name = %s
          AND (%s = '' OR LOWER(f.departure_airport) LIKE %s)
          AND (%s = '' OR LOWER(f.arrival_airport) LIKE %s)
          AND (%s = '' 
               OR LOWER(dep_city.city_name) LIKE %s
               OR LOWER(arr_city.city_name) LIKE %s)
          AND (%s = '' 
               OR LOWER(f.departure_time) LIKE %s
               OR LOWER(f.arrival_time) LIKE %s)
        ORDER BY f.departure_time;
    """

    cursor.execute(
        sql,
        (
            airline,
            dep, f"%{dep}%",
            arr, f"%{arr}%",
            city, f"%{city}%", f"%{city}%",
            date, f"%{date}%", f"%{date}%"
        )
    )

    results = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("staff/flight_search.html", results=results)
@staff_bp.route("/passengers/<airline>/<flight_num>")
def passenger_list(airline, flight_num):
    # must be logged in as staff
    if "user_type" not in session or session["user_type"] != "staff":
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    # fetch flight info
    cursor.execute("""
        SELECT airline_name, flight_num, departure_airport, departure_time,
               arrival_airport, arrival_time, status
        FROM flight
        WHERE airline_name = %s AND flight_num = %s
    """, (airline, flight_num))
    flight = cursor.fetchone()

    if not flight:
        cursor.close()
        conn.close()
        return f"No such flight {airline} {flight_num}", 404

    # fetch passengers
    cursor.execute("""
        SELECT p.customer_email, c.name
        FROM purchases p
        JOIN customer c ON p.customer_email = c.email
        JOIN ticket t ON t.ticket_id = p.ticket_id
        WHERE t.airline_name = %s AND t.flight_num = %s
        ORDER BY c.name
    """, (airline, flight_num))
    passengers = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("staff/passenger_list.html",
                           flight=flight,
                           passengers=passengers)

@staff_bp.route("/customer_history")
def customer_history():
    return render_template("staff/customer_history.html", results=None)
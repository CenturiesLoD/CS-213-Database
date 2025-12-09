from flask import Blueprint, render_template, session, redirect, request, url_for, flash
from db import get_db_connection
import pymysql

def require_staff_login():
    if "user_type" not in session or session["user_type"] != "staff":
        return redirect("/login")
    return None

def require_staff_admin():
    role = (session.get("role") or "").strip().lower()
    if role not in ("admin", "both"):
        return "Access denied: admin only", 403
    return None

def require_staff_operator():
    role = (session.get("staff_role") or "").strip().lower()
    if role not in ("operator", "both"):
        return "Access denied: operator only", 403
    return None

staff_bp = Blueprint("staff", __name__)

@staff_bp.route("/dashboard")
def dashboard():
    # must be logged in as staff
    if "user_type" not in session or session["user_type"] != "staff":
        return redirect("/login")

    airline = session.get("airline_name")
    raw_role = session.get("role", "")   # ← 正确的 key 是 "role"
    role = (raw_role or "").strip().lower()

    is_admin = role in ("admin", "both")
    is_operator = role in ("operator", "both")

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

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

    return render_template(
        "staff/dashboard.html",
        flights=flights,
        airline_name=airline,
        is_admin=is_admin,
        is_operator=is_operator
    )
@staff_bp.route("/next30")
def next30():
    # must be logged in as staff
    if "user_type" not in session or session["user_type"] != "staff":
        return redirect("/login")

    airline = session.get("airline_name")
    if not airline:
        return "No airline found for this staff member", 400

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

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
    cursor = conn.cursor(pymysql.cursors.DictCursor)

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
    cursor = conn.cursor(pymysql.cursors.DictCursor)

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

#again can be done by all staff
@staff_bp.route("/customer_history", methods=["GET", "POST"])
def customer_history():
    # must be logged in as staff
    if "user_type" not in session or session["user_type"] != "staff":
        return redirect("/login")

    airline = session.get("airline_name")
    if not airline:
        return "No airline found for this staff member", 400

    results = []
    customer_email = ""
    error_msg = ""

    if request.method == "POST":
        customer_email = request.form.get("customer_email", "").strip()

        if not customer_email:
            error_msg = "Please enter a customer email."
        else:
            conn = get_db_connection()
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            try:
                # Check that the customer exists
                sql_check_customer = """
                    SELECT email
                    FROM customer
                    WHERE email = %s
                """
                cursor.execute(sql_check_customer, (customer_email,))
                row = cursor.fetchone()

                if not row:
                    error_msg = "No such customer email was found."
                else:
                    # All flights this customer has taken on this airline
                    sql_history = """
                        SELECT
                            f.airline_name,
                            f.flight_num,
                            f.departure_airport,
                            f.departure_time,
                            f.arrival_airport,
                            f.arrival_time,
                            f.status,
                            p.purchase_date,
                            t.ticket_id
                        FROM purchases p
                        JOIN ticket t
                          ON p.ticket_id = t.ticket_id
                        JOIN flight f
                          ON t.airline_name = f.airline_name
                         AND t.flight_num = f.flight_num
                        WHERE p.customer_email = %s
                          AND f.airline_name = %s
                        ORDER BY f.departure_time DESC
                    """
                    cursor.execute(sql_history, (customer_email, airline))
                    results = cursor.fetchall()
            finally:
                cursor.close()
                conn.close()

    return render_template(
        "staff/customer_history.html",
        results=results,
        customer_email=customer_email,
        airline_name=airline,
        error_msg=error_msg,
    )

@staff_bp.route("/analytics/agents")
def analytics_agents():
    # Any staff can view (not admin-only)
    if session.get("user_type") != "staff":
        return redirect("/login")

    airline = session.get("airline_name")
    if not airline:
        return "No airline found for this staff member", 400

    conn = get_db_connection()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    try:
        # Top booking agents in the last month (by tickets & commission)
        sql_month = """
            SELECT
                p.booking_agent_email AS agent_email,
                COUNT(*) AS tickets_sold,
                SUM(f.price * 0.10) AS total_commission
            FROM purchases p
            JOIN ticket t
              ON p.ticket_id = t.ticket_id
            JOIN flight f
              ON t.airline_name = f.airline_name
             AND t.flight_num   = f.flight_num
            WHERE f.airline_name = %s
              AND p.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
              AND p.booking_agent_email IS NOT NULL
            GROUP BY agent_email
            ORDER BY tickets_sold DESC
            LIMIT 5;
        """
        cur.execute(sql_month, (airline,))
        top_agents_month = cur.fetchall()

        # Top booking agents in the last year (by tickets & commission)
        sql_year = """
            SELECT
                p.booking_agent_email AS agent_email,
                COUNT(*) AS tickets_sold,
                SUM(f.price * 0.10) AS total_commission
            FROM purchases p
            JOIN ticket t
              ON p.ticket_id = t.ticket_id
            JOIN flight f
              ON t.airline_name = f.airline_name
             AND t.flight_num   = f.flight_num
            WHERE f.airline_name = %s
              AND p.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
              AND p.booking_agent_email IS NOT NULL
            GROUP BY agent_email
            ORDER BY tickets_sold DESC
            LIMIT 5;
        """
        cur.execute(sql_year, (airline,))
        top_agents_year = cur.fetchall()
    finally:
        cur.close()
        conn.close()

    return render_template(
        "staff/analytics_agents.html",
        airline_name=airline,
        top_agents_month=top_agents_month,
        top_agents_year=top_agents_year,
    )

@staff_bp.route("/analytics/customers")
def analytics_customers():
    # Any staff can view
    if session.get("user_type") != "staff":
        return redirect("/login")

    airline = session.get("airline_name")
    if not airline:
        return "No airline found for this staff member", 400

    conn = get_db_connection()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    try:
        # Most frequent customers in the last year (by tickets bought)
        sql_top_customers = """
            SELECT
                p.customer_email,
                COUNT(*) AS tickets_sold
            FROM purchases p
            JOIN ticket t
              ON p.ticket_id = t.ticket_id
            JOIN flight f
              ON t.airline_name = f.airline_name
             AND t.flight_num   = f.flight_num
            WHERE f.airline_name = %s
              AND p.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
            GROUP BY p.customer_email
            ORDER BY tickets_sold DESC
            LIMIT 5;
        """
        cur.execute(sql_top_customers, (airline,))
        top_customers_year = cur.fetchall()

        # Tickets sold per month for the last year
        sql_tickets_per_month = """
            SELECT
                DATE_FORMAT(p.purchase_date, '%%Y-%%m') AS yr_mth,
                COUNT(*) AS tickets_sold
            FROM purchases p
            JOIN ticket t
            ON p.ticket_id = t.ticket_id
            JOIN flight f
            ON t.airline_name = f.airline_name
            AND t.flight_num   = f.flight_num
            WHERE f.airline_name = %s
            AND p.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
            GROUP BY DATE_FORMAT(p.purchase_date, '%%Y-%%m')
            ORDER BY DATE_FORMAT(p.purchase_date, '%%Y-%%m');


        """
        cur.execute(sql_tickets_per_month, (airline,))
        tickets_per_month = cur.fetchall()

        # Delay vs on-time statistics (last year, by flight status)
        sql_status_counts = """
            SELECT
                f.status,
                COUNT(*) AS flight_count
            FROM flight f
            WHERE f.airline_name = %s
              AND f.departure_time >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
            GROUP BY f.status;
        """
        cur.execute(sql_status_counts, (airline,))
        status_rows = cur.fetchall()
    finally:
        cur.close()
        conn.close()

    # Aggregate into delayed / on_time buckets using known statuses
    delayed = sum(r["flight_count"] for r in status_rows if r["status"] == "delayed")
    on_time = sum(
        r["flight_count"]
        for r in status_rows
        if r["status"] in ("upcoming", "in-progress")
    )
    canceled = sum(r["flight_count"] for r in status_rows if r["status"] == "canceled")

    return render_template(
        "staff/analytics_customers.html",
        airline_name=airline,
        top_customers_year=top_customers_year,
        tickets_per_month=tickets_per_month,
        status_rows=status_rows,
        delayed=delayed,
        on_time=on_time,
        canceled=canceled,
    )

#FIX THIS
@staff_bp.route("/analytics/destinations")
def analytics_destinations():
    # Any staff can view
    if session.get("user_type") != "staff":
        return redirect("/login")

    airline = session.get("airline_name")
    if not airline:
        return "No airline found for this staff member", 400

    conn = get_db_connection()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    try:
        # Top destinations last 3 months (by tickets sold, grouped by arrival city)
        sql_top_dest_3m = """
            SELECT
                arr_city.city_name AS destination_city,
                COUNT(*) AS tickets_sold
            FROM purchases p
            JOIN ticket t
              ON p.ticket_id = t.ticket_id
            JOIN flight f
              ON t.airline_name = f.airline_name
             AND t.flight_num   = f.flight_num
            JOIN airport arr
              ON arr.airport_name = f.arrival_airport
            JOIN city arr_city
              ON arr.airport_city = arr_city.city_name
            WHERE f.airline_name = %s
              AND p.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
            GROUP BY destination_city
            ORDER BY tickets_sold DESC
            LIMIT 5;
        """
        cur.execute(sql_top_dest_3m, (airline,))
        top_destinations_3m = cur.fetchall()

        # Top destinations last year (by tickets sold)
        sql_top_dest_year = """
            SELECT
                arr_city.city_name AS destination_city,
                COUNT(*) AS tickets_sold
            FROM purchases p
            JOIN ticket t
              ON p.ticket_id = t.ticket_id
            JOIN flight f
              ON t.airline_name = f.airline_name
             AND t.flight_num   = f.flight_num
            JOIN airport arr
              ON arr.airport_name = f.arrival_airport
            JOIN city arr_city
              ON arr.airport_city = arr_city.city_name
            WHERE f.airline_name = %s
              AND p.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
            GROUP BY destination_city
            ORDER BY tickets_sold DESC
            LIMIT 5;
        """
        cur.execute(sql_top_dest_year, (airline,))
        top_destinations_year = cur.fetchall()
    finally:
        cur.close()
        conn.close()

    return render_template(
        "staff/analytics_destinations.html",
        airline_name=airline,
        top_destinations_3m=top_destinations_3m,
        top_destinations_year=top_destinations_year,
    )




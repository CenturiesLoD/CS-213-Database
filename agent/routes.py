from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from db import get_db_connection
import pymysql

agent_bp = Blueprint("agent", __name__)

#These are for the urls that the agent will use to access different pages
#Urls lead to corresponding pages in the templates folder


@agent_bp.route("/dashboard")
def dashboard():
    # For now, just render a simple dashboard.
    # You can later add summaries (tickets sold, commission, etc.).
    if session.get("user_type") != "agent":
        flash("You must log in as a booking agent to access this page.")
        return redirect(url_for("auth.login"))
    return render_template("agent/dashboard.html")

@agent_bp.route("/flights", methods=["GET"])
def flights():
    """
    View flights this booking agent has purchased on behalf of customers,
    optionally filtered by date range and route (departure/arrival airport).
    """
    if session.get("user_type") != "agent":
        flash("You must log in as a booking agent to view these flights.")
        return redirect(url_for("auth.login"))

    agent_email = session.get("email")

    # Filters from query string (?qStartDate=...&qEndDate=... etc.)
    qStartDate = request.args.get("qStartDate", "").strip()
    qEndDate   = request.args.get("qEndDate", "").strip()
    qDepart    = request.args.get("qDepart", "").strip()
    qArrive    = request.args.get("qArrive", "").strip()

    # Patterns for LIKE filters (case-insensitive)
    patternDepart = f"%{qDepart.lower()}%" if qDepart else ""
    patternArrive = f"%{qArrive.lower()}%" if qArrive else ""

    flights = []

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        sql = """
            SELECT
                p.ticket_id,
                p.purchase_date,
                p.customer_email,
                f.airline_name,
                f.flight_num,
                f.departure_airport,
                f.departure_time,
                f.arrival_airport,
                f.arrival_time,
                f.price,
                f.status
            FROM purchases p
            JOIN ticket t
              ON p.ticket_id = t.ticket_id
            JOIN flight f
              ON t.airline_name = f.airline_name
             AND t.flight_num   = f.flight_num
            WHERE p.booking_agent_email = %s
              -- Date range filters (optional)
              AND (%s = '' OR p.purchase_date >= %s)
              AND (%s = '' OR p.purchase_date <= %s)
              -- Route filters (optional)
              AND (%s = '' OR LOWER(f.departure_airport) LIKE %s)
              AND (%s = '' OR LOWER(f.arrival_airport)   LIKE %s)
            ORDER BY p.purchase_date DESC, f.departure_time DESC
        """
        cursor.execute(
            sql,
            (
                agent_email,
                qStartDate, qStartDate,
                qEndDate,   qEndDate,
                patternDepart, patternDepart,
                patternArrive, patternArrive,
            ),
        )
        flights = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template(
        "agent/flights.html",
        flights=flights,
        qStartDate=qStartDate,
        qEndDate=qEndDate,
        qDepart=qDepart,
        qArrive=qArrive,
    )


#a helper function, could be replaced with pure SQL statement inside of search function
def get_authorized_airlines(agent_email):
    """
    Return a list of airline_name values this agent is authorized for.
    Reads from agent_airline_authorization.
    """
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        sql = """
            SELECT airline_name
            FROM agent_airline_authorization
            WHERE agent_email = %s
            ORDER BY airline_name
        """
        cursor.execute(sql, (agent_email,))
        rows = cursor.fetchall()
        return [r["airline_name"] for r in rows]
    finally:
        cursor.close()
        conn.close()



@agent_bp.route("/search", methods=["GET"])
def search():
    """
    Booking agent flight search.
    Shows only flights for airlines this agent is authorized to represent.
    """
    if session.get("user_type") != "agent":
        flash("You must log in as a booking agent to search flights.")
        return redirect(url_for("auth.login"))

    agent_email = session.get("email")

    # Fetch list of authorized airlines via helper
    authorized = get_authorized_airlines(agent_email)

    # If no authorizations, nothing to search
    if not authorized:
        flash("You are not authorized for any airlines yet.")
        return render_template(
            "agent/search.html",
            flights=[],
            qArrive="",
            qDepart="",
            qCityArr="",
            qCityDep="",
            qDate="",
        )

    # Read filters from query string
    qArrive = request.args.get("qArrive", "").strip()
    qDepart = request.args.get("qDepart", "").strip()
    qCityArr = request.args.get("qCityArr", "").strip()
    qCityDep = request.args.get("qCityDep", "").strip()
    qDate   = request.args.get("qDate", "").strip()

    # If all are blank, just show the empty form (no results)
    if not (qArrive or qDepart or qCityArr or qCityDep or qDate):
        # Optionally flash once if there were query args:
        if request.args:
            flash("Please enter at least one search field.")
        return render_template(
            "agent/search.html",
            flights=[],
            qArrive=qArrive,
            qDepart=qDepart,
            qCityArr=qCityArr,
            qCityDep=qCityDep,
            qDate=qDate,
        )


    patternArrive = f"%{qArrive.lower()}%" if qArrive else ""
    patternDepart = f"%{qDepart.lower()}%" if qDepart else ""
    patternCityArr = f"%{qCityArr.lower()}%" if qCityArr else ""
    patternCityDep = f"%{qCityDep.lower()}%" if qCityDep else ""
    patternDate   = f"%{qDate}%" if qDate else ""

    flights = []
    
    # Only query if at least one filter is provided (optional, can remove)
    #if qArrive or qDepart or qCityArr or qCityDep or qDate:
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        # Build placeholders for IN clause (one %s per authorized airline)
        airline_placeholders = ",".join(["%s"] * len(authorized))

        sql = f"""
            SELECT
                f.airline_name,
                f.flight_num,
                dep.airport_name AS departure_airport_name,
                f.departure_airport,
                f.departure_time,
                arr.airport_name AS arrival_airport_name,
                f.arrival_airport,
                f.arrival_time,
                f.price,
                f.status,
                f.airplane_id
            FROM flight AS f
            JOIN airport AS dep
                ON f.departure_airport = dep.airport_name
            JOIN city AS dep_city
                ON dep.airport_city = dep_city.city_name
            JOIN airport AS arr
                ON f.arrival_airport = arr.airport_name
            JOIN city AS arr_city
                ON arr.airport_city = arr_city.city_name
            WHERE f.status = 'upcoming'
                AND f.airline_name IN ({airline_placeholders})
                AND (%s = '' OR LOWER(f.arrival_airport)  LIKE %s)
                AND (%s = '' OR LOWER(f.departure_airport) LIKE %s)
                AND (%s = '' OR LOWER(arr_city.city_name) LIKE %s)
                AND (%s = '' OR LOWER(dep_city.city_name) LIKE %s)
                AND (%s = '' OR LOWER(f.arrival_time)     LIKE %s)
                AND (%s = '' OR LOWER(f.departure_time)   LIKE %s)
            ORDER BY f.departure_time;
        """

        # Params: first all authorized airline names, then patterns
        params = (
            *authorized,
            patternArrive, patternArrive,
            patternDepart, patternDepart,
            patternCityArr, patternCityArr,
            patternCityDep, patternCityDep,
            patternDate, patternDate,
            patternDate, patternDate,
        )

        cursor.execute(sql, params)
        flights = cursor.fetchall()
    except Exception as e:
        flash(f"Agent search failed: {e}")
    finally:
        cursor.close()
        conn.close()

    return render_template(
        "agent/search.html",
        flights=flights,
        qArrive=qArrive,
        qDepart=qDepart,
        qCityArr=qCityArr,
        qCityDep=qCityDep,
        qDate=qDate,
    )



#NEED TO IMPLEMENT LATER 12/7/25
# @agent_bp.route("/search")
# def search():
#     # Later: restrict to airlines this agent is authorized for
#     if session.get("user_type") != "agent":
#         flash("You must log in as a booking agent to search flights.")
#         return redirect(url_for("auth.login"))
#     return render_template("agent/search.html")

#Purchase function where agent can dictate who to purchase for
@agent_bp.route("/purchase", methods=["POST"])
def purchase():
    """
    Booking agent purchases a ticket on behalf of a customer.
    Enforces:
      - agent is logged in
      - customer exists
      - agent is authorized for the airline
      - flight is upcoming and not full
    """
    if session.get("user_type") != "agent":
        flash("You must log in as a booking agent to purchase.")
        return redirect(url_for("auth.login"))

    agent_email = session.get("email")

    airline_name   = request.form.get("airline_name", "").strip()
    flight_num     = request.form.get("flight_num", "").strip()
    airplane_id    = request.form.get("airplane_id", "").strip()
    customer_email = request.form.get("customer_email", "").strip()

    if not (airline_name and flight_num and airplane_id and customer_email):
        flash("Missing flight or customer data.")
        return redirect(url_for("agent.search"))

    # Optional: basic sanity for flight_num / airplane_id
    try:
        flight_num = int(flight_num)
        airplane_id = int(airplane_id)
    except ValueError:
        flash("Invalid flight data.")
        return redirect(url_for("agent.search"))

    conn = get_db_connection()
    conn.begin()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        # 1) Ensure customer exists
        sql_cust = """
            SELECT email
            FROM customer
            WHERE email = %s
        """
        cursor.execute(sql_cust, (customer_email,))
        if cursor.fetchone() is None:
            raise ValueError("Customer does not exist.")

        # 2) Ensure agent is authorized for this airline
        sql_auth = """
            SELECT 1
            FROM agent_airline_authorization
            WHERE agent_email = %s
              AND airline_name = %s
        """
        cursor.execute(sql_auth, (agent_email, airline_name))
        if cursor.fetchone() is None:
            raise ValueError("You are not authorized to sell tickets for this airline.")

        # 3) Read current price/status/capacity for the flight (lock row)
        sql_flight = """
            SELECT f.price,
                   f.status,
                   a.seat_capacity AS seat_capacity
            FROM flight f
            JOIN airplane a
              ON a.airline_name = f.airline_name
             AND a.airplane_id = f.airplane_id
            WHERE f.airline_name = %s
              AND f.flight_num   = %s
              AND f.airplane_id  = %s
            FOR UPDATE
        """
        cursor.execute(sql_flight, (airline_name, flight_num, airplane_id))
        row = cursor.fetchone()
        if not row:
            raise ValueError("Flight not found.")

        if row["status"] != "upcoming":
            raise ValueError("Flight is not available for purchase.")

        price = row["price"]
        seat_capacity = row["seat_capacity"]

        # 4) Count tickets already sold for this flight (lock related rows)
        sql_sold = """
            SELECT COUNT(*) AS sold
            FROM ticket t
            JOIN purchases p ON p.ticket_id = t.ticket_id
            WHERE t.airline_name = %s
              AND t.flight_num   = %s
            FOR UPDATE
        """
        cursor.execute(sql_sold, (airline_name, flight_num))
        sold = cursor.fetchone()["sold"]

        if sold >= seat_capacity:
            raise ValueError("This flight is full.")

        # 5) Generate next ticket_id by filling gaps
        #    Find the smallest positive integer not already used as a ticket_id.
        cursor.execute(
            "SELECT ticket_id FROM ticket ORDER BY ticket_id FOR UPDATE"
        )
        rows = cursor.fetchall()

        next_id = 1
        for r in rows:
            current = r["ticket_id"]
            if current > next_id:
                # Found a gap: next_id is not used
                break
            if current == next_id:
                next_id += 1
        # After the loop, next_id is either the first gap or 1 + max(ticket_id)


        # 6) Insert ticket with explicit ticket_id
        cursor.execute(
            "INSERT INTO ticket (ticket_id, airline_name, flight_num) VALUES (%s, %s, %s)",
            (next_id, airline_name, flight_num),
        )

        # 7) Insert purchase, including booking_agent_email
        cursor.execute(
            """
            INSERT INTO purchases (ticket_id, customer_email, booking_agent_email, purchase_date)
            VALUES (%s, %s, %s, CURDATE())
            """,
            (next_id, customer_email, agent_email),
        )

        conn.commit()

        seats_left_after = seat_capacity - (sold + 1)
        flash(
            f"Sold {airline_name} flight {flight_num} to {customer_email} at {price}. "
            f"Seats left: {seats_left_after}"
        )

        # After sale, go back to agent flights list or search
        return redirect(url_for("agent.flights"))

    except Exception as e:
        conn.rollback()
        flash(f"Purchase failed: {e}")
        return redirect(url_for("agent.search"))
    finally:
        cursor.close()
        conn.close()


@agent_bp.route("/analytics/commission")
def commission():
    if session.get("user_type") != "agent":
        flash("You must log in as a booking agent to view analytics.")
        return redirect(url_for("auth.login"))
    return render_template("agent/analytics_commission.html")


@agent_bp.route("/analytics/top_customers")
def top_customers():
    if session.get("user_type") != "agent":
        flash("You must log in as a booking agent to view analytics.")
        return redirect(url_for("auth.login"))
    return render_template("agent/analytics_top_customers.html")



#DEBUG PURPOSE 
@agent_bp.route("/debug/airlines")
def debug_airlines():
    """
    Debug page: show airlines this booking agent is authorized for.
    """
    if session.get("user_type") != "agent":
        flash("You must log in as a booking agent to view this page.")
        return redirect(url_for("auth.login"))

    agent_email = session.get("email")

    airlines = []

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        sql = """
            SELECT airline_name
            FROM agent_airline_authorization
            WHERE agent_email = %s
            ORDER BY airline_name
        """
        cursor.execute(sql, (agent_email,))
        airlines = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template(
        "agent/debug_airlines.html",
        agent_email=agent_email,
        airlines=airlines,
    )
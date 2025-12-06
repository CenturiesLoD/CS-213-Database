from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from db import get_db_connection
import pymysql

customer_bp = Blueprint("customer", __name__)

#These are for the urls that the agent will use to access different pages
#Urls lead to corresponding pages in the templates folder

#12/5 19:25, working on dashboard
@customer_bp.route("/dashboard")
def dashboard():
#    Require login as customer
    if session.get("user_type") != "customer":
        flash("You got into the userdash board without logging in as customer! Go away.")
        return redirect(url_for("auth.login"))
    customer_email = session.get("email")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
            SELECT
                f.airline_name,
                f.flight_num,
                f.departure_airport,
                f.departure_time,
                f.arrival_airport,
                f.arrival_time,
                f.status
            FROM purchases p
            JOIN ticket t
              ON p.ticket_id = t.ticket_id
            JOIN flight f
              ON t.airline_name = f.airline_name
             AND t.flight_num = f.flight_num
            WHERE p.customer_email = %s
              AND f.status = 'upcoming'
            ORDER BY f.departure_time
        """
        cursor.execute(sql, (customer_email,))
        flights = cursor.fetchall()

        # sql = """
        #     SELECT COUNT(*) AS flight_count
        #     FROM purchases p"""
    finally:
        cursor.close()
        conn.close()

    return render_template("customer/dashboard.html", flights=flights, customer_email=customer_email)


#NOTE IT IS BEING REWRITTEN AS OF 12/6 20:20
#IT SHOULD BE FUNCTIONALLY THE SAME AS public/routes.py's search
@customer_bp.route("/search", methods=["GET", "POST"])
def search_flights():
    # Only logged-in customers can search & purchase
    if session.get("user_type") != "customer":
        flash("You must log in as a customer to search and purchase.")
        return redirect(url_for("auth.login"))

    if request.method == "GET":
        return render_template("customer/search.html")

    # Same field names as public search: qArrive, qDepart, qCity, qDate
    qArrive = request.form.get("qArrive", "").strip()
    qDepart = request.form.get("qDepart", "").strip()
    qCity   = request.form.get("qCity",   "").strip()
    qDate   = request.form.get("qDate",   "").strip()

    # introduce wild cards so if it appears, it's accepted (same as public)
    patternArrive = f"%{qArrive.lower()}%" if qArrive else ""
    patternDepart = f"%{qDepart.lower()}%" if qDepart else ""
    patternCity   = f"%{qCity.lower()}%"   if qCity   else ""
    patternDate   = f"%{qDate}%"           if qDate   else ""

    flights = []

    if not (qArrive or qDepart or qCity or qDate):
        flash("Please enter at least one search field.")
        return redirect(url_for("customer.search_flights"))

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        # SQL copied from public_search_upcoming: upcoming flights filtered by
        # arrival/departure airport, city, and date. [file:281]
        sql = """
            SELECT
                flight.airline_name,
                flight.flight_num,
                flight.departure_airport,
                flight.departure_time,
                flight.arrival_airport,
                flight.arrival_time,
                flight.price,
                flight.status,
                flight.airplane_id
            FROM flight
            JOIN airport
              ON flight.departure_airport = airport.airport_name
              OR flight.arrival_airport   = airport.airport_name
            WHERE flight.status = 'upcoming'
              AND (
                    LOWER(flight.arrival_airport)   LIKE %s
                 OR LOWER(flight.departure_airport) LIKE %s
                 OR LOWER(airport.airport_city)     LIKE %s
                 OR LOWER(flight.arrival_time)      LIKE %s
                 OR LOWER(flight.departure_time)    LIKE %s
                  )
            ORDER BY flight.departure_time;
        """

        cursor.execute(
            sql,
            (patternArrive, patternDepart, patternCity, patternDate, patternDate),
        )
        flights = cursor.fetchall()

        # Same search behavior as public, but customer template can show Buy buttons.
        return render_template(
            "customer/search_results.html",
            results=flights,
            qArrive=qArrive,
            qDepart=qDepart,
            qCity=qCity,
            qDate=qDate,
        )

    except Exception as e:
        flash(f"Search failed: {e}")
        return redirect(url_for("customer.search_flights"))

    finally:
        cursor.close()
        conn.close()

#UNUSED FORNOW. SINCE CUSTOMERS CANT BUY TICKETS FOR FLYING PLANES JUST USE PUBLIC SEARCH
# @customer_bp.route("/search/in_progress", methods=["GET"])
# def customer_search_in_progress():
#     # Read query parameters from URL, e.g. /search/in_progress?airline=DemoAir1&flight_num=1001
#     airline = request.args.get("airline", "").strip()
#     flight_num = request.args.get("flight_num", "").strip()

#     flights_in_progress = []

#     if airline and flight_num:
#         conn = get_db_connection()
#         cursor = conn.cursor(pymysql.cursors.DictCursor)
#         try:
#             sql = """
#                 SELECT
#                     airline_name,
#                     flight_num,
#                     departure_airport,
#                     departure_time,
#                     arrival_airport,
#                     arrival_time,
#                     status
#                 FROM flight
#                 WHERE LOWER(airline_name) = %s
#                   AND flight_num = %s
#                   AND status = 'in-progress'
#             """
#             cursor.execute(sql, (airline.lower(), flight_num))
#             flights_in_progress = cursor.fetchall()
#         finally:
#             cursor.close()
#             conn.close()

#     return render_template(
#         "public_search_in_progress.html",
#         flights=flights_in_progress,
#         airline=airline,
#         flight_num=flight_num,
#     )

@customer_bp.route("/flights")
def my_flights():
    return render_template("customer/flights.html")

@customer_bp.route("/purchase", methods=["POST"])
def purchase():
    return render_template("customer/purchase.html")

@customer_bp.route("/spending/default")
def spending_default():
    return render_template("customer/spending_default.html")

@customer_bp.route("/spending/custom")
def spending_custom():
    return render_template("customer/spending_custom.html")
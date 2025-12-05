from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from db import get_db_connection

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


@customer_bp.route("/search", methods=["GET", "POST"])
def search_flights():
    # Show search page
    if request.method == "GET":
        return render_template("customer/search.html")

    # Extract input
    departure = request.form.get("departure")
    arrival = request.form.get("arrival")
    date = request.form.get("date")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # SQL: search flights by city or airport name
        query = """
            SELECT *
            FROM flight
            WHERE (departure_airport = %s OR departure_city = %s)
              AND (arrival_airport = %s OR arrival_city = %s)
              AND DATE(departure_time) = %s
        """

        cursor.execute(query, (departure, departure, arrival, arrival, date))
        results = cursor.fetchall()

        return render_template("customer/search_results.html", results=results)

    except Exception as e:
        flash(f"Search failed: {e}")
        return redirect(url_for("customer.search_flights"))

    finally:
        cursor.close()
        conn.close()

@customer_bp.route("/flights")
def my_flights():
    return render_template("customer/flights.html")

@customer_bp.route("/purchase")
def purchase():
    return render_template("customer/purchase.html")

@customer_bp.route("/spending/default")
def spending_default():
    return render_template("customer/spending_default.html")

@customer_bp.route("/spending/custom")
def spending_custom():
    return render_template("customer/spending_custom.html")
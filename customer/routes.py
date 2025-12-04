from flask import Blueprint, render_template, request, flash, redirect, url_for
from db import get_db_connection

customer_bp = Blueprint("customer", __name__)

@customer_bp.route("/dashboard")
def dashboard():
    return render_template("customer/dashboard.html")

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
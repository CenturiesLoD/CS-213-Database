from flask import Blueprint, render_template, request
from db import get_db_connection
import pymysql

public_bp = Blueprint("public", __name__)

#These are for the urls that the agent will use to access different pages
#Urls lead to corresponding pages in the templates folder
@public_bp.route("/search/upcoming", methods=["GET"])
def public_search_upcoming():
    # q will come from the search bar, e.g. ?q=JFK
    # HTML conventionally uses "q" for query
    q = request.args.get("q", "").strip()
    flights_upcoming = []

    if q:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        try:
            sql = """
                SELECT
                    airline_name,
                    flight_num,
                    departure_airport,
                    departure_time,
                    arrival_airport,
                    arrival_time,
                    status
                FROM flight 
                JOIN airport
                WHERE status LIKE 'upcoming'
                  AND (departure_airport LIKE %s OR arrival_airport LIKE %s
                  OR )
                ORDER BY departure_time
            """
            # Execute the query with the provided airport code for both departure and arrival
            cursor.execute(sql, (q, q))
            flights_upcoming = cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    return render_template("public_search_upcoming.html", flights=flights_upcoming, q=q)

@public_bp.route("/search/in_progress", methods=["GET"])
def public_search_in_progress():
    q = request.args.get("q", "").strip()
    flights_in_progress = []



@public_bp.route("/status")
def public_status():
    return render_template("public_status.html")
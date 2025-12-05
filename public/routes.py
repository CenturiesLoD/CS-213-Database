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
                    flight.airline_name,
                    flight.flight_num,
                    flight.departure_airport,
                    flight.departure_time,
                    flight.arrival_airport,
                    flight.arrival_time,
                    flight.status
                FROM flight
                JOIN airport
                ON flight.departure_airport = airport.airport_name
                OR flight.arrival_airport = airport.airport_name
                WHERE flight.status = 'upcoming'
                AND (flight.departure_airport LIKE %s OR flight.arrival_airport LIKE %s)
                ORDER BY flight.departure_time;

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

    if q:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)



@public_bp.route("/status")
def public_status():
    return render_template("public_status.html")
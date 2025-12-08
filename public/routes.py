from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from db import get_db_connection
import pymysql

public_bp = Blueprint("public", __name__)

#These are for the urls that the agent will use to access different pages
#Urls lead to corresponding pages in the templates folder

#TO BE SHARED WITH CUSTOMER SINCE THEY BOTH SEARCHING
#GIVING UP ON THE IDEA CUSTOMER WILL GET THEIR OWN SEARCH FUNCTION
def query_upcoming_flights(qArrive, qDepart, qCity, qDate):

    pass

@public_bp.route("/search/upcoming", methods=["GET"])
def public_search_upcoming():
    # q will come from the search bar, e.g. ?q=JFK
    # HTML conventionally uses "q" for query
    qArrive = request.args.get("qArrive", "").strip()
    qDepart = request.args.get("qDepart", "").strip()
    qCityArr   = request.args.get("qCityArr",   "").strip()
    qCityDep = request.args.get("qCityDep", "").strip()
    qDate   = request.args.get("qDate",   "").strip()

    # introduce wild cards so if it appears, it's accepted (same as public)
    patternArrive = f"%{qArrive.lower()}%" if qArrive else ""
    patternDepart = f"%{qDepart.lower()}%" if qDepart else ""
    patternCityArr   = f"%{qCityArr.lower()}%"   if qCityArr   else ""
    patternCityDep = f"%{qCityDep.lower()}%"   if qCityDep   else ""
    patternDate   = f"%{qDate}%"      if qDate   else ""
    flights_upcoming = []

    if qArrive or qDepart or qCityArr or qCityDep or qDate:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        try:
            sql = """
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
                -- Airport filter
                -- patternArrive, patternArrive, patternDepart, patternDepart, 
                AND (%s = '' OR LOWER(f.arrival_airport)   LIKE %s)
                AND (%s = '' OR LOWER(f.departure_airport) LIKE %s)

                
                -- City filter: match ANY airport in that city for either leg
                -- patternCityArr, patternCityArr, patternCityDep, patternCityDep,
                AND (%s = '' OR LOWER(arr_city.city_name) LIKE %s)
                AND( %s = '' OR LOWER(dep_city.city_name) LIKE %s )

                -- Time filter
                -- patternDate, patternDate, patternDate, patternDate
                AND (%s = '' OR LOWER(f.arrival_time)      LIKE %s)
                AND (%s = '' OR LOWER(f.departure_time)    LIKE %s)
                ORDER BY f.departure_time;


                """
            #flash("Hi")
            cursor.execute(
                sql,
                (patternArrive, patternArrive, 
                patternDepart, patternDepart, 
                patternCityArr, patternCityArr, 
                patternCityDep, patternCityDep,
                patternDate, patternDate, 
                patternDate, patternDate),
            )
            #old debug stuff
            #flash(len(flights_upcoming))

            flights_upcoming = cursor.fetchall()
            #flash(len(flights_upcoming))

        finally:
            cursor.close()
            conn.close()

    return render_template("public_search_upcoming.html", 
                           flights=flights_upcoming, 
                           qArrive=qArrive, qDepart=qDepart, 
                           qCityArr=qCityArr, 
                           qCityDep = qCityDep, 
                           qDate=qDate)

@public_bp.route("/search/in_progress", methods=["GET"])
def public_search_in_progress():
    # Read query parameters from URL, e.g. /search/in_progress?airline=DemoAir1&flight_num=1001
    airline = request.args.get("airline", "").strip()
    flight_num = request.args.get("flight_num", "").strip()

    flights_in_progress = []

    if airline and flight_num:
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
                WHERE LOWER(airline_name) = %s
                  AND flight_num = %s
                  AND status = 'in-progress'
            """
            cursor.execute(sql, (airline.lower(), flight_num))
            flights_in_progress = cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    return render_template(
        "public_search_in_progress.html",
        flights=flights_in_progress,
        airline=airline,
        flight_num=flight_num,
    )

#Should handle cases when anyone signed in is searching from public search page
@public_bp.before_request
def _redirect_customer_from_public_search():
    # Only intercept for these public endpoints
    if session.get("user_type") == "customer" and request.endpoint in {
        "public.public_search_upcoming",


        #NOT NEEDED FOR NOWCAUSE YOU CANT BUY IN PROGRESS FLIGHTS
        #"public.public_search_in_progress",
    }:
    
        # Preserve current query params (qArrive, qDepart, qCity, qDate, etc.)
        args = request.args.to_dict(flat=True)  # MultiDict -> dict for url_for [web:304]
        return redirect(url_for("customer.search_flights", **args))
    elif session.get("user_type") == "agent" and request.endpoint in {
        "public.public_search_upcoming",}:
        args = request.args.to_dict(flat=True)  # MultiDict -> dict for url_for [web:304]
        return redirect(url_for("agent.search", **args))
    elif session.get("user_type") == "staff" and request.endpoint in {
        "public.public_search_upcoming",}:
        args = request.args.to_dict(flat=True)  # MultiDict -> dict for url_for [web:304]
        return redirect(url_for("staff.search", **args))

@public_bp.route("/status")
def public_status():
    return render_template("public_status.html")
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from db import get_db_connection
import pymysql

customer_bp = Blueprint("customer", __name__)

#These are for the urls that the agent will use to access different pages
#Urls lead to corresponding pages in the templates folder

#12/5 19:25, working on dashboard
#12/7 DASHBOARD ONLY SHOWS UPCOMING FLIGHTS
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
                f.status,
                COUNT(*) AS ticket_amount
            FROM purchases p
            JOIN ticket t
            ON p.ticket_id = t.ticket_id
            JOIN flight f
            ON t.airline_name = f.airline_name
            AND t.flight_num   = f.flight_num
            WHERE p.customer_email = %s
            AND f.status = 'upcoming'
            GROUP BY
                f.airline_name,
                f.flight_num,
                f.departure_airport,
                f.departure_time,
                f.arrival_airport,
                f.arrival_time,
                f.status
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
        #so inputs stay in the search box after search
        qArrive = request.args.get("qArrive", "").strip()
        qDepart = request.args.get("qDepart", "").strip()
        qCityArr   = request.args.get("qCityArr", "").strip()
        qCityDep = request.args.get("qCityDep", "").strip()
        qDate   = request.args.get("qDate", "").strip()
        return render_template(
            "customer/search.html",
            qArrive=qArrive,
            qDepart=qDepart,
            qCityArr=qCityArr,
            qCityDep=qCityDep,
            qDate=qDate,
        )

    # Same field names as public search: qArrive, qDepart, qCity, qDate
    qArrive = request.form.get("qArrive", "").strip()
    qDepart = request.form.get("qDepart", "").strip()
    qCityArr   = request.form.get("qCityArr",   "").strip()
    qCityDep = request.form.get("qCityDep", "").strip()
    qDate   = request.form.get("qDate",   "").strip()

    # introduce wild cards so if it appears, it's accepted (same as public)
    patternArrive = f"%{qArrive.lower()}%" if qArrive else ""
    patternDepart = f"%{qDepart.lower()}%" if qDepart else ""
    patternCityArr   = f"%{qCityArr.lower()}%"   if qCityArr   else ""
    patternCityDep = f"%{qCityDep.lower()}%"   if qCityDep   else ""
    patternDate   = f"%{qDate}%"      if qDate   else ""

    flights = []

    #updated
    if not (qArrive or qDepart or qCityArr or qCityDep or qDate):
        #flash(qCityDep)
        flash("Please enter at least one search field.")
        return redirect(url_for("customer.search_flights"))

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        # SQL copied from public_search_upcoming: upcoming flights filtered by
        # arrival/departure airport, city, and date. [file:281]
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

        cursor.execute(
            sql,
            (patternArrive, patternArrive, 
            patternDepart, patternDepart, 
            patternCityArr, patternCityArr, patternCityDep, patternCityDep,
            patternDate, patternDate, 
            patternDate, patternDate),
        )
        flights = cursor.fetchall()

        # Same search behavior as public, but customer template can show Buy buttons.
        return render_template(
            "customer/search_results.html",
            results=flights,
            qArrive=qArrive,
            qDepart=qDepart,
            qCityArr=qCityArr,
            qCityDep = qCityDep,
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

#SHOULD SHOW ALL FLIGHTS THE CUSTOMER HAS EVER PURCHASED
@customer_bp.route("/flights")
def my_flights():
    # Require login as customer
    if session.get("user_type") != "customer":
        flash("You must log in as a customer to view your flights.")
        return redirect(url_for("auth.login"))

    customer_email = session.get("email")

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        sql = """
        SELECT
            p.ticket_id,
            p.purchase_date,
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
        WHERE p.customer_email = %s
        ORDER BY f.departure_time DESC;
        """
        cursor.execute(sql, (customer_email,))
        purchases = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template(
        "customer/flights.html",
        purchases=purchases,
        customer_email=customer_email,
    )


@customer_bp.route("/purchase", methods=["POST"])
def purchase():
    if session.get("user_type") != "customer":
        flash("You must log in as a customer to purchase.")
        return redirect(url_for("auth.login"))
    
    #gets relevant info from browser
    #session is from login
    customer_email = session.get("email")
    airline_name = request.form.get("airline_name", "").strip()
    flight_num   = request.form.get("flight_num", "").strip()
    airplane_id  = request.form.get("airplane_id", "").strip()

    if not (airline_name and flight_num and airplane_id):
        flash("Missing flight data.")
        return redirect(url_for("customer.search_flights"))

    conn = get_db_connection()
    conn.begin()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        # 1) Read current price and capacity (enforce server-side pricing/capacity)
        sql_flight = """
            SELECT f.price, f.status, a.seat_capacity AS seat_capacity
            FROM flight f
            JOIN airplane a
              ON a.airline_name = f.airline_name
             AND a.airplane_id  = f.airplane_id
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

        # Generate next ticket_id inside the transaction
        cursor.execute("SELECT COALESCE(MAX(ticket_id), 0) AS max_id FROM ticket FOR UPDATE")
        # flash("HI")
        next_id = cursor.fetchone()["max_id"] + 1

        # # Insert ticket with explicit ticket_id
        # cursor.execute(
        #     "INSERT INTO ticket (ticket_id, airline_name, flight_num) VALUES (%s, %s, %s)",
        #     (next_id, airline_name, flight_num),
        # )
        # ticket_id = next_id
        # flash("HI2")

        # 2) Count tickets sold for this flight (lock to prevent over-sell)
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

        # 3) Create ticket (assumes AUTO_INCREMENT ticket_id)
        #flash("HI")

        cursor.execute(
            "INSERT INTO ticket (ticket_id, airline_name, flight_num) VALUES (%s, %s, %s)",
            (next_id, airline_name, flight_num),
        )

        # 4) Insert purchase with server-side price
        cursor.execute(
            "INSERT INTO purchases (ticket_id, customer_email, purchase_date) "
            "VALUES (%s, %s, CURDATE())",
            (next_id, customer_email),
        )

        conn.commit()
        seats_left = row["seat_capacity"] - sold
        flash(f"Purchased {airline_name} flight {flight_num} at {price}. Seats left: {seats_left}")


        #CONFIRMATION PAGE customer/purchase.html
        seats_left_after = seat_capacity - (sold + 1)
        return render_template(
            "customer/purchase.html",
            confirmed=True,
            #next_id is ticket_id in effect
            ticket_id=next_id,
            airline_name=airline_name, flight_num=flight_num, airplane_id=airplane_id,
            price=price,
            # departure_airport=row["departure_airport"], departure_time=row["departure_time"],
            # arrival_airport=row["arrival_airport"],   arrival_time=row["arrival_time"],
            seat_capacity=seat_capacity, sold=sold + 1, seats_left=seats_left_after
        )
        #return redirect(url_for("customer.dashboard"))
    except Exception as e:
        conn.rollback()
        flash(f"Purchase failed: {e}")
        return redirect(url_for("customer.search_flights"))
    finally:
        cursor.close()
        conn.close()
    #return render_template("customer/purchase.html")

#12/7 2:00 AM spending page. 
@customer_bp.route("/spending/default")
def spending_default():
    if session.get("user_type") != "customer":
        flash("You must log in as a customer to view spending.")
        return redirect(url_for("auth.login"))

    customer_email = session.get("email")

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        # 1) Total spending in last 12 months
        sql_total = """
            SELECT COALESCE(SUM(f.price), 0) AS total_spending
            FROM purchases p
            JOIN ticket t
              ON p.ticket_id = t.ticket_id
            JOIN flight f
              ON t.airline_name = f.airline_name
             AND t.flight_num   = f.flight_num
            WHERE p.customer_email = %s
              AND p.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
        """
        cursor.execute(sql_total, (customer_email,))
        row = cursor.fetchone()
        total_spending_12m = row["total_spending"]

        # 2) Month-by-month spending last 6 months (for bar chart)
        # year_month IS RESERVED KEYWORD
        sql_months = """
            SELECT
                DATE_FORMAT(p.purchase_date, '%%Y-%%m') AS yr_mth,
                SUM(f.price) AS month_total
            FROM purchases p
            JOIN ticket t
              ON p.ticket_id = t.ticket_id
            JOIN flight f
              ON t.airline_name = f.airline_name
             AND t.flight_num   = f.flight_num
            WHERE p.customer_email = %s
              AND p.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            GROUP BY DATE_FORMAT(p.purchase_date, '%%Y-%%m')
            ORDER BY yr_mth
        """
        cursor.execute(sql_months, (customer_email,))
        rows = cursor.fetchall()

        labels = [r["yr_mth"] for r in rows]
        values = [float(r["month_total"]) for r in rows]
    except Exception as e:
        flash(f"Failed to load spending data: {e}")
        return redirect(url_for("customer.dashboard"))
    finally:
        cursor.close()
        conn.close()

    return render_template(
        "customer/spending_default.html",
        total_spending_12m=total_spending_12m,
        labels=labels,
        values=values,
    )


@customer_bp.route("/spending/custom", methods=["GET", "POST"])
def spending_custom():
    if session.get("user_type") != "customer":
        flash("You must log in as a customer to view spending.")
        return redirect(url_for("auth.login"))

    customer_email = session.get("email")

    # q* values come from dropdowns
    qStartYear = ""
    qStartMonth = ""
    qEndYear = ""
    qEndMonth = ""

    qTotalSpending = None
    labels = []
    values = []

    if request.method == "POST":
        qStartYear = request.form.get("qStartYear", "").strip()
        qStartMonth = request.form.get("qStartMonth", "").strip()
        qEndYear = request.form.get("qEndYear", "").strip()
        qEndMonth = request.form.get("qEndMonth", "").strip()

        # Basic validation
        if not (qStartYear and qStartMonth and qEndYear and qEndMonth):
            flash("Please choose both start and end months.")
            return redirect(url_for("customer.spending_custom"))

        # Build YYYY-MM strings from the dropdowns
        qStart = f"{qStartYear}-{qStartMonth.zfill(2)}"
        qEnd = f"{qEndYear}-{qEndMonth.zfill(2)}"

        # Ensure start <= end (lexicographic works for YYYY-MM)
        if qStart > qEnd:
            flash("Start month must be before or equal to end month.")
            return redirect(url_for("customer.spending_custom"))

        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        try:
            # 1) Total spending from first day of start month through
            #    last day of end month.
            sql_total = """
                SELECT COALESCE(SUM(f.price), 0) AS total_spending
                FROM purchases p
                JOIN ticket t
                  ON p.ticket_id = t.ticket_id
                JOIN flight f
                  ON t.airline_name = f.airline_name
                 AND t.flight_num   = f.flight_num
                WHERE p.customer_email = %s
                  AND p.purchase_date BETWEEN
                        DATE(CONCAT(%s, '-01'))
                    AND LAST_DAY(DATE(CONCAT(%s, '-01')))
            """
            cursor.execute(sql_total, (customer_email, qStart, qEnd))
            row = cursor.fetchone()
            qTotalSpending = row["total_spending"]

            # 2) Month-by-month spending in that full-month range
            sql_months = """
                SELECT
                    DATE_FORMAT(p.purchase_date, '%%Y-%%m') AS yr_mth,
                    SUM(f.price) AS month_total
                FROM purchases p
                JOIN ticket t
                  ON p.ticket_id = t.ticket_id
                JOIN flight f
                  ON t.airline_name = f.airline_name
                 AND t.flight_num   = f.flight_num
                WHERE p.customer_email = %s
                  AND p.purchase_date BETWEEN
                        DATE(CONCAT(%s, '-01'))
                    AND LAST_DAY(DATE(CONCAT(%s, '-01')))
                GROUP BY DATE_FORMAT(p.purchase_date, '%%Y-%%m')
                ORDER BY yr_mth
            """
            cursor.execute(sql_months, (customer_email, qStart, qEnd))
            rows = cursor.fetchall()

            labels = [r["yr_mth"] for r in rows]
            values = [float(r["month_total"]) for r in rows]
        except Exception as e:
            flash(f"Failed to load custom spending data: {e}")
            return redirect(url_for("customer.dashboard"))
        finally:
            cursor.close()
            conn.close()

    return render_template(
        "customer/spending_custom.html",
        qStartYear=qStartYear,
        qStartMonth=qStartMonth,
        qEndYear=qEndYear,
        qEndMonth=qEndMonth,
        qTotalSpending=qTotalSpending,
        labels=labels,
        values=values,
    )

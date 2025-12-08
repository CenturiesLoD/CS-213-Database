# staff/admin_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_db_connection
import pymysql


admin_bp = Blueprint("admin_staff", __name__, url_prefix="/staff/admin")

# Helper: require staff admin
def _require_staff_admin():
    """
    Ensure the current logged-in user is an airline staff member
    with admin (or 'both') privileges.
    If the check fails, return a redirect response.
    If everything is okay, return None.
    """
    # Must be logged in as staff
    if session.get("user_type") != "staff":
        flash("Staff login required.", "danger")
        return redirect(url_for("auth.login"))

    username = session.get("username")
    airline_name = session.get("airline_name")

    if not username or not airline_name:
        flash("Missing staff session information.", "danger")
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    try:
        cur.execute(
            """
            SELECT role
            FROM airline_staff
            WHERE username = %s AND airline_name = %s
            """,
            (username, airline_name),
        )
        row = cur.fetchone()
    finally:
        cur.close()
        conn.close()

    if not row:
        flash("Staff account not found for this airline.", "danger")
        return redirect(url_for("auth.login"))

    role = row["role"]
    # Allow both pure admins and 'both' (admin + operator)
    if role not in ("admin", "both"):
        flash("Admin privileges required for this action.", "danger")
        return redirect(url_for("staff.dashboard"))

    # All good
    return None

@admin_bp.route("/add_airport", methods=["GET", "POST"])
def add_airport():
    # 权限检查
    guard = _require_staff_admin()
    if guard:
        return guard

    if request.method == "POST":
        airport_name = (request.form.get("airport_name") or "").strip()
        airport_city = (request.form.get("airport_city") or "").strip()

        if not airport_name or not airport_city:
            flash("Airport name and city are required.", "danger")
            return redirect(url_for("admin_staff.add_airport"))

        conn = get_db_connection()
        try:
            cur = conn.cursor()

            # 先确保 city 存在（anti-auto 的 city 表）
            cur.execute(
                "INSERT IGNORE INTO city (city_name) VALUES (%s)",
                (airport_city,)
            )

            # 再插 airport
            cur.execute(
                """
                INSERT INTO airport (airport_name, airport_city)
                VALUES (%s, %s)
                """,
                (airport_name, airport_city),
            )
            conn.commit()
            flash(f"Airport {airport_name} added.", "success")
        except pymysql.err.IntegrityError as e:
            conn.rollback()
            flash(f"Failed to add airport: {e.args[1]}", "danger")
        finally:
            cur.close()
            conn.close()

        return redirect(url_for("admin_staff.add_airport"))

    # GET
    return render_template("staff/admin_add_airport.html")


@admin_bp.route("/add_airplane", methods=["GET", "POST"])
def add_airplane():
    guard = _require_staff_admin()
    if guard:
        return guard

    airline_name = session.get("airline_name")

    if request.method == "POST":
        airplane_id_raw = (request.form.get("airplane_id") or "").strip()
        seat_capacity_raw = (request.form.get("seat_capacity") or "").strip()

        if not airplane_id_raw or not seat_capacity_raw:
            flash("Airplane ID and seat capacity are required.", "danger")
            return redirect(url_for("admin_staff.add_airplane"))

        try:
            airplane_id = int(airplane_id_raw)
            seat_capacity = int(seat_capacity_raw)
        except ValueError:
            flash("Airplane ID and seat capacity must be integers.", "danger")
            return redirect(url_for("admin_staff.add_airplane"))

        conn = get_db_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO airplane (airline_name, airplane_id, seat_capacity)
                VALUES (%s, %s, %s)
                """,
                (airline_name, airplane_id, seat_capacity),
            )
            conn.commit()
            flash(f"Airplane {airline_name}-{airplane_id} added.", "success")
        except pymysql.err.IntegrityError as e:
            conn.rollback()
            flash(f"Failed to add airplane: {e.args[1]}", "danger")
        finally:
            cur.close()
            conn.close()

        return redirect(url_for("admin_staff.add_airplane"))

    return render_template("staff/admin_add_airplane.html", airline_name=airline_name)


@admin_bp.route("/create_flight", methods=["GET", "POST"])
def create_flight():
    guard = _require_staff_admin()
    if guard:
        return guard

    airline_name = session.get("airline_name")

    conn = get_db_connection()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    # 用于表单下拉：现有机场、现有该航空的飞机
    cur.execute("SELECT airport_name FROM airport ORDER BY airport_name")
    airports = [row["airport_name"] for row in cur.fetchall()]

    cur.execute(
        "SELECT airplane_id FROM airplane WHERE airline_name = %s ORDER BY airplane_id",
        (airline_name,),
    )
    airplane_ids = [row["airplane_id"] for row in cur.fetchall()]

    if request.method == "POST":
        flight_num_raw = (request.form.get("flight_num") or "").strip()
        departure_airport = (request.form.get("departure_airport") or "").strip()
        arrival_airport = (request.form.get("arrival_airport") or "").strip()
        departure_time = (request.form.get("departure_time") or "").strip()
        arrival_time = (request.form.get("arrival_time") or "").strip()
        price_raw = (request.form.get("price") or "").strip()
        airplane_id_raw = (request.form.get("airplane_id") or "").strip()
        status = (request.form.get("status") or "upcoming").strip() or "upcoming"

        if not (flight_num_raw and departure_airport and arrival_airport and
                departure_time and arrival_time and price_raw and airplane_id_raw):
            flash("All fields are required.", "danger")
            cur.close()
            conn.close()
            return redirect(url_for("admin_staff.create_flight"))

        try:
            flight_num = int(flight_num_raw)
            price = float(price_raw)
            airplane_id = int(airplane_id_raw)
        except ValueError:
            flash("Flight number, price, and airplane ID must be numeric.", "danger")
            cur.close()
            conn.close()
            return redirect(url_for("admin_staff.create_flight"))

        try:
            cur.execute(
                """
                INSERT INTO flight
                    (airline_name, flight_num,
                     departure_airport, departure_time,
                     arrival_airport, arrival_time,
                     price, status, airplane_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    airline_name,
                    flight_num,
                    departure_airport,
                    departure_time,
                    arrival_airport,
                    arrival_time,
                    price,
                    status,
                    airplane_id,
                ),
            )
            conn.commit()
            flash(f"Flight {airline_name} {flight_num} created.", "success")
        except pymysql.err.IntegrityError as e:
            conn.rollback()
            flash(f"Failed to create flight: {e.args[1]}", "danger")

        cur.close()
        conn.close()
        return redirect(url_for("admin_staff.create_flight"))

    # GET
    cur.close()
    conn.close()
    return render_template(
        "staff/admin_create_flight.html",
        airline_name=airline_name,
        airports=airports,
        airplane_ids=airplane_ids,
    )



@admin_bp.route("/authorize_agent", methods=["GET", "POST"])
def authorize_agent():
    guard = _require_staff_admin()
    if guard:
        return guard

    airline_name = session.get("airline_name")

    conn = get_db_connection()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    if request.method == "POST":
        agent_email = (request.form.get("agent_email") or "").strip()

        if not agent_email:
            flash("Agent email is required.", "danger")
        else:
            # 确认 agent 存在
            cur.execute(
                "SELECT email FROM booking_agent WHERE email = %s",
                (agent_email,),
            )
            row = cur.fetchone()
            if not row:
                flash("No such booking agent email.", "danger")
            else:
                try:
                    cur.execute(
                        """
                        INSERT IGNORE INTO agent_airline_authorization
                            (agent_email, airline_name)
                        VALUES (%s, %s)
                        """,
                        (agent_email, airline_name),
                    )
                    conn.commit()
                    flash(
                        f"Agent {agent_email} authorized for {airline_name}.",
                        "success",
                    )
                except pymysql.err.IntegrityError as e:
                    conn.rollback()
                    flash(f"Failed to authorize: {e.args[1]}", "danger")

    # 展示当前 airline 已授权的 agent
    cur.execute(
        """
        SELECT agent_email
        FROM agent_airline_authorization
        WHERE airline_name = %s
        ORDER BY agent_email
        """,
        (airline_name,),
    )
    authorized_agents = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "staff/admin_authorize_agent.html",
        airline_name=airline_name,
        authorized_agents=authorized_agents,
    )
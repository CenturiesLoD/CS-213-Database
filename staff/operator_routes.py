from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from db import get_db_connection
import pymysql


operator_bp = Blueprint("operator_staff", __name__)

@operator_bp.route("/update_status", methods=["GET", "POST"])
def update_status():
    # Must be logged in as airline staff
    if session.get("user_type") != "staff":
        flash("You must log in as airline staff to access this page.")
        return redirect(url_for("auth.login"))

    # Must have operator permission (operator or both)
    role = session.get("role")
    if role not in ("operator", "both"):
        flash("You do not have operator permissions.")
        return redirect(url_for("staff.dashboard"))

    airline_name = session.get("airline_name")
    if not airline_name:
        flash("No airline found for this staff member.")
        return redirect(url_for("staff.dashboard"))

    flights = []

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        # If this is a POST, attempt to update the status
        if request.method == "POST":
            flight_num = request.form.get("flight_num", "").strip()
            new_status = request.form.get("status", "").strip()

            allowed_statuses = {"upcoming", "in-progress", "delayed", "canceled"}
            if not flight_num or new_status not in allowed_statuses:
                flash("Invalid flight or status selected.")
            else:
                sql_update_status = """
                    UPDATE flight
                    SET status = %s
                    WHERE airline_name = %s
                      AND flight_num = %s
                """
                try:
                    cursor.execute(sql_update_status, (new_status, airline_name, flight_num))
                    conn.commit()
                    if cursor.rowcount == 0:
                        flash("No such flight found for your airline.")
                    else:
                        flash("Flight status updated successfully.")
                except Exception as e:
                    conn.rollback()
                    flash(f"Failed to update flight status: {e}")

        # Always load the list of flights for this airline
        sql_list_flights = """
            SELECT
                flight_num,
                departure_airport,
                departure_time,
                arrival_airport,
                arrival_time,
                status
            FROM flight
            WHERE airline_name = %s
            ORDER BY departure_time DESC
        """
        cursor.execute(sql_list_flights, (airline_name,))
        flights = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return render_template(
        "staff/operator_update_status.html",
        flights=flights,
        airline_name=airline_name,
    )
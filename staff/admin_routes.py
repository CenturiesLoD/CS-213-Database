from flask import Blueprint, render_template

admin_bp = Blueprint("admin_staff", __name__)

@admin_bp.route("/add_airport")
def add_airport():
    return render_template("staff/admin_add_airport.html")

@admin_bp.route("/add_airplane")
def add_airplane():
    return render_template("staff/admin_add_airplane.html")

@admin_bp.route("/create_flight")
def create_flight():
    return render_template("staff/admin_create_flight.html")

@admin_bp.route("/authorize_agent")
def authorize_agent():
    return render_template("staff/admin_authorize_agent.html")
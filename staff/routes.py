from flask import Blueprint, render_template

staff_bp = Blueprint("staff", __name__)

@staff_bp.route("/dashboard")
def dashboard():
    return render_template("staff/dashboard.html")

@staff_bp.route("/next30")
def next30():
    return render_template("staff/flights_next30.html")

@staff_bp.route("/search")
def search():
    return render_template("staff/flight_search.html")

@staff_bp.route("/passengers")
def passengers():
    return render_template("staff/passenger_list.html")

@staff_bp.route("/customer_history")
def customer_history():
    return render_template("staff/customer_history.html")
from flask import Blueprint, render_template

customer_bp = Blueprint("customer", __name__)

@customer_bp.route("/dashboard")
def dashboard():
    return render_template("customer/dashboard.html")

@customer_bp.route("/search")
def search_flights():
    return render_template("customer/search.html")

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
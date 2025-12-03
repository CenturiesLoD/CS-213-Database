from flask import Blueprint, render_template

agent_bp = Blueprint("agent", __name__)

@agent_bp.route("/dashboard")
def dashboard():
    return render_template("agent/dashboard.html")

@agent_bp.route("/flights")
def flights():
    return render_template("agent/flights.html")

@agent_bp.route("/search")
def search():
    return render_template("agent/search.html")

@agent_bp.route("/analytics/commission")
def commission():
    return render_template("agent/analytics_commission.html")

@agent_bp.route("/analytics/top_customers")
def top_customers():
    return render_template("agent/analytics_top_customers.html")
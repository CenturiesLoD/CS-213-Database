from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from db import get_db_connection
import pymysql

agent_bp = Blueprint("agent", __name__)

#These are for the urls that the agent will use to access different pages
#Urls lead to corresponding pages in the templates folder


@agent_bp.route("/dashboard")
def dashboard():
    # For now, just render a simple dashboard.
    # You can later add summaries (tickets sold, commission, etc.).
    if session.get("user_type") != "agent":
        flash("You must log in as a booking agent to access this page.")
        return redirect(url_for("auth.login"))
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
from flask import Blueprint, render_template

public_bp = Blueprint("public", __name__)

@public_bp.route("/search")
def public_search():
    return render_template("public_search.html")

@public_bp.route("/status")
def public_status():
    return render_template("public_status.html")
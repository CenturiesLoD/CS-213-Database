from flask import Blueprint, render_template

operator_bp = Blueprint("operator_staff", __name__)

@operator_bp.route("/update_status")
def update_status():
    return render_template("staff/operator_update_status.html")
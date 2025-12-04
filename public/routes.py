from flask import Blueprint, render_template

public_bp = Blueprint("public", __name__)

#These are for the urls that the agent will use to access different pages
#Urls lead to corresponding pages in the templates folder
@public_bp.route("/search")
def public_search():
    return render_template("public_search.html")

@public_bp.route("/status")
def public_status():
    return render_template("public_status.html")
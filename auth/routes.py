from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

from db import get_db_connection

auth_bp = Blueprint("auth", __name__)

#These are for the urls that the agent will use to access different pages
#Urls lead to corresponding pages in the templates folder
@auth_bp.route("/register")
def register():
    #will have different options for different user types
    return render_template("auth/choose_user_type.html")

#registration for customers
@auth_bp.route("/register/customer", methods=["GET", "POST"])
def register_customer():
    if request.method == "GET":
        #got form from register_customer.html
        return render_template("auth/register_customer.html")

    email = request.form.get("email")
    password = generate_password_hash(request.form.get("password"))
    name = request.form.get("name")
    building = request.form.get("building_number")
    street = request.form.get("street")
    city = request.form.get("city")
    state = request.form.get("state")
    phone = request.form.get("phone_number")
    passport_num = request.form.get("passport_number")
    passport_exp = request.form.get("passport_expiration")
    passport_country = request.form.get("passport_country")
    dob = request.form.get("date_of_birth")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql = """
            INSERT INTO customer (
                email, name, password,
                building_number, street, city, state,
                phone_number, passport_number, passport_expiration,
                passport_country, date_of_birth
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        cursor.execute(sql, (email, name, password,
                             building, street, city, state,
                             phone, passport_num, passport_exp,
                             passport_country, dob))
        conn.commit()
        flash("Customer registered! Please log in.")
        return redirect(url_for("auth.login"))
    except Exception as e:
        conn.rollback()
        flash(str(e))
        #flash("STUPID")
        return redirect(url_for("auth.register_customer"))
    finally:
        cursor.close()
        conn.close()


@auth_bp.route("/register/agent", methods=["GET", "POST"])
def register_agent():
    if request.method == "GET":
        return render_template("auth/register_agent.html")

    email = request.form.get("email")
    password = generate_password_hash(request.form.get("password"))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO booking_agent (email, password) VALUES (%s,%s)", (email, password))
        conn.commit()
        flash("Agent registered! Please log in.")
        return redirect(url_for("auth.login"))
    except Exception as e:
        conn.rollback()
        flash(str(e))
        return redirect(url_for("auth.register_agent"))
    finally:
        cursor.close()
        conn.close()


@auth_bp.route("/register/staff", methods=["GET", "POST"])
def register_staff():
    if request.method == "GET":
        return render_template("auth/register_staff.html")

    username = request.form.get("username")
    password = generate_password_hash(request.form.get("password"))
    first = request.form.get("first_name")
    last = request.form.get("last_name")
    dob = request.form.get("date_of_birth")
    airline = request.form.get("airline_name")
    role = request.form.get("role")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql = """
            INSERT INTO airline_staff (
                username, password, first_name, last_name,
                date_of_birth, airline_name, role
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """
        cursor.execute(sql, (username, password, first, last, dob, airline, role))
        conn.commit()
        flash("Staff registered! Please log in.")
        return redirect(url_for("auth.login"))
    except Exception as e:
        conn.rollback()
        flash(str(e))
        return redirect(url_for("auth.register_staff"))
    finally:
        cursor.close()
        conn.close()


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    #COULD BE IMRPOVED MAYBE?
    # If already logged in, don't allow logging in again
    if session.get("user_type"):
        flash("You are already logged in. Please log out first if you want to switch accounts.")
        user_type = session["user_type"]
        if user_type == "customer":
            return redirect(url_for("customer.dashboard"))
        elif user_type == "agent":
            return redirect(url_for("agent.dashboard"))
        elif user_type == "staff":
            return redirect(url_for("staff.dashboard"))

    if request.method == "GET":
        return render_template("login.html")
    
    if request.method == "GET":
        return render_template("login.html")

    user_type = request.form.get("user_type")  # customer / agent / staff
    identifier = request.form.get("identifier")  # email or username
    password = request.form.get("password")

    if not user_type or not identifier or not password:
        flash("User type, email/username and password are required.")
        return render_template("login.html")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if user_type == "customer":
            sql = "SELECT email, password, name FROM customer WHERE email = %s"
            cursor.execute(sql, (identifier,))
            row = cursor.fetchone()

            if row is None:
                flash("Customer not found.")
                return render_template("login.html")

            # row 现在是 dict，如：
            # {'email': 'xxx', 'password': 'hashed...', 'name': 'Jenson'}
            email = row["email"]
            password_hash = row["password"]
            name = row["name"]

            if not check_password_hash(password_hash, password):
                flash("Incorrect password.")
                return render_template("login.html")

            # success — 写入 session
            session.clear()
            session["user_type"] = "customer"
            session["email"] = email
            session["name"] = name

            return redirect(url_for("customer.dashboard"))

        elif user_type == "agent":
            sql = "SELECT email, password FROM booking_agent WHERE email = %s"
            cursor.execute(sql, (identifier,))
            row = cursor.fetchone()
            if not row:
                flash("Agent not found.")
                return render_template("login.html")

            email = row["email"]
            password_hash = row["password"]

            if not check_password_hash(password_hash, password):
                flash("Incorrect password.")
                return render_template("login.html")

            session.clear()
            session["user_type"] = "agent"
            session["email"] = email

            return redirect(url_for("agent.dashboard"))

        elif user_type == "staff":
            sql = """
                SELECT username, password, airline_name, role
                FROM airline_staff
                WHERE username = %s
            """
            cursor.execute(sql, (identifier,))
            row = cursor.fetchone()
            if not row:
                flash("Staff not found.")
                return render_template("login.html")

            username = row["username"]
            password_hash = row["password"]
            airline_name = row["airline_name"]
            role = row["role"]

            if not check_password_hash(password_hash, password):
                flash("Incorrect password.")
                return render_template("login.html")

            session.clear()
            session["user_type"] = "staff"
            session["username"] = username
            session["airline_name"] = airline_name
            session["role"] = role  # admin / operator / both

            return redirect(url_for("staff.dashboard"))

        else:
            flash("Unknown user type.")
            return render_template("login.html")

    except Exception as e:
        flash(f"Login failed: {e}")
        #flash("WHAT")

        return render_template("login.html")

    finally:
        cursor.close()
        conn.close()

#TEST TO SEE SESSION CONTENTS
from flask import jsonify
@auth_bp.route("/debug_session")
def debug_session():
    return jsonify(dict(session))

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("home"))
    # 注意：这里假设 app.py 里的主页函数名字是 home()
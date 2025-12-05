# app.py
# app.py
from flask import Flask, render_template
# Blueprint imports
from auth.routes import auth_bp
from public.routes import public_bp
from customer.routes import customer_bp
from agent.routes import agent_bp
from staff.routes import staff_bp
from staff.admin_routes import admin_bp
from staff.operator_routes import operator_bp
# Flask：主框架
# render_template：用来渲染 templates 文件夹里的 HTML 模板

from db import get_db_connection


# 创建 Flask 应用对象
# __name__ 是当前模块名，Flask 用它来定位静态文件、模板文件等
app = Flask(__name__)
app.config['SECRET_KEY'] = 'replace_with_real_secret'

# Register blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(public_bp, url_prefix="/public")
app.register_blueprint(customer_bp, url_prefix="/customer")
app.register_blueprint(agent_bp, url_prefix="/agent")
app.register_blueprint(staff_bp, url_prefix="/staff")
app.register_blueprint(admin_bp, url_prefix="/staff/admin")
app.register_blueprint(operator_bp, url_prefix="/staff/operator")

@app.route("/")
def home():
    """
    frontpage
    1. get all airline from db
    2. give to index.html for rendering
    """
    # 1. connect database
    conn = get_db_connection()
    cursor = conn.cursor()

    # 2. run SQL
    cursor.execute("SELECT airline_name FROM airline")

    # 3. list with each element a tuple
    rows = cursor.fetchall()

    # 4. shut down
    cursor.close()
    conn.close()

    # 5. send results to template
    # airlines = ["xxx", "yyy"] 
    airlines = [row["airline_name"] for row in rows]

    return render_template("index.html", airlines=airlines)



if __name__ == "__main__":
    # debug=True：
    app.run(debug=True)
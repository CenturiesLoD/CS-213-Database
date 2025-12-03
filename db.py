# db.py
import pymysql


def get_db_connection():
    """
    建立并返回一个数据库连接对象。
    每次需要访问数据库时，就调用这个函数拿到一个新的连接。
    用完记得关闭！
    """
    conn = pymysql.connect(
        host="localhost",        #
        user="root",             # 
        password="your_password",# 
        database="air_reservation",  # 
        charset="utf8mb4",
        cursorclass=pymysql.cursors.Cursor  # 
    )
    return conn
#s are up to change
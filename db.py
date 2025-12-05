import pymysql
import os
from dotenv import load_dotenv 
load_dotenv()
def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="123456",  # 你刚设置的密码
        database="air_reservation",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.Cursor
    )
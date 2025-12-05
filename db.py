import pymysql
import os
from dotenv import load_dotenv 
load_dotenv()
def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),  # 你刚设置的密码
        database=os.getenv("DB_NAME"),
        charset=os.getenv("DB_CHARSET"),
        cursorclass=pymysql.cursors.DictCursor
    )
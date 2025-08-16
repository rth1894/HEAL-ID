import pytermgui as ptg
import pymysql

# MySQL connection (replace with your actual credentials)
db = pymysql.connect(
    host="localhost",
    user="python",
    password="Password@123",
    database="heal_id"
)
cursor = db.cursor()

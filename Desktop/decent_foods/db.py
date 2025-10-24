# db.py
import mysql.connector
from mysql.connector import Error

def create_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",      # 👈 Replace with your MySQL username
            password="11207107021Sam",  # 👈 Replace with your MySQL password
            database="waruguru_foods"
        )
        if connection.is_connected():
            print("✅ Database connection successful")
            return connection
    except Error as e:
        print(f"❌ Error: {e}")
        return None

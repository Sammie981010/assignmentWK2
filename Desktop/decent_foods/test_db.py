import mysql.connector

# Database connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_password",
    database="waruguru_foods"
)
cursor = conn.cursor()

# Required tables
required_tables = {"purchases", "sales"}

# Get existing tables
cursor.execute("SHOW TABLES")
existing_tables = {table[0] for table in cursor.fetchall()}

# Check
missing_tables = required_tables - existing_tables

if missing_tables:
    print("Missing tables:", missing_tables)
else:
    print("✅ All required tables exist.")

cursor.close()
conn.close()

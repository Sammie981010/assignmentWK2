import mysql.connector

# Database connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # Add your password
    database="decent_food"
)
cursor = conn.cursor()

# Table creation queries
table_queries = {
    "users": """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        )
    """,
    "purchases": """
        CREATE TABLE IF NOT EXISTS purchases (
            id INT AUTO_INCREMENT PRIMARY KEY,
            item_name VARCHAR(100) NOT NULL,
            quantity INT NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            total DECIMAL(10,2) NOT NULL,
            purchase_date DATE NOT NULL
        )
    """,
    "sales": """
        CREATE TABLE IF NOT EXISTS sales (
            id INT AUTO_INCREMENT PRIMARY KEY,
            customer_name VARCHAR(100) NOT NULL,
            item_name VARCHAR(100) NOT NULL,
            quantity INT NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            total DECIMAL(10,2) NOT NULL,
            sale_date DATE NOT NULL
        )
    """
}

# Check and create missing tables
cursor.execute("SHOW TABLES")
existing_tables = [table[0] for table in cursor.fetchall()]

for table_name, create_query in table_queries.items():
    if table_name not in existing_tables:
        cursor.execute(create_query)
        print(f"✅ Created missing table: {table_name}")
    else:
        print(f"✅ Table already exists: {table_name}")

conn.commit()
cursor.close()
conn.close()

print("🎯 Table check and creation complete!")

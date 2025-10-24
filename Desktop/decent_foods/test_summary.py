import mysql.connector
from datetime import datetime, timedelta

def test_database():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="11207107021Sam",
            database="decent_food"
        )
        
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("Available tables:", tables)
        
        # Check purchases structure
        cursor.execute("DESCRIBE purchases")
        purchase_cols = cursor.fetchall()
        print("Purchases columns:", purchase_cols)
        
        # Check sales structure  
        cursor.execute("DESCRIBE sales")
        sales_cols = cursor.fetchall()
        print("Sales columns:", sales_cols)
        
        # Test data
        cursor.execute("SELECT COUNT(*) FROM purchases")
        p_count = cursor.fetchone()[0]
        print(f"Purchases count: {p_count}")
        
        cursor.execute("SELECT COUNT(*) FROM sales")
        s_count = cursor.fetchone()[0]
        print(f"Sales count: {s_count}")
        
        # Sample data
        if p_count > 0:
            cursor.execute("SELECT * FROM purchases LIMIT 1")
            sample_purchase = cursor.fetchone()
            print("Sample purchase:", sample_purchase)
            
        if s_count > 0:
            cursor.execute("SELECT * FROM sales LIMIT 1")
            sample_sale = cursor.fetchone()
            print("Sample sale:", sample_sale)
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_database()
import tkinter as tk
from tkinter import messagebox
import mysql.connector
from datetime import datetime, timedelta
from multi_purchase import open_purchase_window
from sales import open_sales_window
from working_summary import open_summary_window
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

# ===================== MYSQL CONNECTION =====================
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",       # Change if needed
        password="11207107021Sam",       # Change if needed
        database="waruguru_foods"
    )

# ===================== WEEKLY SUMMARY (PDF) =====================
def weekly_summary():
    try:
        conn = connect_db()
        cursor = conn.cursor()

        today = datetime.now()
        last_week = today - timedelta(days=7)

        # Purchases in last 7 days
        cursor.execute("""
            SELECT IFNULL(SUM(total), 0) 
            FROM purchases 
            WHERE purchase_date BETWEEN %s AND %s
        """, (last_week, today))
        total_purchases = cursor.fetchone()[0]

        # Sales in last 7 days
        cursor.execute("""
            SELECT IFNULL(SUM(total), 0) 
            FROM sales 
            WHERE sale_date BETWEEN %s AND %s
        """, (last_week, today))
        total_sales = cursor.fetchone()[0]

        conn.close()

        # File path for PDF
        filename = f"Weekly_Summary_{today.strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(os.getcwd(), filename)

        # Create PDF
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4

        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - 50, "Weekly Summary Report")

        c.setFont("Helvetica", 12)
        c.drawString(50, height - 100, f"Period: {last_week.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}")
        c.drawString(50, height - 140, f"Total Purchases: {total_purchases:.2f}")
        c.drawString(50, height - 170, f"Total Sales: {total_sales:.2f}")

        c.setFont("Helvetica-Oblique", 10)
        c.drawString(50, 50, f"Generated on: {today.strftime('%Y-%m-%d %H:%M:%S')}")

        c.save()

        messagebox.showinfo("Weekly Summary", f"Report saved successfully!\n\nFile: {filename}")

    except Exception as e:
        messagebox.showerror("Error", f"Could not generate summary:\n{e}")

# ===================== DASHBOARD =====================
def open_dashboard():
    from fullscreen_app import FullScreenApp
    app = FullScreenApp()
    app.run()

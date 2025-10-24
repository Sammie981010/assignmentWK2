import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from fpdf import FPDF
from datetime import datetime, timedelta

def show_weekly_summary(parent):
    summary_win = tk.Toplevel(parent)
    summary_win.title("Weekly Summary")
    summary_win.geometry("800x500")

    # Connect to MySQL
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="waruguru_foods"
    )
    cursor = conn.cursor()

    # Get the date 7 days ago
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    # Fetch Purchases
    cursor.execute("SELECT item_name, quantity_kg, price_per_kg, total_price, date FROM purchases WHERE date >= %s", (seven_days_ago,))
    purchases = cursor.fetchall()

    # Fetch Sales
    cursor.execute("SELECT customer_name, item_name, quantity_kg, price_per_kg, total_price, date FROM sales WHERE date >= %s", (seven_days_ago,))
    sales = cursor.fetchall()

    conn.close()

    # Create Notebook for tabs
    notebook = ttk.Notebook(summary_win)
    notebook.pack(fill="both", expand=True)

    # Purchases Tab
    purchase_frame = ttk.Frame(notebook)
    notebook.add(purchase_frame, text="Purchases")

    purchase_table = ttk.Treeview(purchase_frame, columns=("Item", "Qty (Kg)", "Price/Kg", "Total", "Date"), show="headings")
    for col in ("Item", "Qty (Kg)", "Price/Kg", "Total", "Date"):
        purchase_table.heading(col, text=col)
        purchase_table.column(col, width=120)
    purchase_table.pack(fill="both", expand=True)

    for row in purchases:
        purchase_table.insert("", tk.END, values=row)

    # Sales Tab
    sales_frame = ttk.Frame(notebook)
    notebook.add(sales_frame, text="Sales")

    sales_table = ttk.Treeview(sales_frame, columns=("Customer", "Item", "Qty (Kg)", "Price/Kg", "Total", "Date"), show="headings")
    for col in ("Customer", "Item", "Qty (Kg)", "Price/Kg", "Total", "Date"):
        sales_table.heading(col, text=col)
        sales_table.column(col, width=120)
    sales_table.pack(fill="both", expand=True)

    for row in sales:
        sales_table.insert("", tk.END, values=row)

    # Export to PDF automatically
    export_weekly_summary_to_pdf(purchases, sales)

    messagebox.showinfo("Success", "Weekly Summary generated and saved to 'weekly_summary.pdf'.")

def export_weekly_summary_to_pdf(purchases, sales):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Purchases Section
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Weekly Summary - Purchases", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(40, 10, "Item")
    pdf.cell(30, 10, "Qty (Kg)")
    pdf.cell(30, 10, "Price/Kg")
    pdf.cell(30, 10, "Total")
    pdf.cell(40, 10, "Date", ln=True)

    pdf.set_font("Arial", "", 10)
    for row in purchases:
        pdf.cell(40, 10, str(row[0]))
        pdf.cell(30, 10, str(row[1]))
        pdf.cell(30, 10, str(row[2]))
        pdf.cell(30, 10, str(row[3]))
        pdf.cell(40, 10, str(row[4]), ln=True)

    # Sales Section
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Weekly Summary - Sales", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(40, 10, "Customer")
    pdf.cell(30, 10, "Item")
    pdf.cell(30, 10, "Qty (Kg)")
    pdf.cell(30, 10, "Price/Kg")
    pdf.cell(30, 10, "Total")
    pdf.cell(30, 10, "Date", ln=True)

    pdf.set_font("Arial", "", 10)
    for row in sales:
        pdf.cell(40, 10, str(row[0]))
        pdf.cell(30, 10, str(row[1]))
        pdf.cell(30, 10, str(row[2]))
        pdf.cell(30, 10, str(row[3]))
        pdf.cell(30, 10, str(row[4]))
        pdf.cell(30, 10, str(row[5]), ln=True)

    # Save PDF
    pdf.output("weekly_summary.pdf")

import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import mysql.connector

def open_summary_window(parent):
    win = tk.Toplevel(parent)
    win.title("Summary")
    win.geometry("300x200")
    
    def weekly():
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="11207107021Sam",
                database="waruguru_foods"
            )
            cursor = conn.cursor()
            
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=7)
            
            cursor.execute("SELECT COUNT(*), COALESCE(SUM(total), 0) FROM purchases WHERE purchase_date BETWEEN %s AND %s", (start_date, end_date))
            p_count, p_total = cursor.fetchone()
            
            cursor.execute("SELECT COUNT(*), COALESCE(SUM(total), 0) FROM sales WHERE sale_date BETWEEN %s AND %s", (start_date, end_date))
            s_count, s_total = cursor.fetchone()
            
            conn.close()
            
            result = f"WEEKLY SUMMARY\n{start_date} to {end_date}\n\nPurchases: {p_count} - ${p_total:.2f}\nSales: {s_count} - ${s_total:.2f}\nProfit: ${s_total - p_total:.2f}"
            messagebox.showinfo("Weekly Summary", result)
            
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")
    
    def monthly():
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="11207107021Sam",
                database="waruguru_foods"
            )
            cursor = conn.cursor()
            
            today = datetime.now().date()
            start_date = today.replace(day=1)
            
            cursor.execute("SELECT COUNT(*), COALESCE(SUM(total), 0) FROM purchases WHERE purchase_date BETWEEN %s AND %s", (start_date, today))
            p_count, p_total = cursor.fetchone()
            
            cursor.execute("SELECT COUNT(*), COALESCE(SUM(total), 0) FROM sales WHERE sale_date BETWEEN %s AND %s", (start_date, today))
            s_count, s_total = cursor.fetchone()
            
            conn.close()
            
            result = f"MONTHLY SUMMARY\n{start_date} to {today}\n\nPurchases: {p_count} - ${p_total:.2f}\nSales: {s_count} - ${s_total:.2f}\nProfit: ${s_total - p_total:.2f}"
            messagebox.showinfo("Monthly Summary", result)
            
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")
    
    tk.Button(win, text="This Week", command=weekly).pack(pady=20)
    tk.Button(win, text="This Month", command=monthly).pack(pady=20)
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import mysql.connector

def open_summary_window(parent):
    win = tk.Toplevel(parent)
    win.title("Summary Reports")
    win.geometry("500x300")
    
    tk.Label(win, text="SUMMARY REPORTS", font=("Arial", 16, "bold")).pack(pady=20)
    
    def show_weekly():
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root", 
                password="11207107021Sam",
                database="decent_food"
            )
            cursor = conn.cursor()
            
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=7)
            
            cursor.execute("SELECT COUNT(*), IFNULL(SUM(total), 0) FROM purchases WHERE purchase_date BETWEEN %s AND %s", (start_date, end_date))
            p_count, p_total = cursor.fetchone()
            
            cursor.execute("SELECT COUNT(*), IFNULL(SUM(total), 0) FROM sales WHERE sale_date BETWEEN %s AND %s", (start_date, end_date))
            s_count, s_total = cursor.fetchone()
            
            conn.close()
            
            result = f"WEEKLY SUMMARY ({start_date} to {end_date})\n\n"
            result += f"Purchases: {p_count} transactions, ${p_total:.2f}\n"
            result += f"Sales: {s_count} transactions, ${s_total:.2f}\n"
            result += f"Profit: ${s_total - p_total:.2f}"
            
            messagebox.showinfo("Weekly Summary", result)
            
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")
    
    def show_monthly():
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="11207107021Sam", 
                database="decent_food"
            )
            cursor = conn.cursor()
            
            today = datetime.now().date()
            start_date = today.replace(day=1)
            
            cursor.execute("SELECT COUNT(*), IFNULL(SUM(total), 0) FROM purchases WHERE purchase_date BETWEEN %s AND %s", (start_date, today))
            p_count, p_total = cursor.fetchone()
            
            cursor.execute("SELECT COUNT(*), IFNULL(SUM(total), 0) FROM sales WHERE sale_date BETWEEN %s AND %s", (start_date, today))
            s_count, s_total = cursor.fetchone()
            
            conn.close()
            
            result = f"MONTHLY SUMMARY ({start_date} to {today})\n\n"
            result += f"Purchases: {p_count} transactions, ${p_total:.2f}\n"
            result += f"Sales: {s_count} transactions, ${s_total:.2f}\n"
            result += f"Profit: ${s_total - p_total:.2f}"
            
            messagebox.showinfo("Monthly Summary", result)
            
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {e}")
    
    tk.Button(win, text="This Week", command=show_weekly, width=20, height=2, bg="#4CAF50", fg="white").pack(pady=10)
    tk.Button(win, text="This Month", command=show_monthly, width=20, height=2, bg="#2196F3", fg="white").pack(pady=10)
    tk.Button(win, text="Close", command=win.destroy, width=20, height=2).pack(pady=10)
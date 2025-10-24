import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import json
import os
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def get_purchases_file():
    return os.path.join(os.path.dirname(__file__), "purchases.json")

def get_sales_file():
    return os.path.join(os.path.dirname(__file__), "sales.json")

def load_purchases():
    try:
        if os.path.exists(get_purchases_file()):
            with open(get_purchases_file(), 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading purchases: {e}")
        return []

def load_sales():
    try:
        if os.path.exists(get_sales_file()):
            with open(get_sales_file(), 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading sales: {e}")
        return []

def get_weekly_data():
    today = datetime.today()
    week_start = today - timedelta(days=today.weekday())  # Monday
    week_end = week_start + timedelta(days=6)  # Sunday
    
    purchases = load_purchases()
    sales = load_sales()
    
    weekly_purchases = []
    weekly_sales = []
    
    # Filter purchases for this week
    for purchase in purchases:
        purchase_date = datetime.fromisoformat(purchase['purchase_date'])
        if week_start <= purchase_date <= week_end:
            weekly_purchases.append(purchase)
    
    # Filter sales for this week
    for sale in sales:
        sale_date = datetime.fromisoformat(sale['sale_date'])
        if week_start <= sale_date <= week_end:
            weekly_sales.append(sale)
    
    return weekly_purchases, weekly_sales, week_start, week_end

def calculate_summary():
    purchases, sales, week_start, week_end = get_weekly_data()
    
    # Calculate totals
    total_purchases = sum(p['total'] for p in purchases)
    total_sales = 0
    total_items_sold = 0
    
    for sale in sales:
        total_sales += sale['total_amount']
        total_items_sold += len(sale['items'])
    
    profit = total_sales - total_purchases
    
    return {
        'week_start': week_start,
        'week_end': week_end,
        'total_purchases': total_purchases,
        'total_sales': total_sales,
        'profit': profit,
        'num_purchases': len(purchases),
        'num_sales': len(sales),
        'total_items_sold': total_items_sold,
        'purchases': purchases,
        'sales': sales
    }

def export_weekly_pdf():
    try:
        summary = calculate_summary()
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save Weekly Summary Report"
        )
        
        if not filename:
            return
        
        # Create PDF
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        
        # Title
        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, height - 50, "Weekly Summary Report - Decent Foods")
        
        week_str = f"{summary['week_start'].strftime('%Y-%m-%d')} to {summary['week_end'].strftime('%Y-%m-%d')}"
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 75, f"Week: {week_str}")
        c.drawString(50, height - 95, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        y = height - 130
        
        # Summary section
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "WEEKLY SUMMARY")
        y -= 25
        
        c.setFont("Helvetica", 11)
        c.drawString(50, y, f"Total Purchases: ${summary['total_purchases']:.2f} ({summary['num_purchases']} transactions)")
        y -= 20
        c.drawString(50, y, f"Total Sales: ${summary['total_sales']:.2f} ({summary['num_sales']} transactions)")
        y -= 20
        c.drawString(50, y, f"Net Profit: ${summary['profit']:.2f}")
        y -= 20
        c.drawString(50, y, f"Items Sold: {summary['total_items_sold']}")
        y -= 40
        
        # Purchases section
        if summary['purchases']:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "PURCHASES")
            y -= 20
            
            c.setFont("Helvetica-Bold", 9)
            c.drawString(50, y, "Date")
            c.drawString(120, y, "Supplier")
            c.drawString(220, y, "Item")
            c.drawString(320, y, "Qty")
            c.drawString(360, y, "Price")
            c.drawString(420, y, "Total")
            y -= 15
            
            c.setFont("Helvetica", 8)
            for purchase in summary['purchases']:
                if y < 50:
                    c.showPage()
                    y = height - 50
                
                date_str = purchase['purchase_date'][:10]
                c.drawString(50, y, date_str)
                c.drawString(120, y, purchase['supplier'][:12])
                c.drawString(220, y, purchase['item'][:12])
                c.drawString(320, y, str(purchase['quantity']))
                c.drawString(360, y, f"${purchase['price']:.2f}")
                c.drawString(420, y, f"${purchase['total']:.2f}")
                y -= 12
            
            y -= 20
        
        # Sales section
        if summary['sales']:
            if y < 200:
                c.showPage()
                y = height - 50
            
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "SALES")
            y -= 20
            
            for sale in summary['sales']:
                if y < 100:
                    c.showPage()
                    y = height - 50
                
                c.setFont("Helvetica-Bold", 10)
                c.drawString(50, y, f"Sale #{sale['id']} - {sale['customer_name']}")
                c.drawString(350, y, f"${sale['total_amount']:.2f}")
                c.drawString(450, y, sale['sale_date'][:10])
                y -= 15
                
                c.setFont("Helvetica", 8)
                for item in sale['items']:
                    c.drawString(70, y, f"• {item['item']} x{item['quantity']} @ ${item['price']:.2f} = ${item['total']:.2f}")
                    y -= 10
                y -= 10
        
        c.save()
        messagebox.showinfo("Success", f"Weekly summary PDF saved!\nLocation: {filename}")
        
    except ImportError:
        messagebox.showerror("Error", "ReportLab library not installed.\nInstall with: pip install reportlab")
    except Exception as e:
        messagebox.showerror("Error", f"Could not create PDF: {e}")

def open_weekly_summary_window(parent):
    summary_win = tk.Toplevel(parent)
    summary_win.title("Weekly Summary - Decent Foods")
    summary_win.geometry("800x600")
    summary_win.resizable(True, True)
    
    # Title
    title_frame = tk.Frame(summary_win, bg="#2E86AB", height=50)
    title_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
    title_frame.grid_propagate(False)
    
    tk.Label(title_frame, text="WEEKLY SUMMARY", font=("Arial", 16, "bold"), 
             bg="#2E86AB", fg="white").pack(pady=12)
    
    # Get summary data
    summary = calculate_summary()
    
    # Summary info frame
    info_frame = tk.Frame(summary_win, bg="#f8f9fa", relief="ridge", bd=2)
    info_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
    
    week_str = f"{summary['week_start'].strftime('%b %d')} - {summary['week_end'].strftime('%b %d, %Y')}"
    tk.Label(info_frame, text=f"Week: {week_str}", font=("Arial", 12, "bold"), 
             bg="#f8f9fa").pack(pady=5)
    
    # Summary stats
    stats_frame = tk.Frame(info_frame, bg="#f8f9fa")
    stats_frame.pack(pady=10)
    
    # Left column
    left_stats = tk.Frame(stats_frame, bg="#f8f9fa")
    left_stats.pack(side=tk.LEFT, padx=20)
    
    tk.Label(left_stats, text=f"Total Purchases: ${summary['total_purchases']:.2f}", 
             font=("Arial", 11), bg="#f8f9fa").pack(anchor="w")
    tk.Label(left_stats, text=f"Purchase Transactions: {summary['num_purchases']}", 
             font=("Arial", 11), bg="#f8f9fa").pack(anchor="w")
    
    # Right column
    right_stats = tk.Frame(stats_frame, bg="#f8f9fa")
    right_stats.pack(side=tk.LEFT, padx=20)
    
    tk.Label(right_stats, text=f"Total Sales: ${summary['total_sales']:.2f}", 
             font=("Arial", 11), bg="#f8f9fa").pack(anchor="w")
    tk.Label(right_stats, text=f"Sales Transactions: {summary['num_sales']}", 
             font=("Arial", 11), bg="#f8f9fa").pack(anchor="w")
    
    # Profit
    profit_color = "#4CAF50" if summary['profit'] >= 0 else "#f44336"
    tk.Label(info_frame, text=f"Net Profit: ${summary['profit']:.2f}", 
             font=("Arial", 14, "bold"), bg="#f8f9fa", fg=profit_color).pack(pady=10)
    
    # Notebook for tabs
    notebook = ttk.Notebook(summary_win)
    notebook.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
    
    # Purchases tab
    purchases_frame = ttk.Frame(notebook)
    notebook.add(purchases_frame, text="Purchases")
    
    # Purchases tree
    purchases_tree = ttk.Treeview(purchases_frame, columns=("Date", "Supplier", "Item", "Qty", "Price", "Total"), 
                                 show="headings", height=15)
    
    for col in ["Date", "Supplier", "Item", "Qty", "Price", "Total"]:
        purchases_tree.heading(col, text=col)
        purchases_tree.column(col, width=120, anchor="center")
    
    for purchase in summary['purchases']:
        date_str = purchase['purchase_date'][:10]
        purchases_tree.insert("", "end", values=(
            date_str, purchase['supplier'], purchase['item'], 
            purchase['quantity'], f"${purchase['price']:.2f}", f"${purchase['total']:.2f}"
        ))
    
    purchases_tree.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Sales tab
    sales_frame = ttk.Frame(notebook)
    notebook.add(sales_frame, text="Sales")
    
    # Sales tree
    sales_tree = ttk.Treeview(sales_frame, columns=("Date", "Customer", "Items", "Total"), 
                             show="headings", height=15)
    
    for col in ["Date", "Customer", "Items", "Total"]:
        sales_tree.heading(col, text=col)
        sales_tree.column(col, width=150, anchor="center")
    
    for sale in summary['sales']:
        date_str = sale['sale_date'][:10]
        items_str = f"{len(sale['items'])} items"
        sales_tree.insert("", "end", values=(
            date_str, sale['customer_name'], items_str, f"${sale['total_amount']:.2f}"
        ))
    
    sales_tree.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Buttons
    button_frame = tk.Frame(summary_win)
    button_frame.grid(row=3, column=0, columnspan=2, pady=20)
    
    tk.Button(button_frame, text="Export PDF", command=export_weekly_pdf,
              bg="#FF6B35", fg="white", font=("Arial", 11, "bold"), 
              width=15, height=2).pack(side=tk.LEFT, padx=10)
    
    tk.Button(button_frame, text="Refresh", 
              command=lambda: summary_win.destroy() or open_weekly_summary_window(parent),
              bg="#2E86AB", fg="white", font=("Arial", 11, "bold"), 
              width=15, height=2).pack(side=tk.LEFT, padx=10)
    
    tk.Button(button_frame, text="Close", command=summary_win.destroy,
              bg="#6c757d", fg="white", font=("Arial", 11, "bold"), 
              width=15, height=2).pack(side=tk.LEFT, padx=10)
    
    # Configure grid weights
    summary_win.grid_rowconfigure(2, weight=1)
    summary_win.grid_columnconfigure(0, weight=1)
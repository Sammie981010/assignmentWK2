import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import calendar
from db import create_connection

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

class SummaryManager:
    def __init__(self):
        self.connection = create_connection()
    
    def get_data_by_period(self, start_date, end_date):
        """Get purchases and sales data for a specific period"""
        if not self.connection:
            return None, None
        
        cursor = self.connection.cursor(dictionary=True)
        
        # Get purchases
        purchase_query = """
        SELECT p.*, s.name as supplier_name 
        FROM purchases p 
        LEFT JOIN suppliers s ON p.supplier_id = s.id 
        WHERE DATE(p.purchase_date) BETWEEN %s AND %s 
        ORDER BY p.purchase_date DESC
        """
        cursor.execute(purchase_query, (start_date, end_date))
        purchases = cursor.fetchall()
        
        # Get sales
        sales_query = """
        SELECT s.*, si.item, si.quantity, si.price, si.total,
               (si.quantity * si.price) as item_total
        FROM sales s 
        JOIN sale_items si ON s.id = si.sale_id 
        WHERE DATE(s.sale_date) BETWEEN %s AND %s 
        ORDER BY s.sale_date DESC
        """
        cursor.execute(sales_query, (start_date, end_date))
        sales_raw = cursor.fetchall()
        
        # Group sales by sale_id
        sales = {}
        for row in sales_raw:
            sale_id = row['id']
            if sale_id not in sales:
                sales[sale_id] = {
                    'id': row['id'],
                    'customer_name': row['customer_name'],
                    'sale_date': row['sale_date'],
                    'total_amount': row['total_amount'],
                    'items': []
                }
            sales[sale_id]['items'].append({
                'item': row['item'],
                'quantity': row['quantity'],
                'price': row['price'],
                'total': row['total']
            })
        
        return purchases, list(sales.values())
    
    def calculate_summary_stats(self, purchases, sales):
        """Calculate summary statistics"""
        total_purchases = sum(p.get('total', 0) for p in purchases)
        num_purchases = len(purchases)
        
        total_sales = sum(s.get('total_amount', 0) for s in sales)
        num_sales = len(sales)
        
        total_items_sold = sum(
            sum(item['quantity'] for item in s['items']) 
            for s in sales
        )
        
        profit = total_sales - total_purchases
        
        return {
            'total_purchases': total_purchases,
            'num_purchases': num_purchases,
            'total_sales': total_sales,
            'num_sales': num_sales,
            'total_items_sold': total_items_sold,
            'profit': profit
        }

def open_summary_window(parent):
    """Main summary window with period selection"""
    summary_win = tk.Toplevel(parent)
    summary_win.title("Sales & Purchase Summary - Decent Foods")
    summary_win.geometry("900x700")
    summary_win.resizable(True, True)
    
    # Title
    title_frame = tk.Frame(summary_win, bg="#2E86AB", height=60)
    title_frame.grid(row=0, column=0, columnspan=3, sticky="ew")
    title_frame.grid_propagate(False)
    
    tk.Label(title_frame, text="SALES & PURCHASE SUMMARY", 
             font=("Arial", 18, "bold"), bg="#2E86AB", fg="white").pack(pady=15)
    
    # Period selection frame
    period_frame = tk.LabelFrame(summary_win, text="Select Period", 
                                font=("Arial", 12, "bold"), padx=10, pady=10)
    period_frame.grid(row=1, column=0, columnspan=3, padx=20, pady=10, sticky="ew")
    
    # Quick period buttons
    quick_frame = tk.Frame(period_frame)
    quick_frame.pack(fill="x", pady=5)
    
    tk.Label(quick_frame, text="Quick Select:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
    
    def show_weekly():
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        show_summary_report(summary_win, start_date, end_date, "Weekly")
    
    def show_monthly():
        today = datetime.now().date()
        start_date = today.replace(day=1)
        end_date = today
        show_summary_report(summary_win, start_date, end_date, "Monthly")
    
    def show_last_month():
        today = datetime.now().date()
        first_day_this_month = today.replace(day=1)
        last_day_last_month = first_day_this_month - timedelta(days=1)
        first_day_last_month = last_day_last_month.replace(day=1)
        show_summary_report(summary_win, first_day_last_month, last_day_last_month, "Last Month")
    
    tk.Button(quick_frame, text="This Week", command=show_weekly,
              bg="#4CAF50", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
    
    tk.Button(quick_frame, text="This Month", command=show_monthly,
              bg="#2196F3", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
    
    tk.Button(quick_frame, text="Last Month", command=show_last_month,
              bg="#FF9800", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
    
    # Custom date range
    custom_frame = tk.Frame(period_frame)
    custom_frame.pack(fill="x", pady=10)
    
    tk.Label(custom_frame, text="Custom Range:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
    
    tk.Label(custom_frame, text="From:").pack(side=tk.LEFT, padx=(20, 5))
    start_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
    start_entry = tk.Entry(custom_frame, textvariable=start_date_var, width=12)
    start_entry.pack(side=tk.LEFT, padx=5)
    
    tk.Label(custom_frame, text="To:").pack(side=tk.LEFT, padx=(10, 5))
    end_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
    end_entry = tk.Entry(custom_frame, textvariable=end_date_var, width=12)
    end_entry.pack(side=tk.LEFT, padx=5)
    
    def show_custom():
        try:
            start_date = datetime.strptime(start_date_var.get(), "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_var.get(), "%Y-%m-%d").date()
            if start_date > end_date:
                messagebox.showerror("Error", "Start date must be before end date")
                return
            show_summary_report(summary_win, start_date, end_date, "Custom Period")
        except ValueError:
            messagebox.showerror("Error", "Please enter dates in YYYY-MM-DD format")
    
    tk.Button(custom_frame, text="Generate Report", command=show_custom,
              bg="#FF6B35", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=10)
    
    # Instructions
    info_frame = tk.Frame(summary_win, bg="#f8f9fa", relief="ridge", bd=1)
    info_frame.grid(row=2, column=0, columnspan=3, padx=20, pady=10, sticky="ew")
    
    tk.Label(info_frame, text="📊 Select a period above to generate detailed purchase and sales reports",
             font=("Arial", 11), bg="#f8f9fa", fg="#666").pack(pady=15)
    
    # Configure grid weights
    summary_win.grid_columnconfigure(1, weight=1)

def show_summary_report(parent, start_date, end_date, period_name):
    """Show detailed summary report for the selected period"""
    report_win = tk.Toplevel(parent)
    report_win.title(f"{period_name} Summary - Decent Foods")
    report_win.geometry("1000x700")
    report_win.resizable(True, True)
    
    # Get data
    manager = SummaryManager()
    purchases, sales = manager.get_data_by_period(start_date, end_date)
    
    if purchases is None:
        messagebox.showerror("Error", "Could not connect to database")
        report_win.destroy()
        return
    
    stats = manager.calculate_summary_stats(purchases, sales)
    
    # Title
    title_frame = tk.Frame(report_win, bg="#2E86AB", height=50)
    title_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
    title_frame.grid_propagate(False)
    
    tk.Label(title_frame, text=f"{period_name.upper()} SUMMARY REPORT", 
             font=("Arial", 16, "bold"), bg="#2E86AB", fg="white").pack(pady=12)
    
    # Period info
    info_frame = tk.Frame(report_win, bg="#f8f9fa", relief="ridge", bd=2)
    info_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
    
    period_str = f"{start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}"
    tk.Label(info_frame, text=f"Period: {period_str}", 
             font=("Arial", 12, "bold"), bg="#f8f9fa").pack(pady=5)
    
    # Summary statistics
    stats_frame = tk.Frame(info_frame, bg="#f8f9fa")
    stats_frame.pack(pady=10)
    
    # Create 2x2 grid for stats
    stats_grid = tk.Frame(stats_frame, bg="#f8f9fa")
    stats_grid.pack()
    
    # Purchases stats
    purchase_frame = tk.Frame(stats_grid, bg="#e3f2fd", relief="ridge", bd=1, padx=10, pady=8)
    purchase_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
    tk.Label(purchase_frame, text="PURCHASES", font=("Arial", 10, "bold"), bg="#e3f2fd").pack()
    tk.Label(purchase_frame, text=f"${stats['total_purchases']:.2f}", 
             font=("Arial", 14, "bold"), bg="#e3f2fd", fg="#1976d2").pack()
    tk.Label(purchase_frame, text=f"{stats['num_purchases']} transactions", 
             font=("Arial", 9), bg="#e3f2fd").pack()
    
    # Sales stats
    sales_frame = tk.Frame(stats_grid, bg="#e8f5e8", relief="ridge", bd=1, padx=10, pady=8)
    sales_frame.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
    tk.Label(sales_frame, text="SALES", font=("Arial", 10, "bold"), bg="#e8f5e8").pack()
    tk.Label(sales_frame, text=f"${stats['total_sales']:.2f}", 
             font=("Arial", 14, "bold"), bg="#e8f5e8", fg="#388e3c").pack()
    tk.Label(sales_frame, text=f"{stats['num_sales']} transactions", 
             font=("Arial", 9), bg="#e8f5e8").pack()
    
    # Profit stats
    profit_color = "#4CAF50" if stats['profit'] >= 0 else "#f44336"
    profit_bg = "#e8f5e8" if stats['profit'] >= 0 else "#ffebee"
    profit_frame = tk.Frame(stats_grid, bg=profit_bg, relief="ridge", bd=1, padx=10, pady=8)
    profit_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
    tk.Label(profit_frame, text="NET PROFIT", font=("Arial", 10, "bold"), bg=profit_bg).pack()
    tk.Label(profit_frame, text=f"${stats['profit']:.2f}", 
             font=("Arial", 14, "bold"), bg=profit_bg, fg=profit_color).pack()
    
    # Items sold
    items_frame = tk.Frame(stats_grid, bg="#fff3e0", relief="ridge", bd=1, padx=10, pady=8)
    items_frame.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
    tk.Label(items_frame, text="ITEMS SOLD", font=("Arial", 10, "bold"), bg="#fff3e0").pack()
    tk.Label(items_frame, text=f"{stats['total_items_sold']}", 
             font=("Arial", 14, "bold"), bg="#fff3e0", fg="#f57c00").pack()
    
    # Notebook for detailed data
    notebook = ttk.Notebook(report_win)
    notebook.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
    
    # Purchases tab
    purchases_frame = ttk.Frame(notebook)
    notebook.add(purchases_frame, text=f"Purchases ({len(purchases)})")
    
    purchases_tree = ttk.Treeview(purchases_frame, 
                                 columns=("Date", "Supplier", "Item", "Qty", "Price", "Total"), 
                                 show="headings", height=15)
    
    for col in ["Date", "Supplier", "Item", "Qty", "Price", "Total"]:
        purchases_tree.heading(col, text=col)
        purchases_tree.column(col, width=120, anchor="center")
    
    for purchase in purchases:
        date_str = purchase['purchase_date'].strftime('%Y-%m-%d') if purchase['purchase_date'] else 'N/A'
        supplier = purchase.get('supplier_name', 'Unknown')
        purchases_tree.insert("", "end", values=(
            date_str, supplier, purchase.get('item', ''), 
            purchase.get('quantity', 0), f"${purchase.get('price', 0):.2f}", 
            f"${purchase.get('total', 0):.2f}"
        ))
    
    purchases_tree.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Sales tab
    sales_frame = ttk.Frame(notebook)
    notebook.add(sales_frame, text=f"Sales ({len(sales)})")
    
    sales_tree = ttk.Treeview(sales_frame, 
                             columns=("Date", "Customer", "Items", "Total"), 
                             show="headings", height=15)
    
    for col in ["Date", "Customer", "Items", "Total"]:
        sales_tree.heading(col, text=col)
        sales_tree.column(col, width=150, anchor="center")
    
    for sale in sales:
        date_str = sale['sale_date'].strftime('%Y-%m-%d') if sale['sale_date'] else 'N/A'
        items_count = len(sale['items'])
        sales_tree.insert("", "end", values=(
            date_str, sale['customer_name'], f"{items_count} items", 
            f"${sale['total_amount']:.2f}"
        ))
    
    sales_tree.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Buttons
    button_frame = tk.Frame(report_win)
    button_frame.grid(row=3, column=0, columnspan=2, pady=20)
    
    def export_pdf():
        export_summary_pdf(purchases, sales, stats, start_date, end_date, period_name)
    
    tk.Button(button_frame, text="Export PDF", command=export_pdf,
              bg="#FF6B35", fg="white", font=("Arial", 11, "bold"), 
              width=15, height=2).pack(side=tk.LEFT, padx=10)
    
    tk.Button(button_frame, text="Close", command=report_win.destroy,
              bg="#6c757d", fg="white", font=("Arial", 11, "bold"), 
              width=15, height=2).pack(side=tk.LEFT, padx=10)
    
    # Configure grid weights
    report_win.grid_rowconfigure(2, weight=1)
    report_win.grid_columnconfigure(0, weight=1)

def export_summary_pdf(purchases, sales, stats, start_date, end_date, period_name):
    """Export summary to PDF"""
    if not REPORTLAB_AVAILABLE:
        messagebox.showerror("Error", "ReportLab library not installed.\nInstall with: pip install reportlab")
        return
    
    try:
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title=f"Save {period_name} Summary Report"
        )
        
        if not filename:
            return
        
        # Create PDF
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        
        # Title
        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, height - 50, f"{period_name} Summary Report - Decent Foods")
        
        period_str = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 75, f"Period: {period_str}")
        c.drawString(50, height - 95, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        y = height - 130
        
        # Summary statistics
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "SUMMARY STATISTICS")
        y -= 25
        
        c.setFont("Helvetica", 11)
        c.drawString(50, y, f"Total Purchases: ${stats['total_purchases']:.2f} ({stats['num_purchases']} transactions)")
        y -= 20
        c.drawString(50, y, f"Total Sales: ${stats['total_sales']:.2f} ({stats['num_sales']} transactions)")
        y -= 20
        c.drawString(50, y, f"Net Profit: ${stats['profit']:.2f}")
        y -= 20
        c.drawString(50, y, f"Items Sold: {stats['total_items_sold']}")
        y -= 40
        
        # Purchases section
        if purchases:
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
            for purchase in purchases:
                if y < 50:
                    c.showPage()
                    y = height - 50
                
                date_str = purchase['purchase_date'].strftime('%Y-%m-%d') if purchase['purchase_date'] else 'N/A'
                supplier = purchase.get('supplier_name', 'Unknown')[:12]
                item = purchase.get('item', '')[:12]
                
                c.drawString(50, y, date_str)
                c.drawString(120, y, supplier)
                c.drawString(220, y, item)
                c.drawString(320, y, str(purchase.get('quantity', 0)))
                c.drawString(360, y, f"${purchase.get('price', 0):.2f}")
                c.drawString(420, y, f"${purchase.get('total', 0):.2f}")
                y -= 12
            
            y -= 20
        
        # Sales section
        if sales:
            if y < 200:
                c.showPage()
                y = height - 50
            
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "SALES")
            y -= 20
            
            for sale in sales:
                if y < 100:
                    c.showPage()
                    y = height - 50
                
                date_str = sale['sale_date'].strftime('%Y-%m-%d') if sale['sale_date'] else 'N/A'
                c.setFont("Helvetica-Bold", 10)
                c.drawString(50, y, f"Sale #{sale['id']} - {sale['customer_name']}")
                c.drawString(350, y, f"${sale['total_amount']:.2f}")
                c.drawString(450, y, date_str)
                y -= 15
                
                c.setFont("Helvetica", 8)
                for item in sale['items']:
                    c.drawString(70, y, f"• {item['item']} x{item['quantity']} @ ${item['price']:.2f} = ${item['total']:.2f}")
                    y -= 10
                y -= 10
        
        c.save()
        messagebox.showinfo("Success", f"{period_name} summary PDF saved!\nLocation: {filename}")
        
    except Exception as e:
        messagebox.showerror("Error", f"Could not create PDF: {e}")
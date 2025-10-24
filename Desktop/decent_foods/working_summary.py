import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import json
import os


try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

def load_purchases():
    try:
        if os.path.exists("purchases.json"):
            with open("purchases.json", 'r') as f:
                return json.load(f)
        return []
    except:
        return []

def load_sales():
    try:
        if os.path.exists("sales.json"):
            with open("sales.json", 'r') as f:
                return json.load(f)
        return []
    except:
        return []

def get_data_by_period(start_date, end_date):
    """Get purchases and sales data for a specific period"""
    purchases = load_purchases()
    sales = load_sales()
    
    filtered_purchases = []
    for p in purchases:
        try:
            p_date = datetime.fromisoformat(p['purchase_date']).date()
            if start_date <= p_date <= end_date:
                p['item_name'] = p['item']
                filtered_purchases.append(p)
        except:
            continue
    
    filtered_sales = []
    for s in sales:
        try:
            s_date = datetime.fromisoformat(s['sale_date']).date()
            if start_date <= s_date <= end_date:
                # Flatten sales items
                for item in s['items']:
                    sale_item = {
                        'id': s['id'],
                        'customer_name': s['customer_name'],
                        'item_name': item['item'],
                        'quantity': item['quantity'],
                        'price': item['price'],
                        'total': item['total'],
                        'sale_date': s['sale_date']
                    }
                    filtered_sales.append(sale_item)
        except:
            continue
    
    return filtered_purchases, filtered_sales

def calculate_summary_stats(purchases, sales):
    """Calculate summary statistics"""
    total_purchases = sum(float(p.get('total', 0)) for p in purchases)
    num_purchases = len(purchases)
    
    total_sales = sum(float(s.get('total', 0)) for s in sales)
    num_sales = len(sales)
    
    total_items_sold = sum(int(s.get('quantity', 0)) for s in sales)
    
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
    summary_win.geometry("800x600")
    summary_win.resizable(True, True)
    
    # Title
    title_frame = tk.Frame(summary_win, bg="#2E86AB", height=60)
    title_frame.pack(fill="x")
    title_frame.pack_propagate(False)
    
    tk.Label(title_frame, text="SALES & PURCHASE SUMMARY", 
             font=("Arial", 18, "bold"), bg="#2E86AB", fg="white").pack(pady=15)
    
    # Period selection frame
    period_frame = tk.LabelFrame(summary_win, text="Select Period", 
                                font=("Arial", 12, "bold"), padx=10, pady=10)
    period_frame.pack(fill="x", padx=20, pady=10)
    
    # Quick period buttons
    quick_frame = tk.Frame(period_frame)
    quick_frame.pack(fill="x", pady=5)
    
    tk.Label(quick_frame, text="Quick Select:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
    
    def show_weekly():
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        show_summary_report(summary_win, start_date, end_date, "This Week")
    
    def show_monthly():
        today = datetime.now().date()
        start_date = today.replace(day=1)
        end_date = today
        show_summary_report(summary_win, start_date, end_date, "This Month")
    
    def show_last_month():
        today = datetime.now().date()
        first_day_this_month = today.replace(day=1)
        last_day_last_month = first_day_this_month - timedelta(days=1)
        first_day_last_month = last_day_last_month.replace(day=1)
        show_summary_report(summary_win, first_day_last_month, last_day_last_month, "Last Month")
    
    def download_weekly():
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        purchases, sales = get_data_by_period(start_date, end_date)
        stats = calculate_summary_stats(purchases, sales)
        export_summary_pdf(purchases, sales, stats, start_date, end_date, "Weekly")
    
    def download_monthly():
        today = datetime.now().date()
        start_date = today.replace(day=1)
        purchases, sales = get_data_by_period(start_date, today)
        stats = calculate_summary_stats(purchases, sales)
        export_summary_pdf(purchases, sales, stats, start_date, today, "Monthly")
    
    tk.Button(quick_frame, text="This Week", command=show_weekly,
              bg="#4CAF50", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
    
    tk.Button(quick_frame, text="This Month", command=show_monthly,
              bg="#2196F3", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
    
    tk.Button(quick_frame, text="Last Month", command=show_last_month,
              bg="#FF9800", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
    
    # Download buttons
    download_frame = tk.Frame(period_frame)
    download_frame.pack(fill="x", pady=10)
    
    tk.Label(download_frame, text="Quick Download:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
    
    tk.Button(download_frame, text="Download Weekly PDF", command=download_weekly,
              bg="#9C27B0", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
    
    tk.Button(download_frame, text="Download Monthly PDF", command=download_monthly,
              bg="#673AB7", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
    
    # Separate downloads
    separate_frame = tk.Frame(period_frame)
    separate_frame.pack(fill="x", pady=5)
    
    tk.Label(separate_frame, text="Separate Reports:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
    
    def download_purchases_only():
        today = datetime.now().date()
        start_date = today.replace(day=1)
        purchases, _ = get_data_by_period(start_date, today)
        export_purchases_pdf(purchases, start_date, today)
    
    def download_sales_only():
        today = datetime.now().date()
        start_date = today.replace(day=1)
        _, sales = get_data_by_period(start_date, today)
        export_sales_pdf(sales, start_date, today)
    
    tk.Button(separate_frame, text="Purchases Only", command=download_purchases_only,
              bg="#FF5722", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
    
    tk.Button(separate_frame, text="Sales Only", command=download_sales_only,
              bg="#795548", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
    
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
    info_frame.pack(fill="x", padx=20, pady=10)
    
    tk.Label(info_frame, text="📊 Select a period above to generate detailed purchase and sales reports",
             font=("Arial", 11), bg="#f8f9fa", fg="#666").pack(pady=15)

def show_summary_report(parent, start_date, end_date, period_name):
    """Show detailed summary report for the selected period"""
    try:
        # Get data
        purchases, sales = get_data_by_period(start_date, end_date)
        stats = calculate_summary_stats(purchases, sales)
        
        report_win = tk.Toplevel(parent)
        report_win.title(f"{period_name} Summary - Decent Foods")
        report_win.geometry("1000x700")
        report_win.resizable(True, True)
        
        # Title
        title_frame = tk.Frame(report_win, bg="#2E86AB", height=50)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame, text=f"{period_name.upper()} SUMMARY REPORT", 
                 font=("Arial", 16, "bold"), bg="#2E86AB", fg="white").pack(pady=12)
        
        # Period info
        info_frame = tk.Frame(report_win, bg="#f8f9fa", relief="ridge", bd=2)
        info_frame.pack(fill="x", padx=20, pady=10)
        
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
        tk.Label(purchase_frame, text=f"KSH {stats['total_purchases']:.2f}", 
                 font=("Arial", 14, "bold"), bg="#e3f2fd", fg="#1976d2").pack()
        tk.Label(purchase_frame, text=f"{stats['num_purchases']} transactions", 
                 font=("Arial", 9), bg="#e3f2fd").pack()
        
        # Sales stats
        sales_frame = tk.Frame(stats_grid, bg="#e8f5e8", relief="ridge", bd=1, padx=10, pady=8)
        sales_frame.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        tk.Label(sales_frame, text="SALES", font=("Arial", 10, "bold"), bg="#e8f5e8").pack()
        tk.Label(sales_frame, text=f"KSH {stats['total_sales']:.2f}", 
                 font=("Arial", 14, "bold"), bg="#e8f5e8", fg="#388e3c").pack()
        tk.Label(sales_frame, text=f"{stats['num_sales']} transactions", 
                 font=("Arial", 9), bg="#e8f5e8").pack()
        
        # Profit stats
        profit_color = "#4CAF50" if stats['profit'] >= 0 else "#f44336"
        profit_bg = "#e8f5e8" if stats['profit'] >= 0 else "#ffebee"
        profit_frame = tk.Frame(stats_grid, bg=profit_bg, relief="ridge", bd=1, padx=10, pady=8)
        profit_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        tk.Label(profit_frame, text="NET PROFIT", font=("Arial", 10, "bold"), bg=profit_bg).pack()
        tk.Label(profit_frame, text=f"KSH {stats['profit']:.2f}", 
                 font=("Arial", 14, "bold"), bg=profit_bg, fg=profit_color).pack()
        
        # Items sold
        items_frame = tk.Frame(stats_grid, bg="#fff3e0", relief="ridge", bd=1, padx=10, pady=8)
        items_frame.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        tk.Label(items_frame, text="ITEMS SOLD", font=("Arial", 10, "bold"), bg="#fff3e0").pack()
        tk.Label(items_frame, text=f"{stats['total_items_sold']}", 
                 font=("Arial", 14, "bold"), bg="#fff3e0", fg="#f57c00").pack()
        
        # Notebook for detailed data
        notebook = ttk.Notebook(report_win)
        notebook.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Purchases tab
        purchases_frame = ttk.Frame(notebook)
        notebook.add(purchases_frame, text=f"Purchases ({len(purchases)})")
        
        purchases_tree = ttk.Treeview(purchases_frame, 
                                     columns=("Date", "Item", "Qty", "Price", "Total"), 
                                     show="headings", height=12)
        
        for col in ["Date", "Item", "Qty", "Price", "Total"]:
            purchases_tree.heading(col, text=col)
            purchases_tree.column(col, width=120, anchor="center")
        
        for purchase in purchases:
            try:
                date_str = datetime.fromisoformat(purchase['purchase_date']).strftime('%Y-%m-%d') if purchase.get('purchase_date') else 'N/A'
                purchases_tree.insert("", "end", values=(
                    date_str, purchase.get('item_name', ''), 
                    purchase.get('quantity', 0), f"KSH {purchase.get('price', 0):.2f}", 
                    f"KSH {purchase.get('total', 0):.2f}"
                ))
            except Exception as e:
                print(f"Error processing purchase: {e}")
        
        purchases_tree.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Purchase PDF button
        tk.Button(purchases_frame, text="Export Purchases PDF", 
                  command=lambda: export_purchases_pdf(purchases, start_date, end_date),
                  bg="#FF6B35", fg="white", font=("Arial", 9, "bold")).pack(pady=5)
        
        # Sales tab
        sales_frame = ttk.Frame(notebook)
        notebook.add(sales_frame, text=f"Sales ({len(sales)})")
        
        sales_tree = ttk.Treeview(sales_frame, 
                                 columns=("Date", "Customer", "Item", "Qty", "Price", "Total"), 
                                 show="headings", height=12)
        
        for col in ["Date", "Customer", "Item", "Qty", "Price", "Total"]:
            sales_tree.heading(col, text=col)
            sales_tree.column(col, width=120, anchor="center")
        
        for sale in sales:
            try:
                date_str = datetime.fromisoformat(sale['sale_date']).strftime('%Y-%m-%d') if sale.get('sale_date') else 'N/A'
                sales_tree.insert("", "end", values=(
                    date_str, sale.get('customer_name', ''), sale.get('item_name', ''),
                    sale.get('quantity', 0), f"KSH {sale.get('price', 0):.2f}",
                    f"KSH {sale.get('total', 0):.2f}"
                ))
            except Exception as e:
                print(f"Error processing sale: {e}")
        
        sales_tree.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Sales PDF button
        tk.Button(sales_frame, text="Export Sales PDF", 
                  command=lambda: export_sales_pdf(sales, start_date, end_date),
                  bg="#FF6B35", fg="white", font=("Arial", 9, "bold")).pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(report_win)
        button_frame.pack(pady=20)
        
        def export_pdf():
            export_summary_pdf(purchases, sales, stats, start_date, end_date, period_name)
        
        tk.Button(button_frame, text="Export PDF", command=export_pdf,
                  bg="#FF6B35", fg="white", font=("Arial", 11, "bold"), 
                  width=15, height=2).pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="Close", command=report_win.destroy,
                  bg="#6c757d", fg="white", font=("Arial", 11, "bold"), 
                  width=15, height=2).pack(side=tk.LEFT, padx=10)
        
    except Exception as e:
        print(f"Report generation error: {e}")
        messagebox.showerror("Error", f"Could not generate report: {str(e)}")

def export_purchases_pdf(purchases, start_date, end_date):
    """Export only purchases to PDF"""
    if not REPORTLAB_AVAILABLE:
        messagebox.showerror("Error", "ReportLab library not installed.\nInstall with: pip install reportlab")
        return
    
    try:
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save Purchases Report"
        )
        
        if not filename:
            return
        
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        
        # Report title centered
        c.setFont("Helvetica-Bold", 16)
        title = "Purchases Report"
        title_width = c.stringWidth(title, "Helvetica-Bold", 16)
        c.drawString((width - title_width) / 2, height - 50, title)
        
        # Period info
        period_str = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, f"Period: {period_str}")
        
        y = height - 110
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "PURCHASES")
        y -= 20
        
        c.setFont("Helvetica-Bold", 9)
        c.drawString(50, y, "Date")
        c.drawString(120, y, "Item")
        c.drawString(250, y, "Qty")
        c.drawString(300, y, "Price")
        c.drawString(360, y, "Total")
        y -= 15
        
        c.setFont("Helvetica", 8)
        total_amount = 0
        for purchase in purchases:
            if y < 50:
                c.showPage()
                y = height - 50
            
            date_str = datetime.fromisoformat(purchase['purchase_date']).strftime('%Y-%m-%d') if purchase.get('purchase_date') else 'N/A'
            item = str(purchase.get('item_name', ''))[:20]
            
            c.drawString(50, y, date_str)
            c.drawString(120, y, item)
            c.drawString(250, y, str(purchase.get('quantity', 0)))
            c.drawString(300, y, f"KSH {purchase.get('price', 0):.2f}")
            c.drawString(360, y, f"KSH {purchase.get('total', 0):.2f}")
            total_amount += purchase.get('total', 0)
            y -= 12
        
        y -= 10
        c.setFont("Helvetica-Bold", 12)
        c.drawString(300, y, f"Total: KSH {total_amount:.2f}")
        
        # Add timestamp at bottom
        c.setFont("Helvetica", 8)
        c.drawString(50, 30, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        c.save()
        messagebox.showinfo("Success", f"Purchases PDF saved!\nLocation: {filename}")
        
    except Exception as e:
        messagebox.showerror("Error", f"Could not create PDF: {e}")

def export_sales_pdf(sales, start_date, end_date):
    """Export only sales to PDF"""
    if not REPORTLAB_AVAILABLE:
        messagebox.showerror("Error", "ReportLab library not installed.\nInstall with: pip install reportlab")
        return
    
    try:
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save Sales Report"
        )
        
        if not filename:
            return
        
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        
        # Report title centered
        c.setFont("Helvetica-Bold", 16)
        title = "Sales Report"
        title_width = c.stringWidth(title, "Helvetica-Bold", 16)
        c.drawString((width - title_width) / 2, height - 50, title)
        
        # Period info
        period_str = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, f"Period: {period_str}")
        
        y = height - 110
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "SALES")
        y -= 20
        
        c.setFont("Helvetica-Bold", 9)
        c.drawString(50, y, "Date")
        c.drawString(120, y, "Customer")
        c.drawString(220, y, "Item")
        c.drawString(320, y, "Qty")
        c.drawString(360, y, "Price")
        c.drawString(420, y, "Total")
        y -= 15
        
        c.setFont("Helvetica", 8)
        total_amount = 0
        for sale in sales:
            if y < 50:
                c.showPage()
                y = height - 50
            
            date_str = datetime.fromisoformat(sale['sale_date']).strftime('%Y-%m-%d') if sale.get('sale_date') else 'N/A'
            customer = str(sale.get('customer_name', ''))[:15]
            item = str(sale.get('item_name', ''))[:15]
            
            c.drawString(50, y, date_str)
            c.drawString(120, y, customer)
            c.drawString(220, y, item)
            c.drawString(320, y, str(sale.get('quantity', 0)))
            c.drawString(360, y, f"KSH {sale.get('price', 0):.2f}")
            c.drawString(420, y, f"KSH {sale.get('total', 0):.2f}")
            total_amount += sale.get('total', 0)
            y -= 12
        
        y -= 10
        c.setFont("Helvetica-Bold", 12)
        c.drawString(360, y, f"Total: KSH {total_amount:.2f}")
        
        # Add timestamp at bottom
        c.setFont("Helvetica", 8)
        c.drawString(50, 30, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        c.save()
        messagebox.showinfo("Success", f"Sales PDF saved!\nLocation: {filename}")
        
    except Exception as e:
        messagebox.showerror("Error", f"Could not create PDF: {e}")

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
        
        # Report title centered
        c.setFont("Helvetica-Bold", 18)
        title = f"{period_name} Summary Report"
        title_width = c.stringWidth(title, "Helvetica-Bold", 18)
        c.drawString((width - title_width) / 2, height - 50, title)
        
        # Period info
        period_str = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, f"Period: {period_str}")
        
        y = height - 110
        
        # Summary statistics
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "SUMMARY STATISTICS")
        y -= 25
        
        c.setFont("Helvetica", 11)
        c.drawString(50, y, f"Total Purchases: KSH {stats['total_purchases']:.2f} ({stats['num_purchases']} transactions)")
        y -= 20
        c.drawString(50, y, f"Total Sales: KSH {stats['total_sales']:.2f} ({stats['num_sales']} transactions)")
        y -= 20
        c.drawString(50, y, f"Net Profit: KSH {stats['profit']:.2f}")
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
            c.drawString(120, y, "Item")
            c.drawString(250, y, "Qty")
            c.drawString(300, y, "Price")
            c.drawString(360, y, "Total")
            y -= 15
            
            c.setFont("Helvetica", 8)
            for purchase in purchases:
                if y < 50:
                    c.showPage()
                    y = height - 50
                
                date_str = datetime.fromisoformat(purchase['purchase_date']).strftime('%Y-%m-%d') if purchase.get('purchase_date') else 'N/A'
                item = str(purchase.get('item_name', ''))[:20]
                
                c.drawString(50, y, date_str)
                c.drawString(120, y, item)
                c.drawString(250, y, str(purchase.get('quantity', 0)))
                c.drawString(300, y, f"KSH {purchase.get('price', 0):.2f}")
                c.drawString(360, y, f"KSH {purchase.get('total', 0):.2f}")
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
            
            c.setFont("Helvetica-Bold", 9)
            c.drawString(50, y, "Date")
            c.drawString(120, y, "Customer")
            c.drawString(220, y, "Item")
            c.drawString(320, y, "Qty")
            c.drawString(360, y, "Price")
            c.drawString(420, y, "Total")
            y -= 15
            
            c.setFont("Helvetica", 8)
            for sale in sales:
                if y < 50:
                    c.showPage()
                    y = height - 50
                
                date_str = datetime.fromisoformat(sale['sale_date']).strftime('%Y-%m-%d') if sale.get('sale_date') else 'N/A'
                customer = str(sale.get('customer_name', ''))[:15]
                item = str(sale.get('item_name', ''))[:15]
                
                c.drawString(50, y, date_str)
                c.drawString(120, y, customer)
                c.drawString(220, y, item)
                c.drawString(320, y, str(sale.get('quantity', 0)))
                c.drawString(360, y, f"KSH {sale.get('price', 0):.2f}")
                c.drawString(420, y, f"KSH {sale.get('total', 0):.2f}")
                y -= 12
        
        # Add timestamp at bottom
        c.setFont("Helvetica", 8)
        c.drawString(50, 30, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        c.save()
        messagebox.showinfo("Success", f"{period_name} summary PDF saved!\nLocation: {filename}")
        
    except Exception as e:
        messagebox.showerror("Error", f"Could not create PDF: {e}")
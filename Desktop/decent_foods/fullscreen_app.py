import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

class FullScreenApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CESS FOODS - Management System")
        self.root.state('zoomed')  # Full screen on Windows
        
        # Global variables
        self.purchase_items = []
        self.purchase_total = 0.0
        self.sales_items = []
        self.sales_total = 0.0
        self.order_items = []
        self.order_total = 0.0
        self.invoice_counter = 1
        self.order_counter = 1
        self.create_main_interface()
    

    
    def create_main_interface(self):
        # Title bar
        title_frame = tk.Frame(self.root, bg="#2E86AB", height=60)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame, text="CESS FOODS - MANAGEMENT SYSTEM", 
                font=("Arial", 20, "bold"), bg="#2E86AB", fg="white").pack(pady=15)
    
        # Main notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initialize counters
        self.invoice_counter = self.get_next_invoice_number()
        self.order_counter = self.get_next_order_number()
        
        # Create tabs
        self.create_orders_tab()
        self.create_purchase_tab()
        self.create_sales_tab()
        self.create_supplier_payments_tab()
        self.create_summary_tab()
    
    def create_purchase_tab(self):
        purchase_frame = ttk.Frame(self.notebook)
        self.notebook.add(purchase_frame, text="Purchases")
        
        # Multi-item purchase section
        item_frame = tk.LabelFrame(purchase_frame, text="Add Purchase Items", font=("Arial", 12, "bold"))
        item_frame.pack(fill="x", padx=20, pady=10)
        
        # Date and invoice fields
        date_frame = tk.Frame(item_frame)
        date_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(date_frame, text="Date:", font=("Arial", 10, "bold")).pack(side="left")
        self.purchase_date_entry = tk.Entry(date_frame, width=12, font=("Arial", 10))
        self.purchase_date_entry.pack(side="left", padx=5)
        self.purchase_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        tk.Label(date_frame, text="Invoice/Ref:", font=("Arial", 10, "bold")).pack(side="left", padx=(20,0))
        self.purchase_invoice_entry = tk.Entry(date_frame, width=15, font=("Arial", 10))
        self.purchase_invoice_entry.pack(side="left", padx=5)
        self.purchase_invoice_entry.insert(0, f"PUR-{len(self.load_purchases())+1:04d}")
        
        # Input fields
        fields_frame = tk.Frame(item_frame)
        fields_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(fields_frame, text="Supplier:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.supplier_entry = tk.Entry(fields_frame, width=15, font=("Arial", 10))
        self.supplier_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(fields_frame, text="Item:", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.item_entry = tk.Entry(fields_frame, width=15, font=("Arial", 10))
        self.item_entry.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(fields_frame, text="Qty:", font=("Arial", 10, "bold")).grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.qty_entry = tk.Entry(fields_frame, width=8, font=("Arial", 10))
        self.qty_entry.grid(row=0, column=5, padx=5, pady=5)
        
        tk.Label(fields_frame, text="Price (KSH):", font=("Arial", 10, "bold")).grid(row=0, column=6, padx=5, pady=5, sticky="w")
        self.price_entry = tk.Entry(fields_frame, width=10, font=("Arial", 10))
        self.price_entry.grid(row=0, column=7, padx=5, pady=5)
        
        # Live calculator
        self.item_total_label = tk.Label(fields_frame, text="Item Total: KSH 0.00", font=("Arial", 10, "bold"), fg="#2E86AB")
        self.item_total_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        def update_item_total(*args):
            try:
                q = float(self.qty_entry.get() or 0)
                p = float(self.price_entry.get() or 0)
                self.item_total_label.config(text=f"Item Total: KSH {q*p:.2f}")
            except:
                self.item_total_label.config(text="Item Total: KSH 0.00")
        
        self.qty_entry.bind("<KeyRelease>", update_item_total)
        self.price_entry.bind("<KeyRelease>", update_item_total)
        
        tk.Button(fields_frame, text="Add Item", command=self.add_purchase_item,
                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).grid(row=1, column=6, columnspan=2, padx=5, pady=5)
        
        # Purchase items list
        list_frame = tk.LabelFrame(purchase_frame, text="Purchase Items", font=("Arial", 12, "bold"))
        list_frame.pack(fill="both", expand=True, padx=20, pady=5)
        
        self.purchase_tree = ttk.Treeview(list_frame, columns=("Supplier", "Item", "Qty", "Price", "Total"), 
                                         show="headings", height=6)
        for col in ["Supplier", "Item", "Qty", "Price", "Total"]:
            self.purchase_tree.heading(col, text=col)
            self.purchase_tree.column(col, width=120, anchor="center")
        
        scrollbar_p = ttk.Scrollbar(list_frame, orient="vertical", command=self.purchase_tree.yview)
        self.purchase_tree.configure(yscrollcommand=scrollbar_p.set)
        
        self.purchase_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar_p.pack(side="right", fill="y")
        
        # Total display
        self.purchase_total_label = tk.Label(purchase_frame, text="Total: KSH 0.00", 
                                           font=("Arial", 14, "bold"), fg="#2E86AB", bg="#f8f9fa", 
                                           relief="ridge", bd=2, padx=20, pady=10)
        self.purchase_total_label.pack(pady=15)
        
        # Purchase buttons
        btn_frame = tk.Frame(purchase_frame)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Save Purchase", command=self.save_purchase,
                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), 
                 width=12, height=2).pack(side="left", padx=2)
        
        tk.Button(btn_frame, text="Clear All", command=self.clear_purchase,
                 bg="#FFC107", fg="black", font=("Arial", 10, "bold"), 
                 width=12, height=2).pack(side="left", padx=2)
        
        tk.Button(btn_frame, text="Download PDF", command=self.download_purchase_pdf,
                 bg="#FF6B35", fg="white", font=("Arial", 10, "bold"), 
                 width=12, height=2).pack(side="left", padx=2)
        
        tk.Button(btn_frame, text="Remove Selected", command=self.remove_purchase_item,
                 bg="#f44336", fg="white", font=("Arial", 10, "bold"), 
                 width=12, height=2).pack(side="left", padx=2)
    
    def create_sales_tab(self):
        sales_frame = ttk.Frame(self.notebook)
        self.notebook.add(sales_frame, text="Sales")
        
        # Customer info and metadata
        customer_frame = tk.Frame(sales_frame)
        customer_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(customer_frame, text="Customer Name:", font=("Arial", 12, "bold")).pack(side="left")
        self.customer_entry = tk.Entry(customer_frame, width=25, font=("Arial", 12))
        self.customer_entry.pack(side="left", padx=10)
        
        tk.Label(customer_frame, text="Date:", font=("Arial", 12, "bold")).pack(side="left", padx=(20,0))
        self.sales_date_entry = tk.Entry(customer_frame, width=12, font=("Arial", 12))
        self.sales_date_entry.pack(side="left", padx=5)
        self.sales_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        tk.Label(customer_frame, text="Invoice:", font=("Arial", 12, "bold")).pack(side="left", padx=(20,0))
        self.sales_invoice_entry = tk.Entry(customer_frame, width=12, font=("Arial", 12))
        self.sales_invoice_entry.pack(side="left", padx=5)
        self.sales_invoice_entry.insert(0, f"INV-{self.invoice_counter:04d}")
        
        # Sales item entry
        sales_item_frame = tk.LabelFrame(sales_frame, text="Add Sale Items", font=("Arial", 12, "bold"))
        sales_item_frame.pack(fill="x", padx=20, pady=10)
        
        sales_fields_frame = tk.Frame(sales_item_frame)
        sales_fields_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(sales_fields_frame, text="Item:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.sales_item_entry = tk.Entry(sales_fields_frame, width=20, font=("Arial", 10))
        self.sales_item_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(sales_fields_frame, text="Qty:", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.sales_qty_entry = tk.Entry(sales_fields_frame, width=10, font=("Arial", 10))
        self.sales_qty_entry.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(sales_fields_frame, text="Price (KSH):", font=("Arial", 10, "bold")).grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.sales_price_entry = tk.Entry(sales_fields_frame, width=12, font=("Arial", 10))
        self.sales_price_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # Sales live calculator
        self.sales_item_total_label = tk.Label(sales_fields_frame, text="Item Total: KSH 0.00", font=("Arial", 10, "bold"), fg="#2E86AB")
        self.sales_item_total_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        def update_sales_item_total(*args):
            try:
                q = float(self.sales_qty_entry.get() or 0)
                p = float(self.sales_price_entry.get() or 0)
                self.sales_item_total_label.config(text=f"Item Total: KSH {q*p:.2f}")
            except:
                self.sales_item_total_label.config(text="Item Total: KSH 0.00")
        
        self.sales_qty_entry.bind("<KeyRelease>", update_sales_item_total)
        self.sales_price_entry.bind("<KeyRelease>", update_sales_item_total)
        
        tk.Button(sales_fields_frame, text="Add Item", command=self.add_sales_item,
                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).grid(row=1, column=4, columnspan=2, padx=5, pady=5)
        
        # Sales items list
        sales_list_frame = tk.LabelFrame(sales_frame, text="Sale Items", font=("Arial", 12, "bold"))
        sales_list_frame.pack(fill="both", expand=True, padx=20, pady=5)
        
        self.sales_tree = ttk.Treeview(sales_list_frame, columns=("Item", "Qty", "Price", "Total"), 
                                      show="headings", height=6)
        for col in ["Item", "Qty", "Price", "Total"]:
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, width=120, anchor="center")
        
        scrollbar_s = ttk.Scrollbar(sales_list_frame, orient="vertical", command=self.sales_tree.yview)
        self.sales_tree.configure(yscrollcommand=scrollbar_s.set)
        
        self.sales_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar_s.pack(side="right", fill="y")
        
        # Sales total display
        self.sales_total_label = tk.Label(sales_frame, text="Total: KSH 0.00", 
                                         font=("Arial", 14, "bold"), fg="#2E86AB", bg="#f8f9fa", 
                                         relief="ridge", bd=2, padx=20, pady=10)
        self.sales_total_label.pack(pady=5)
        
        # Sales buttons
        sales_btn_frame = tk.Frame(sales_frame)
        sales_btn_frame.pack(pady=5)
        
        tk.Button(sales_btn_frame, text="Save Sale", command=self.save_sale,
                 bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), 
                 width=15, height=5).pack(side="left", padx=2)
        
        tk.Button(sales_btn_frame, text="Clear All", command=self.clear_sales,
                 bg="#FFC107", fg="black", font=("Arial", 12, "bold"), 
                 width=15, height=5).pack(side="left", padx=2)
        
        tk.Button(sales_btn_frame, text="Download PDF", command=self.download_sales_pdf,
                 bg="#FF6B35", fg="white", font=("Arial", 12, "bold"), 
                 width=15, height=5).pack(side="left", padx=2)
        
        tk.Button(sales_btn_frame, text="Remove Selected", command=self.remove_sales_item,
                 bg="#f44336", fg="white", font=("Arial", 12, "bold"), 
                 width=15, height=5).pack(side="left", padx=2)
    
    def create_summary_tab(self):
        summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(summary_frame, text="Dashboard")
        
        # Main container with padding
        main_container = tk.Frame(summary_frame, bg="#f8f9fa")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header with title and period selector
        header_frame = tk.Frame(main_container, bg="#f8f9fa")
        header_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(header_frame, text="📊 BUSINESS DASHBOARD", 
                font=("Arial", 20, "bold"), fg="#2E86AB", bg="#f8f9fa").pack(side="left")
        
        # Period selector on the right
        period_frame = tk.Frame(header_frame, bg="#f8f9fa")
        period_frame.pack(side="right")
        
        tk.Label(period_frame, text="Period:", font=("Arial", 12, "bold"), bg="#f8f9fa").pack(side="left")
        self.summary_month_var = tk.StringVar(value=str(datetime.now().month))
        month_combo = ttk.Combobox(period_frame, textvariable=self.summary_month_var, 
                                  values=[str(i) for i in range(1, 13)], width=4)
        month_combo.pack(side="left", padx=5)
        
        self.summary_year_var = tk.StringVar(value=str(datetime.now().year))
        year_combo = ttk.Combobox(period_frame, textvariable=self.summary_year_var, 
                                 values=[str(i) for i in range(2020, 2030)], width=6)
        year_combo.pack(side="left", padx=5)
        
        tk.Button(period_frame, text="Update", command=self.update_dashboard,
                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=10)
        
        # PDF download dropdown
        pdf_frame = tk.Frame(period_frame, bg="#f8f9fa")
        pdf_frame.pack(side="left", padx=10)
        
        tk.Label(pdf_frame, text="Export:", font=("Arial", 10, "bold"), bg="#f8f9fa").pack(side="left")
        self.pdf_var = tk.StringVar(value="Select Report")
        pdf_combo = ttk.Combobox(pdf_frame, textvariable=self.pdf_var, 
                                values=["Weekly Sales", "Weekly Purchases", "Monthly Sales", "Monthly Purchases"], 
                                width=15, state="readonly")
        pdf_combo.pack(side="left", padx=5)
        pdf_combo.bind("<<ComboboxSelected>>", self.download_selected_pdf)
        
        tk.Button(pdf_frame, text="📄", command=self.show_pdf_options,
                 bg="#FF6B35", fg="white", font=("Arial", 10, "bold"), width=3).pack(side="left", padx=5)
        
        tk.Button(pdf_frame, text="💾 Backup", command=self.backup_data,
                 bg="#607D8B", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        
        # Stats cards row
        stats_frame = tk.Frame(main_container, bg="#f8f9fa")
        stats_frame.pack(fill="x", pady=(0, 20))
        
        # Sales card
        self.sales_card = tk.Frame(stats_frame, bg="#4CAF50", relief="raised", bd=2)
        self.sales_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        tk.Label(self.sales_card, text="💰 SALES", font=("Arial", 14, "bold"), 
                fg="white", bg="#4CAF50").pack(pady=10)
        self.sales_amount_label = tk.Label(self.sales_card, text="KSH 0.00", 
                                          font=("Arial", 18, "bold"), fg="white", bg="#4CAF50")
        self.sales_amount_label.pack()
        self.sales_count_label = tk.Label(self.sales_card, text="0 transactions", 
                                         font=("Arial", 10), fg="white", bg="#4CAF50")
        self.sales_count_label.pack(pady=(0, 10))
        
        # Purchases card
        self.purchases_card = tk.Frame(stats_frame, bg="#FF9800", relief="raised", bd=2)
        self.purchases_card.pack(side="left", fill="both", expand=True, padx=10)
        
        tk.Label(self.purchases_card, text="📦 PURCHASES", font=("Arial", 14, "bold"), 
                fg="white", bg="#FF9800").pack(pady=10)
        self.purchases_amount_label = tk.Label(self.purchases_card, text="KSH 0.00", 
                                              font=("Arial", 18, "bold"), fg="white", bg="#FF9800")
        self.purchases_amount_label.pack()
        self.purchases_count_label = tk.Label(self.purchases_card, text="0 transactions", 
                                             font=("Arial", 10), fg="white", bg="#FF9800")
        self.purchases_count_label.pack(pady=(0, 10))
        
        # Profit card
        self.profit_card = tk.Frame(stats_frame, bg="#2196F3", relief="raised", bd=2)
        self.profit_card.pack(side="left", fill="both", expand=True, padx=(10, 0))
        
        tk.Label(self.profit_card, text="📈 PROFIT", font=("Arial", 14, "bold"), 
                fg="white", bg="#2196F3").pack(pady=10)
        self.profit_amount_label = tk.Label(self.profit_card, text="KSH 0.00", 
                                           font=("Arial", 18, "bold"), fg="white", bg="#2196F3")
        self.profit_amount_label.pack()
        self.profit_margin_label = tk.Label(self.profit_card, text="0% margin", 
                                           font=("Arial", 10), fg="white", bg="#2196F3")
        self.profit_margin_label.pack(pady=(0, 10))
        
        # Graph and details container
        content_frame = tk.Frame(main_container, bg="#f8f9fa")
        content_frame.pack(fill="both", expand=True)
        
        # Graph frame
        if MATPLOTLIB_AVAILABLE:
            self.graph_frame = tk.Frame(content_frame, bg="white", relief="raised", bd=1)
            self.graph_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
            
            tk.Label(self.graph_frame, text="Monthly Sales Trend", 
                    font=("Arial", 14, "bold"), bg="white").pack(pady=10)
        else:
            # Placeholder when matplotlib not available
            self.graph_frame = tk.Frame(content_frame, bg="white", relief="raised", bd=1)
            self.graph_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
            
            tk.Label(self.graph_frame, text="Graph unavailable\n(Install matplotlib)", 
                    font=("Arial", 12), bg="white", fg="gray").pack(expand=True)
        
        # Details frame
        details_frame = tk.Frame(content_frame, bg="white", relief="raised", bd=1)
        details_frame.pack(side="right", fill="y", padx=(10, 0))
        
        tk.Label(details_frame, text="Recent Activity", 
                font=("Arial", 14, "bold"), bg="white").pack(pady=10)
        
        self.details_text = tk.Text(details_frame, width=40, height=20, font=("Arial", 9))
        details_scroll = ttk.Scrollbar(details_frame, orient="vertical", command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scroll.set)
        
        self.details_text.pack(side="left", fill="both", expand=True, padx=10, pady=(0, 10))
        details_scroll.pack(side="right", fill="y", pady=(0, 10))
        
        # Initialize dashboard
        self.root.after(300, self.update_dashboard)
    
    # Purchase methods (keeping all previous functionality)
    def add_purchase_item(self):
        supplier = self.supplier_entry.get().strip()
        item = self.item_entry.get().strip()
        qty = self.qty_entry.get().strip()
        price = self.price_entry.get().strip()
        
        if not all([supplier, item, qty, price]):
            messagebox.showerror("Error", "All fields are required")
            return
        
        try:
            qty_val = float(qty)
            price_val = float(price)
            if qty_val <= 0 or price_val <= 0:
                raise ValueError("Values must be positive")
            
            total = qty_val * price_val
            
            self.purchase_items.append({
                "supplier": supplier,
                "item": item,
                "quantity": qty_val,
                "price": price_val,
                "total": total
            })
            
            self.purchase_tree.insert("", "end", values=(supplier, item, qty_val, f"KSH {price_val:.2f}", f"KSH {total:.2f}"))
            
            self.purchase_total += total
            self.purchase_total_label.config(text=f"Total: KSH {self.purchase_total:.2f}")
            
            # Clear item fields except supplier
            self.item_entry.delete(0, tk.END)
            self.qty_entry.delete(0, tk.END)
            self.price_entry.delete(0, tk.END)
            self.item_total_label.config(text="Item Total: KSH 0.00")
            
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity or price")
    
    def remove_purchase_item(self):
        selected = self.purchase_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to remove")
            return
        
        item_index = self.purchase_tree.index(selected[0])
        self.purchase_total -= self.purchase_items[item_index]['total']
        self.purchase_items.pop(item_index)
        self.purchase_tree.delete(selected[0])
        self.purchase_total_label.config(text=f"Total: KSH {self.purchase_total:.2f}")
    
    def save_purchase(self):
            
        if not self.purchase_items:
            messagebox.showerror("Error", "No items to save")
            return
        
        purchase_date = self.purchase_date_entry.get().strip()
        purchase_invoice = self.purchase_invoice_entry.get().strip()
        
        if not purchase_date:
            messagebox.showerror("Error", "Date is required")
            return
        
        try:
            # Validate date format
            datetime.strptime(purchase_date, '%Y-%m-%d')
            purchases = self.load_purchases()
            
            for item in self.purchase_items:
                new_purchase = {
                    "id": len(purchases) + 1,
                    "supplier": item["supplier"],
                    "item": item["item"],
                    "quantity": item["quantity"],
                    "price": item["price"],
                    "total": item["total"],
                    "purchase_date": purchase_date + "T00:00:00",
                    "invoice_ref": purchase_invoice,
                    "paid": False,
                    "balance": item["total"]
                }
                purchases.append(new_purchase)
            
            self.save_purchases(purchases)
            messagebox.showinfo("Success", f"Purchase saved!\nInvoice: {purchase_invoice}\nItems: {len(self.purchase_items)}\nTotal: KSH {self.purchase_total:.2f}")
            self.clear_purchase()
            # Refresh suppliers list
            if hasattr(self, 'supplier_combo'):
                self.refresh_suppliers()
            
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save: {e}")
    
    def clear_purchase(self):
        self.purchase_items.clear()
        self.purchase_total = 0.0
        self.supplier_entry.delete(0, tk.END)
        self.item_entry.delete(0, tk.END)
        self.qty_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        for item in self.purchase_tree.get_children():
            self.purchase_tree.delete(item)
        self.purchase_total_label.config(text="Total: KSH 0.00")
        self.item_total_label.config(text="Item Total: KSH 0.00")
        # Reset date and invoice fields
        self.purchase_date_entry.delete(0, tk.END)
        self.purchase_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.purchase_invoice_entry.delete(0, tk.END)
        self.purchase_invoice_entry.insert(0, f"PUR-{len(self.load_purchases())+1:04d}")
    
    def download_purchase_pdf(self):
        try:
            purchases = self.load_purchases()
            if not purchases:
                messagebox.showwarning("No Data", "No purchases to export")
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Save Purchase Report"
            )
            
            if not filename:
                return
            
            c = canvas.Canvas(filename, pagesize=letter)
            width, height = letter
            
            # Title
            c.setFont("Helvetica-Bold", 16)
            title = "Purchase Report"
            title_width = c.stringWidth(title, "Helvetica-Bold", 16)
            c.drawString((width - title_width) / 2, height - 50, title)
            
            c.setFont("Helvetica", 12)
            c.drawString(50, height - 80, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Headers
            c.setFont("Helvetica-Bold", 10)
            y = height - 120
            c.drawString(50, y, "Supplier")
            c.drawString(150, y, "Item")
            c.drawString(250, y, "Qty")
            c.drawString(300, y, "Price")
            c.drawString(370, y, "Total")
            c.drawString(450, y, "Date")
            
            # Data
            c.setFont("Helvetica", 9)
            y -= 20
            grand_total = 0
            
            for purchase in purchases:
                if y < 50:
                    c.showPage()
                    y = height - 50
                
                c.drawString(50, y, purchase['supplier'][:15])
                c.drawString(150, y, purchase['item'][:15])
                c.drawString(250, y, str(purchase['quantity']))
                c.drawString(300, y, f"KSH {purchase['price']:.2f}")
                c.drawString(370, y, f"KSH {purchase['total']:.2f}")
                c.drawString(450, y, purchase['purchase_date'][:10])
                
                grand_total += purchase['total']
                y -= 15
            
            # Grand total
            y -= 10
            c.setFont("Helvetica-Bold", 12)
            c.drawString(320, y, f"Grand Total: KSH {grand_total:.2f}")
            
            # Timestamp at bottom
            c.setFont("Helvetica", 8)
            c.drawString(50, 30, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            c.save()
            messagebox.showinfo("Success", f"PDF saved!\nLocation: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not create PDF: {e}")
    
    # Sales methods (keeping all previous functionality)
    def add_sales_item(self):
        item = self.sales_item_entry.get().strip()
        qty = self.sales_qty_entry.get().strip()
        price = self.sales_price_entry.get().strip()
        
        if not all([item, qty, price]):
            messagebox.showerror("Error", "All fields are required")
            return
        
        try:
            qty_val = float(qty)
            price_val = float(price)
            if qty_val <= 0 or price_val <= 0:
                raise ValueError("Values must be positive")
            
            total = qty_val * price_val
            
            self.sales_items.append({
                "item": item,
                "quantity": qty_val,
                "price": price_val,
                "total": total
            })
            
            self.sales_tree.insert("", "end", values=(item, qty_val, f"KSH {price_val:.2f}", f"KSH {total:.2f}"))
            
            self.sales_total += total
            self.sales_total_label.config(text=f"Total: KSH {self.sales_total:.2f}")
            
            # Clear fields
            self.sales_item_entry.delete(0, tk.END)
            self.sales_qty_entry.delete(0, tk.END)
            self.sales_price_entry.delete(0, tk.END)
            self.sales_item_total_label.config(text="Item Total: KSH 0.00")
            
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity or price")
    
    def remove_sales_item(self):
        selected = self.sales_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to remove")
            return
        
        item_index = self.sales_tree.index(selected[0])
        self.sales_total -= self.sales_items[item_index]['total']
        self.sales_items.pop(item_index)
        self.sales_tree.delete(selected[0])
        self.sales_total_label.config(text=f"Total: KSH {self.sales_total:.2f}")
    
    def save_sale(self):
        customer = self.customer_entry.get().strip()
        sales_date = self.sales_date_entry.get().strip()
        sales_invoice = self.sales_invoice_entry.get().strip()
        
        if not customer or not self.sales_items or not sales_date:
            messagebox.showerror("Error", "Customer name, date and items required")
            return
        
        try:
            # Validate date format
            datetime.strptime(sales_date, '%Y-%m-%d')
            sales = self.load_sales()
            
            new_sale = {
                "id": len(sales) + 1,
                "invoice_no": sales_invoice,
                "customer_name": customer,
                "items": self.sales_items.copy(),
                "total_amount": self.sales_total,
                "sale_date": sales_date + "T00:00:00"
            }
            
            sales.append(new_sale)
            self.save_sales(sales)
            messagebox.showinfo("Success", f"Sale saved!\nInvoice: {sales_invoice}\nCustomer: {customer}\nItems: {len(self.sales_items)}\nTotal: KSH {self.sales_total:.2f}")
            self.invoice_counter += 1
            self.clear_sales()
            
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save: {e}")
    
    def clear_sales(self):
        self.sales_items.clear()
        self.sales_total = 0.0
        self.customer_entry.delete(0, tk.END)
        self.sales_item_entry.delete(0, tk.END)
        self.sales_qty_entry.delete(0, tk.END)
        self.sales_price_entry.delete(0, tk.END)
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
        self.sales_total_label.config(text="Total: KSH 0.00")
        self.sales_item_total_label.config(text="Item Total: KSH 0.00")
        # Reset date and invoice fields
        self.sales_date_entry.delete(0, tk.END)
        self.sales_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.sales_invoice_entry.delete(0, tk.END)
        self.sales_invoice_entry.insert(0, f"INV-{self.invoice_counter:04d}")
    
    def download_sales_pdf(self):
        try:
            sales = self.load_sales()
            if not sales:
                messagebox.showwarning("No Data", "No sales to export")
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Save Sales Report"
            )
            
            if not filename:
                return
            
            c = canvas.Canvas(filename, pagesize=letter)
            width, height = letter
            
            # Title
            c.setFont("Helvetica-Bold", 16)
            title = "Sales Report"
            title_width = c.stringWidth(title, "Helvetica-Bold", 16)
            c.drawString((width - title_width) / 2, height - 50, title)
            
            c.setFont("Helvetica", 12)
            c.drawString(50, height - 80, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            y = height - 120
            grand_total = 0
            
            for sale in sales:
                # Sale header
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y, f"Sale #{sale['id']} - {sale['customer_name']}")
                c.drawString(400, y, sale['sale_date'][:10])
                y -= 20
                
                # Items
                c.setFont("Helvetica", 9)
                for item in sale['items']:
                    c.drawString(70, y, f"• {item['item']} x{item['quantity']} @ KSH {item['price']:.2f} = KSH {item['total']:.2f}")
                    y -= 12
                
                # Sale total
                c.setFont("Helvetica-Bold", 10)
                c.drawString(300, y, f"Sale Total: KSH {sale['total_amount']:.2f}")
                grand_total += sale['total_amount']
                y -= 30
                
                if y < 100:
                    c.showPage()
                    y = height - 50
            
            # Grand total
            c.setFont("Helvetica-Bold", 14)
            c.drawString(300, y - 20, f"Grand Total: KSH {grand_total:.2f}")
            
            # Timestamp at bottom
            c.setFont("Helvetica", 8)
            c.drawString(50, 30, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            c.save()
            messagebox.showinfo("Success", f"PDF saved!\nLocation: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not create PDF: {e}")
    
    # Summary methods
    def show_summary_report(self, period_type):
        if period_type == "week":
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=7)
            title = "Weekly Summary"
        elif period_type == "month":
            today = datetime.now().date()
            start_date = today.replace(day=1)
            end_date = today
            title = "Monthly Summary"
        elif period_type == "last_month":
            today = datetime.now().date()
            first_day_this_month = today.replace(day=1)
            end_date = first_day_this_month - timedelta(days=1)
            start_date = end_date.replace(day=1)
            title = "Last Month Summary"
        
        purchases, sales = self.get_data_by_period(start_date, end_date)
        
        total_purchases = sum(p.get('total', 0) for p in purchases)
        total_sales = sum(s.get('total_amount', 0) for s in sales)
        profit = total_sales - total_purchases
        
        summary = f"{title}\n"
        summary += f"Period: {start_date} to {end_date}\n"
        summary += "="*60 + "\n\n"
        summary += f"📊 SUMMARY STATISTICS\n"
        summary += f"Total Purchases: KSH {total_purchases:.2f} ({len(purchases)} transactions)\n"
        summary += f"Total Sales: KSH {total_sales:.2f} ({len(sales)} transactions)\n"
        summary += f"Net Profit: KSH {profit:.2f}\n"
        summary += f"Items Sold: {sum(sum(item['quantity'] for item in s.get('items', [])) for s in sales)}\n\n"
        
        summary += f"📦 RECENT PURCHASES ({len(purchases)} total)\n"
        for p in purchases[-10:]:
            date_str = datetime.fromisoformat(p['purchase_date']).strftime('%Y-%m-%d') if p.get('purchase_date') else 'N/A'
            summary += f"• {date_str}: {p.get('item', '')} x{p.get('quantity', 0)} = KSH {p.get('total', 0):.2f}\n"
        
        summary += f"\n💰 RECENT SALES ({len(sales)} total)\n"
        for s in sales[-10:]:
            date_str = datetime.fromisoformat(s['sale_date']).strftime('%Y-%m-%d') if s.get('sale_date') else 'N/A'
            summary += f"• {date_str}: {s.get('customer_name', '')} - KSH {s.get('total_amount', 0):.2f}\n"
        
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, summary)
    
    def download_summary_pdf(self, report_type):
        # Use the existing PDF generation from working_summary
        if report_type == "week":
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=7)
            period_name = "Weekly"
        elif report_type == "month":
            today = datetime.now().date()
            start_date = today.replace(day=1)
            end_date = today
            period_name = "Monthly"
        elif report_type == "purchases":
            today = datetime.now().date()
            start_date = today.replace(day=1)
            end_date = today
            purchases, _ = self.get_data_by_period(start_date, end_date)
            self.export_purchases_only_pdf(purchases, start_date, end_date)
            return
        elif report_type == "sales":
            today = datetime.now().date()
            start_date = today.replace(day=1)
            end_date = today
            _, sales = self.get_data_by_period(start_date, end_date)
            self.export_sales_only_pdf(sales, start_date, end_date)
            return
        
        purchases, sales = self.get_data_by_period(start_date, end_date)
        self.create_summary_pdf(purchases, sales, start_date, end_date, period_name)
    
    def create_summary_pdf(self, purchases, sales, start_date, end_date, period_name):
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title=f"Save {period_name} Summary Report"
        )
        
        if not filename:
            return
        
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        
        # Title
        c.setFont("Helvetica-Bold", 18)
        title = f"{period_name} Summary Report"
        title_width = c.stringWidth(title, "Helvetica-Bold", 18)
        c.drawString((width - title_width) / 2, height - 50, title)
        
        # Period
        period_str = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, f"Period: {period_str}")
        
        y = height - 110
        
        # Summary statistics
        total_purchases = sum(p.get('total', 0) for p in purchases)
        total_sales = sum(s.get('total_amount', 0) for s in sales)
        profit = total_sales - total_purchases
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "SUMMARY STATISTICS")
        y -= 25
        
        c.setFont("Helvetica", 11)
        c.drawString(50, y, f"Total Purchases: KSH {total_purchases:.2f} ({len(purchases)} transactions)")
        y -= 20
        c.drawString(50, y, f"Total Sales: KSH {total_sales:.2f} ({len(sales)} transactions)")
        y -= 20
        c.drawString(50, y, f"Net Profit: KSH {profit:.2f}")
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
                item = str(purchase.get('item', ''))[:20]
                
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
            
            for sale in sales:
                if y < 100:
                    c.showPage()
                    y = height - 50
                
                date_str = datetime.fromisoformat(sale['sale_date']).strftime('%Y-%m-%d') if sale.get('sale_date') else 'N/A'
                c.setFont("Helvetica-Bold", 10)
                c.drawString(50, y, f"Sale #{sale['id']} - {sale['customer_name']}")
                c.drawString(350, y, f"KSH {sale['total_amount']:.2f}")
                c.drawString(450, y, date_str)
                y -= 15
                
                c.setFont("Helvetica", 8)
                for item in sale['items']:
                    c.drawString(70, y, f"• {item['item']} x{item['quantity']} @ KSH {item['price']:.2f} = KSH {item['total']:.2f}")
                    y -= 10
                y -= 10
        
        # Timestamp at bottom
        c.setFont("Helvetica", 8)
        c.drawString(50, 30, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        c.save()
        messagebox.showinfo("Success", f"{period_name} summary PDF saved!\nLocation: {filename}")
    
    def export_purchases_only_pdf(self, purchases, start_date, end_date):
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save Purchases Report"
        )
        
        if not filename:
            return
        
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        
        # Title
        c.setFont("Helvetica-Bold", 16)
        title = "Purchases Report"
        title_width = c.stringWidth(title, "Helvetica-Bold", 16)
        c.drawString((width - title_width) / 2, height - 50, title)
        
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
            item = str(purchase.get('item', ''))[:20]
            
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
        
        # Timestamp at bottom
        c.setFont("Helvetica", 8)
        c.drawString(50, 30, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        c.save()
        messagebox.showinfo("Success", f"Purchases PDF saved!\nLocation: {filename}")
    
    def export_sales_only_pdf(self, sales, start_date, end_date):
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save Sales Report"
        )
        
        if not filename:
            return
        
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        
        # Title
        c.setFont("Helvetica-Bold", 16)
        title = "Sales Report"
        title_width = c.stringWidth(title, "Helvetica-Bold", 16)
        c.drawString((width - title_width) / 2, height - 50, title)
        
        period_str = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, f"Period: {period_str}")
        
        y = height - 110
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "SALES")
        y -= 20
        
        total_amount = 0
        for sale in sales:
            if y < 100:
                c.showPage()
                y = height - 50
            
            date_str = datetime.fromisoformat(sale['sale_date']).strftime('%Y-%m-%d') if sale.get('sale_date') else 'N/A'
            c.setFont("Helvetica-Bold", 10)
            c.drawString(50, y, f"Sale #{sale['id']} - {sale['customer_name']}")
            c.drawString(350, y, f"KSH {sale['total_amount']:.2f}")
            c.drawString(450, y, date_str)
            y -= 15
            
            c.setFont("Helvetica", 8)
            for item in sale['items']:
                c.drawString(70, y, f"• {item['item']} x{item['quantity']} @ KSH {item['price']:.2f} = KSH {item['total']:.2f}")
                y -= 10
            
            total_amount += sale['total_amount']
            y -= 10
        
        y -= 10
        c.setFont("Helvetica-Bold", 12)
        c.drawString(360, y, f"Total: KSH {total_amount:.2f}")
        
        # Timestamp at bottom
        c.setFont("Helvetica", 8)
        c.drawString(50, 30, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        c.save()
        messagebox.showinfo("Success", f"Sales PDF saved!\nLocation: {filename}")
    
    # Data methods
    def load_purchases(self):
        try:
            if os.path.exists("purchases.json"):
                with open("purchases.json", 'r') as f:
                    purchases = json.load(f)
                    # Migrate old purchases to include payment tracking
                    updated = False
                    for purchase in purchases:
                        if 'paid' not in purchase:
                            purchase['paid'] = False
                            purchase['balance'] = purchase.get('total', 0)
                            updated = True
                    if updated:
                        self.save_purchases(purchases)
                    return purchases
        except:
            pass
        return []
    
    def save_purchases(self, purchases):
        with open("purchases.json", 'w') as f:
            json.dump(purchases, f, indent=2, default=str)
    
    def load_sales(self):
        try:
            if os.path.exists("sales.json"):
                with open("sales.json", 'r') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def save_sales(self, sales):
        with open("sales.json", 'w') as f:
            json.dump(sales, f, indent=2, default=str)
    
    def get_data_by_period(self, start_date, end_date):
        purchases = self.load_purchases()
        sales = self.load_sales()
        
        filtered_purchases = []
        for p in purchases:
            try:
                # Handle both old format and new editable timestamp format
                purchase_date_str = p['purchase_date']
                if 'T' in purchase_date_str:
                    p_date = datetime.fromisoformat(purchase_date_str).date()
                else:
                    p_date = datetime.strptime(purchase_date_str[:10], '%Y-%m-%d').date()
                
                if start_date <= p_date <= end_date:
                    filtered_purchases.append(p)
            except:
                continue
        
        filtered_sales = []
        for s in sales:
            try:
                # Handle both old format and new editable timestamp format
                sale_date_str = s['sale_date']
                if 'T' in sale_date_str:
                    s_date = datetime.fromisoformat(sale_date_str).date()
                else:
                    s_date = datetime.strptime(sale_date_str[:10], '%Y-%m-%d').date()
                
                if start_date <= s_date <= end_date:
                    filtered_sales.append(s)
            except:
                continue
        
        return filtered_purchases, filtered_sales
    
    def get_next_invoice_number(self):
        try:
            sales = self.load_sales()
            if sales:
                return max([int(s.get('invoice_no', 'INV-0000').split('-')[1]) for s in sales if 'invoice_no' in s]) + 1
        except:
            pass
        return 1
    
    def get_next_order_number(self):
        try:
            orders = self.load_orders()
            if orders:
                return max([int(o.get('order_no', 'ORD-0000').split('-')[1]) for o in orders if 'order_no' in o]) + 1
        except:
            pass
        return 1
    
    def create_orders_tab(self):
        orders_frame = ttk.Frame(self.notebook)
        self.notebook.add(orders_frame, text="Orders")
        
        # Customer selection
        customer_frame = tk.Frame(orders_frame)
        customer_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(customer_frame, text="Customer Name:", font=("Arial", 12, "bold")).pack(side="left")
        self.order_customer_entry = tk.Entry(customer_frame, width=30, font=("Arial", 12))
        self.order_customer_entry.pack(side="left", padx=10)
        
        # Order number display
        self.order_no_label = tk.Label(customer_frame, text=f"Order No: ORD-{self.order_counter:04d}", 
                                      font=("Arial", 12, "bold"), fg="#2E86AB")
        self.order_no_label.pack(side="right", padx=10)
        
        # Order item entry
        order_item_frame = tk.LabelFrame(orders_frame, text="Add Order Items", font=("Arial", 12, "bold"))
        order_item_frame.pack(fill="x", padx=20, pady=10)
        
        order_fields_frame = tk.Frame(order_item_frame)
        order_fields_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(order_fields_frame, text="Item:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.order_item_entry = tk.Entry(order_fields_frame, width=20, font=("Arial", 10))
        self.order_item_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(order_fields_frame, text="Qty:", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.order_qty_entry = tk.Entry(order_fields_frame, width=10, font=("Arial", 10))
        self.order_qty_entry.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(order_fields_frame, text="Price (KSH):", font=("Arial", 10, "bold")).grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.order_price_entry = tk.Entry(order_fields_frame, width=12, font=("Arial", 10))
        self.order_price_entry.grid(row=0, column=5, padx=5, pady=5)
        
        tk.Button(order_fields_frame, text="Add Item", command=self.add_order_item,
                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).grid(row=0, column=6, padx=5, pady=5)
        
        # Order items list
        order_list_frame = tk.LabelFrame(orders_frame, text="Order Items", font=("Arial", 12, "bold"))
        order_list_frame.pack(fill="both", expand=True, padx=20, pady=5)
        
        self.order_tree = ttk.Treeview(order_list_frame, columns=("Item", "Qty", "Price", "Total"), 
                                      show="headings", height=6)
        for col in ["Item", "Qty", "Price", "Total"]:
            self.order_tree.heading(col, text=col)
            self.order_tree.column(col, width=120, anchor="center")
        
        scrollbar_o = ttk.Scrollbar(order_list_frame, orient="vertical", command=self.order_tree.yview)
        self.order_tree.configure(yscrollcommand=scrollbar_o.set)
        
        self.order_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar_o.pack(side="right", fill="y")
        
        # Order total display
        self.order_total_label = tk.Label(orders_frame, text="Total: KSH 0.00", 
                                         font=("Arial", 14, "bold"), fg="#2E86AB", bg="#f8f9fa", 
                                         relief="ridge", bd=2, padx=20, pady=10)
        self.order_total_label.pack(pady=5)
        
        # Order buttons
        order_btn_frame = tk.Frame(orders_frame)
        order_btn_frame.pack(pady=5)
        
        tk.Button(order_btn_frame, text="Save Order", command=self.save_order,
                 bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), 
                 width=15, height=3).pack(side="left", padx=2)
        
        tk.Button(order_btn_frame, text="Clear All", command=self.clear_order,
                 bg="#FFC107", fg="black", font=("Arial", 12, "bold"), 
                 width=15, height=3).pack(side="left", padx=2)
        
        tk.Button(order_btn_frame, text="Remove Selected", command=self.remove_order_item,
                 bg="#f44336", fg="white", font=("Arial", 12, "bold"), 
                 width=15, height=3).pack(side="left", padx=2)
    

    
    # Order methods
    def add_order_item(self):
        item = self.order_item_entry.get().strip()
        qty = self.order_qty_entry.get().strip()
        price = self.order_price_entry.get().strip()
        
        if not all([item, qty, price]):
            messagebox.showerror("Error", "All fields are required")
            return
        
        try:
            qty_val = float(qty)
            price_val = float(price)
            if qty_val <= 0 or price_val <= 0:
                raise ValueError("Values must be positive")
            
            total = qty_val * price_val
            
            self.order_items.append({
                "item": item,
                "quantity": qty_val,
                "price": price_val,
                "total": total
            })
            
            self.order_tree.insert("", "end", values=(item, qty_val, f"KSH {price_val:.2f}", f"KSH {total:.2f}"))
            
            self.order_total += total
            self.order_total_label.config(text=f"Total: KSH {self.order_total:.2f}")
            
            # Clear fields
            self.order_item_entry.delete(0, tk.END)
            self.order_qty_entry.delete(0, tk.END)
            self.order_price_entry.delete(0, tk.END)
            
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity or price")
    
    def save_order(self):
        customer = self.order_customer_entry.get().strip()
        if not customer or not self.order_items:
            messagebox.showerror("Error", "Customer name and items required")
            return
        
        try:
            orders = self.load_orders()
            date_now = datetime.now()
            
            new_order = {
                "id": len(orders) + 1,
                "order_no": f"ORD-{self.order_counter:04d}",
                "customer_name": customer,
                "items": self.order_items.copy(),
                "total_amount": self.order_total,
                "order_date": date_now.isoformat(),
                "status": "Pending"
            }
            
            orders.append(new_order)
            self.save_orders(orders)
            messagebox.showinfo("Success", f"Order saved!\nOrder No: ORD-{self.order_counter:04d}\nCustomer: {customer}\nItems: {len(self.order_items)}\nTotal: KSH {self.order_total:.2f}")
            self.order_counter += 1
            self.clear_order()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not save order: {e}")
    
    def clear_order(self):
        self.order_items.clear()
        self.order_total = 0.0
        self.order_customer_entry.delete(0, tk.END)
        self.order_item_entry.delete(0, tk.END)
        self.order_qty_entry.delete(0, tk.END)
        self.order_price_entry.delete(0, tk.END)
        for item in self.order_tree.get_children():
            self.order_tree.delete(item)
        self.order_total_label.config(text="Total: KSH 0.00")
        self.order_no_label.config(text=f"Order No: ORD-{self.order_counter:04d}")
    
    def remove_order_item(self):
        selected = self.order_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to remove")
            return
        
        item_index = self.order_tree.index(selected[0])
        self.order_total -= self.order_items[item_index]['total']
        self.order_items.pop(item_index)
        self.order_tree.delete(selected[0])
        self.order_total_label.config(text=f"Total: KSH {self.order_total:.2f}")
    

    
    # Data methods for new features
    def load_orders(self):
        try:
            if os.path.exists("orders.json"):
                with open("orders.json", 'r') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def save_orders(self, orders):
        with open("orders.json", 'w') as f:
            json.dump(orders, f, indent=2, default=str)
    
    def load_payments(self):
        try:
            if os.path.exists("payments.json"):
                with open("payments.json", 'r') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def save_payments(self, payments):
        with open("payments.json", 'w') as f:
            json.dump(payments, f, indent=2, default=str)
    
    def create_supplier_payments_tab(self):
        supplier_frame = ttk.Frame(self.notebook)
        self.notebook.add(supplier_frame, text="Supplier Payments")
        
        # Supplier selection
        selection_frame = tk.LabelFrame(supplier_frame, text="Select Supplier", font=("Arial", 12, "bold"))
        selection_frame.pack(fill="x", padx=20, pady=10)
        
        supplier_select_frame = tk.Frame(selection_frame)
        supplier_select_frame.pack(padx=10, pady=10)
        
        tk.Label(supplier_select_frame, text="Supplier:", font=("Arial", 10, "bold")).pack(side="left")
        self.supplier_var = tk.StringVar()
        self.supplier_combo = ttk.Combobox(supplier_select_frame, textvariable=self.supplier_var, width=25, font=("Arial", 10))
        self.supplier_combo.pack(side="left", padx=10)
        
        tk.Button(supplier_select_frame, text="Load Statement", command=self.load_supplier_statement,
                 bg="#2196F3", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=10)
        
        # Statement display
        statement_frame = tk.LabelFrame(supplier_frame, text="Purchase Statement", font=("Arial", 12, "bold"))
        statement_frame.pack(fill="x", padx=20, pady=10)
        
        # Purchases tree
        self.supplier_tree = ttk.Treeview(statement_frame, columns=("Date", "Item", "Qty", "Amount", "Paid", "Balance"), 
                                         show="headings", height=5)
        for col in ["Date", "Item", "Qty", "Amount", "Paid", "Balance"]:
            self.supplier_tree.heading(col, text=col)
            self.supplier_tree.column(col, width=100, anchor="center")
        
        scrollbar_sup = ttk.Scrollbar(statement_frame, orient="vertical", command=self.supplier_tree.yview)
        self.supplier_tree.configure(yscrollcommand=scrollbar_sup.set)
        
        self.supplier_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar_sup.pack(side="right", fill="y")
        
        # Summary and payment section
        summary_frame = tk.Frame(supplier_frame)
        summary_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Balance display
        balance_frame = tk.LabelFrame(summary_frame, text="Balance Summary", font=("Arial", 12, "bold"))
        balance_frame.pack(side="left", padx=(0, 10))
        
        self.total_purchases_label = tk.Label(balance_frame, text="Total Purchases: KSH 0.00", font=("Arial", 11, "bold"))
        self.total_purchases_label.pack(pady=3)
        
        self.total_paid_label = tk.Label(balance_frame, text="Total Paid: KSH 0.00", font=("Arial", 11, "bold"), fg="green")
        self.total_paid_label.pack(pady=3)
        
        self.outstanding_label = tk.Label(balance_frame, text="Outstanding: KSH 0.00", font=("Arial", 12, "bold"), fg="red")
        self.outstanding_label.pack(pady=3)
        
        # Payment entry
        payment_frame = tk.LabelFrame(summary_frame, text="Make Payment", font=("Arial", 12, "bold"))
        payment_frame.pack(side="right", padx=(10, 0))
        
        # Payment fields in horizontal layout
        fields_frame = tk.Frame(payment_frame)
        fields_frame.pack(padx=10, pady=5)
        
        tk.Label(fields_frame, text="Amount:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5)
        self.supplier_payment_entry = tk.Entry(fields_frame, width=10, font=("Arial", 10))
        self.supplier_payment_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(fields_frame, text="Method:", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5, pady=5)
        self.supplier_payment_method = tk.StringVar(value="CASH")
        method_combo = ttk.Combobox(fields_frame, textvariable=self.supplier_payment_method, 
                                   values=["CASH", "MPESA", "BANK"], width=8, font=("Arial", 10))
        method_combo.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(fields_frame, text="Reference:", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=5, pady=5)
        self.supplier_ref_entry = tk.Entry(fields_frame, width=20, font=("Arial", 10))
        self.supplier_ref_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        
        # Buttons below
        button_frame = tk.Frame(payment_frame)
        button_frame.pack(padx=10, pady=10)
        
        tk.Button(button_frame, text="PAY", command=self.make_supplier_payment,
                 bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), width=12, height=2).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Payment History", command=self.show_payment_history,
                 bg="#9C27B0", fg="white", font=("Arial", 10, "bold"), width=12, height=1).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Print Statement", command=self.export_supplier_statement,
                 bg="#FF6B35", fg="white", font=("Arial", 10, "bold"), width=12, height=1).pack(side="left", padx=5)
        
        # Load suppliers on tab creation
        self.refresh_suppliers()
    
    def refresh_suppliers(self):
        purchases = self.load_purchases()
        suppliers = list(set(p['supplier'] for p in purchases if p.get('supplier')))
        self.supplier_combo['values'] = sorted(suppliers)
    
    def load_supplier_statement(self):
        supplier = self.supplier_var.get().strip()
        if not supplier:
            messagebox.showwarning("Warning", "Please select a supplier")
            return
        
        # Clear existing data
        for item in self.supplier_tree.get_children():
            self.supplier_tree.delete(item)
        
        purchases = self.load_purchases()
        supplier_purchases = [p for p in purchases if p.get('supplier', '').lower() == supplier.lower()]
        
        if not supplier_purchases:
            messagebox.showinfo("Info", f"No purchases found for {supplier}")
            return
        
        total_purchases = 0
        total_paid = 0
        outstanding = 0
        
        for purchase in supplier_purchases:
            date_str = datetime.fromisoformat(purchase['purchase_date']).strftime('%Y-%m-%d') if purchase.get('purchase_date') else 'N/A'
            paid_status = "Yes" if purchase.get('paid', False) else "No"
            balance = purchase.get('balance', purchase.get('total', 0))
            
            self.supplier_tree.insert("", "end", values=(
                date_str,
                purchase.get('item', ''),
                purchase.get('quantity', 0),
                f"KSH {purchase.get('total', 0):.2f}",
                paid_status,
                f"KSH {balance:.2f}"
            ))
            
            total_purchases += purchase.get('total', 0)
            if purchase.get('paid', False):
                total_paid += purchase.get('total', 0) - balance
            outstanding += balance
        
        # Update summary labels
        self.total_purchases_label.config(text=f"Total Purchases: KSH {total_purchases:.2f}")
        self.total_paid_label.config(text=f"Total Paid: KSH {total_paid:.2f}")
        self.outstanding_label.config(text=f"Outstanding: KSH {outstanding:.2f}")
    
    def make_supplier_payment(self):
            
        supplier = self.supplier_var.get().strip()
        amount_str = self.supplier_payment_entry.get().strip()
        reference = self.supplier_ref_entry.get().strip()
        
        if not all([supplier, amount_str]):
            messagebox.showerror("Error", "Supplier and amount are required")
            return
        
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be positive")
            
            purchases = self.load_purchases()
            supplier_purchases = [p for p in purchases if p.get('supplier', '').lower() == supplier.lower() and not p.get('paid', False)]
            
            if not supplier_purchases:
                messagebox.showinfo("Info", "No outstanding purchases for this supplier")
                return
            
            # Apply payment to oldest purchases first
            remaining_payment = amount
            updated = False
            
            for purchase in sorted(supplier_purchases, key=lambda x: x.get('purchase_date', '')):
                if remaining_payment <= 0:
                    break
                
                balance = purchase.get('balance', purchase.get('total', 0))
                if balance > 0:
                    payment_applied = min(remaining_payment, balance)
                    purchase['balance'] = balance - payment_applied
                    remaining_payment -= payment_applied
                    
                    if purchase['balance'] <= 0:
                        purchase['paid'] = True
                        purchase['balance'] = 0
                    
                    updated = True
            
            if updated:
                self.save_purchases(purchases)
                
                # Record payment
                payments = self.load_payments()
                new_payment = {
                    "id": len(payments) + 1,
                    "supplier": supplier,
                    "amount": amount,
                    "method": self.supplier_payment_method.get(),
                    "reference": reference,
                    "payment_date": datetime.now().isoformat(),
                    "type": "supplier_payment"
                }
                payments.append(new_payment)
                self.save_payments(payments)
                
                messagebox.showinfo("Success", f"Payment of KSH {amount:.2f} applied to {supplier}")
                
                # Clear form and refresh
                self.supplier_payment_entry.delete(0, tk.END)
                self.supplier_ref_entry.delete(0, tk.END)
                self.supplier_payment_method.set("CASH")
                self.load_supplier_statement()
            else:
                messagebox.showwarning("Warning", "No payment could be applied")
                
        except ValueError:
            messagebox.showerror("Error", "Invalid amount")
        except Exception as e:
            messagebox.showerror("Error", f"Could not process payment: {e}")
    
    def export_supplier_statement(self):
        supplier = self.supplier_var.get().strip()
        if not supplier:
            messagebox.showwarning("Warning", "Please select a supplier first")
            return
        
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title=f"Save {supplier} Statement"
            )
            
            if not filename:
                return
            
            purchases = self.load_purchases()
            supplier_purchases = [p for p in purchases if p.get('supplier', '').lower() == supplier.lower()]
            
            if not supplier_purchases:
                messagebox.showinfo("Info", f"No purchases found for {supplier}")
                return
            
            c = canvas.Canvas(filename, pagesize=letter)
            width, height = letter
            
            # Title
            c.setFont("Helvetica-Bold", 16)
            title = f"Supplier Statement - {supplier}"
            title_width = c.stringWidth(title, "Helvetica-Bold", 16)
            c.drawString((width - title_width) / 2, height - 50, title)
            
            c.setFont("Helvetica", 12)
            c.drawString(50, height - 80, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Headers
            c.setFont("Helvetica-Bold", 10)
            y = height - 120
            c.drawString(50, y, "Date")
            c.drawString(120, y, "Item")
            c.drawString(220, y, "Qty")
            c.drawString(260, y, "Amount")
            c.drawString(320, y, "Paid")
            c.drawString(360, y, "Balance")
            
            # Data
            c.setFont("Helvetica", 9)
            y -= 20
            total_purchases = 0
            total_paid = 0
            outstanding = 0
            
            for purchase in sorted(supplier_purchases, key=lambda x: x.get('purchase_date', '')):
                if y < 50:
                    c.showPage()
                    y = height - 50
                
                date_str = datetime.fromisoformat(purchase['purchase_date']).strftime('%Y-%m-%d') if purchase.get('purchase_date') else 'N/A'
                paid_status = "Yes" if purchase.get('paid', False) else "No"
                balance = purchase.get('balance', purchase.get('total', 0))
                amount = purchase.get('total', 0)
                
                c.drawString(50, y, date_str)
                c.drawString(120, y, str(purchase.get('item', ''))[:12])
                c.drawString(220, y, str(purchase.get('quantity', 0)))
                c.drawString(260, y, f"KSH {amount:.2f}")
                c.drawString(320, y, paid_status)
                c.drawString(360, y, f"KSH {balance:.2f}")
                
                total_purchases += amount
                if purchase.get('paid', False):
                    total_paid += amount - balance
                outstanding += balance
                y -= 15
            
            # Summary
            y -= 20
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "SUMMARY:")
            y -= 20
            c.setFont("Helvetica", 11)
            c.drawString(50, y, f"Total Purchases: KSH {total_purchases:.2f}")
            y -= 15
            c.drawString(50, y, f"Total Paid: KSH {total_paid:.2f}")
            y -= 15
            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, y, f"Outstanding Balance: KSH {outstanding:.2f}")
            
            # Timestamp at bottom
            c.setFont("Helvetica", 8)
            c.drawString(50, 30, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            c.save()
            messagebox.showinfo("Success", f"Statement PDF saved!\nLocation: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not create PDF: {e}")
    
    
    def update_dashboard(self):
        try:
            month = int(self.summary_month_var.get())
            year = int(self.summary_year_var.get())
            
            # Create date range for the selected month
            start_date = datetime(year, month, 1).date()
            if month == 12:
                end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
            else:
                end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
            
            purchases, sales = self.get_data_by_period(start_date, end_date)
            
            # Update stats cards
            total_sales = sum(s.get('total_amount', 0) for s in sales)
            total_purchases = sum(p.get('total', 0) for p in purchases)
            profit = total_sales - total_purchases
            profit_margin = (profit / total_sales * 100) if total_sales > 0 else 0
            
            self.sales_amount_label.config(text=f"KSH {total_sales:,.2f}")
            self.sales_count_label.config(text=f"{len(sales)} transactions")
            
            self.purchases_amount_label.config(text=f"KSH {total_purchases:,.2f}")
            self.purchases_count_label.config(text=f"{len(purchases)} transactions")
            
            self.profit_amount_label.config(text=f"KSH {profit:,.2f}")
            self.profit_margin_label.config(text=f"{profit_margin:.1f}% margin")
            
            # Update profit card color based on profit
            if profit > 0:
                self.profit_card.config(bg="#4CAF50")
                for widget in self.profit_card.winfo_children():
                    widget.config(bg="#4CAF50")
            elif profit < 0:
                self.profit_card.config(bg="#f44336")
                for widget in self.profit_card.winfo_children():
                    widget.config(bg="#f44336")
            else:
                self.profit_card.config(bg="#9E9E9E")
                for widget in self.profit_card.winfo_children():
                    widget.config(bg="#9E9E9E")
            
            # Update graph
            if MATPLOTLIB_AVAILABLE:
                self.update_sales_graph()
            
            # Update details
            self.update_details(purchases, sales, month, year)
            
        except ValueError:
            messagebox.showerror("Error", "Please select valid month and year")
    
    def update_sales_graph(self):
        if not MATPLOTLIB_AVAILABLE:
            return
            
        try:
            # Clear previous graph
            for widget in self.graph_frame.winfo_children():
                if hasattr(widget, 'get_tk_widget'):
                    widget.get_tk_widget().destroy()
                elif str(type(widget)) != "<class 'tkinter.Label'>":
                    widget.destroy()
            
            sales = self.load_sales()
            if not sales:
                return
            
            # Group sales by month (last 12 months)
            monthly_data = {}
            current_date = datetime.now().date()
            
            for i in range(12):
                month_date = current_date.replace(day=1) - timedelta(days=i*30)
                month_key = month_date.strftime('%Y-%m')
                monthly_data[month_key] = 0
            
            for sale in sales:
                try:
                    sale_date_str = sale['sale_date']
                    if 'T' in sale_date_str:
                        sale_date = datetime.fromisoformat(sale_date_str)
                    else:
                        sale_date = datetime.strptime(sale_date_str[:10], '%Y-%m-%d')
                    
                    month_key = sale_date.strftime('%Y-%m')
                    if month_key in monthly_data:
                        monthly_data[month_key] += sale.get('total_amount', 0)
                except:
                    continue
            
            # Create graph
            fig, ax = plt.subplots(figsize=(8, 4))
            fig.patch.set_facecolor('white')
            
            sorted_months = sorted(monthly_data.keys())
            amounts = [monthly_data[month] for month in sorted_months]
            
            ax.plot(sorted_months, amounts, color='#4CAF50', marker='o', linewidth=3, markersize=8)
            ax.fill_between(sorted_months, amounts, alpha=0.3, color='#4CAF50')
            ax.set_ylabel('Sales (KSH)', fontsize=10)
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
            
            plt.xticks(rotation=45, fontsize=8)
            plt.yticks(fontsize=8)
            plt.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
            
        except Exception as e:
            pass
    
    def show_pdf_options(self):
        # Reset dropdown to show options
        self.pdf_var.set("Select Report")
    
    def download_selected_pdf(self, event=None):
        selection = self.pdf_var.get()
        
        if selection == "Weekly Sales":
            self.download_summary_pdf("week")
        elif selection == "Weekly Purchases":
            self.download_weekly_purchases_pdf()
        elif selection == "Monthly Sales":
            self.download_summary_pdf("sales")
        elif selection == "Monthly Purchases":
            self.download_summary_pdf("purchases")
        
        # Reset dropdown
        self.pdf_var.set("Select Report")
    
    def update_details(self, purchases, sales, month, year):
        self.details_text.delete(1.0, tk.END)
        
        details = f"📅 {month:02d}/{year} SUMMARY\n"
        details += "="*30 + "\n\n"
        
        if sales:
            details += "💰 RECENT SALES:\n"
            for sale in sales[-5:]:
                try:
                    date_str = sale['sale_date'][:10] if sale.get('sale_date') else 'N/A'
                    invoice = sale.get('invoice_no', 'N/A')
                    customer = sale.get('customer_name', '')[:15]
                    amount = sale.get('total_amount', 0)
                    details += f"• {date_str} [{invoice}]\n  {customer} - KSH {amount:,.2f}\n\n"
                except:
                    continue
        
        if purchases:
            details += "\n📦 RECENT PURCHASES:\n"
            for purchase in purchases[-5:]:
                try:
                    date_str = purchase['purchase_date'][:10] if purchase.get('purchase_date') else 'N/A'
                    supplier = purchase.get('supplier', '')[:15]
                    item = purchase.get('item', '')[:15]
                    amount = purchase.get('total', 0)
                    details += f"• {date_str}\n  {supplier} - {item}\n  KSH {amount:,.2f}\n\n"
                except:
                    continue
        
        self.details_text.insert(1.0, details)
    
    def filter_summary_data(self):
        try:
            month = int(self.summary_month_var.get())
            year = int(self.summary_year_var.get())
            
            # Create date range for the selected month
            start_date = datetime(year, month, 1).date()
            if month == 12:
                end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
            else:
                end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
            
            purchases, sales = self.get_data_by_period(start_date, end_date)
            
            total_purchases = sum(p.get('total', 0) for p in purchases)
            total_sales = sum(s.get('total_amount', 0) for s in sales)
            profit = total_sales - total_purchases
            
            summary = f"MONTHLY SUMMARY - {month:02d}/{year}\n"
            summary += f"Period: {start_date} to {end_date}\n"
            summary += "="*60 + "\n\n"
            summary += f"📊 SUMMARY STATISTICS\n"
            summary += f"Total Purchases: KSH {total_purchases:.2f} ({len(purchases)} transactions)\n"
            summary += f"Total Sales: KSH {total_sales:.2f} ({len(sales)} transactions)\n"
            summary += f"Net Profit: KSH {profit:.2f}\n"
            summary += f"Items Sold: {sum(sum(item['quantity'] for item in s.get('items', [])) for s in sales)}\n\n"
            
            if purchases:
                summary += f"📦 PURCHASES ({len(purchases)} total)\n"
                for p in purchases:
                    try:
                        purchase_date_str = p['purchase_date']
                        if 'T' in purchase_date_str:
                            date_str = datetime.fromisoformat(purchase_date_str).strftime('%Y-%m-%d')
                        else:
                            date_str = purchase_date_str[:10]
                    except:
                        date_str = 'N/A'
                    invoice_ref = p.get('invoice_ref', 'N/A')
                    summary += f"• {date_str} [{invoice_ref}]: {p.get('supplier', '')} - {p.get('item', '')} x{p.get('quantity', 0)} = KSH {p.get('total', 0):.2f}\n"
            else:
                summary += f"📦 No purchases found for this period\n"
            
            if sales:
                summary += f"\n💰 SALES ({len(sales)} total)\n"
                for s in sales:
                    try:
                        sale_date_str = s['sale_date']
                        if 'T' in sale_date_str:
                            date_str = datetime.fromisoformat(sale_date_str).strftime('%Y-%m-%d')
                        else:
                            date_str = sale_date_str[:10]
                    except:
                        date_str = 'N/A'
                    invoice_no = s.get('invoice_no', 'N/A')
                    summary += f"• {date_str} [{invoice_no}]: {s.get('customer_name', '')} - KSH {s.get('total_amount', 0):.2f}\n"
            else:
                summary += f"\n💰 No sales found for this period\n"
            
            # This method is kept for compatibility but dashboard uses update_dashboard
            self.update_dashboard()
            
        except ValueError:
            messagebox.showerror("Error", "Please select valid month and year")
    
    def download_weekly_purchases_pdf(self):
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        purchases, _ = self.get_data_by_period(start_date, end_date)
        self.export_purchases_only_pdf(purchases, start_date, end_date)
    

    

    
    def backup_data(self):
        try:
            from datetime import datetime
            import shutil
            
            # Create backup folder with timestamp
            backup_time = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_folder = f"backup_{backup_time}"
            
            if not os.path.exists(backup_folder):
                os.makedirs(backup_folder)
            
            # List of data files to backup
            data_files = ['purchases.json', 'sales.json', 'orders.json', 'payments.json']
            backed_up = []
            
            for file in data_files:
                if os.path.exists(file):
                    shutil.copy2(file, backup_folder)
                    backed_up.append(file)
            
            if backed_up:
                messagebox.showinfo("Backup Complete", 
                                  f"Data backed up successfully!\n\nLocation: {backup_folder}\nFiles: {', '.join(backed_up)}")
            else:
                messagebox.showwarning("No Data", "No data files found to backup")
                
        except Exception as e:
            messagebox.showerror("Backup Error", f"Could not backup data: {e}")
    
    def show_payment_history(self):
        supplier = self.supplier_var.get().strip()
        if not supplier:
            messagebox.showwarning("Warning", "Please select a supplier first")
            return
        
        # Create payment history window
        history_window = tk.Toplevel(self.root)
        history_window.title(f"Payment History - {supplier}")
        history_window.geometry("800x500")
        
        # Header
        tk.Label(history_window, text=f"Payment History for {supplier}", 
                font=("Arial", 16, "bold"), fg="#2E86AB").pack(pady=10)
        
        # Payment history tree
        history_frame = tk.Frame(history_window)
        history_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        history_tree = ttk.Treeview(history_frame, columns=("Date", "Amount", "Method", "Reference"), 
                                   show="headings", height=15)
        for col in ["Date", "Amount", "Method", "Reference"]:
            history_tree.heading(col, text=col)
            history_tree.column(col, width=150, anchor="center")
        
        scrollbar_hist = ttk.Scrollbar(history_frame, orient="vertical", command=history_tree.yview)
        history_tree.configure(yscrollcommand=scrollbar_hist.set)
        
        history_tree.pack(side="left", fill="both", expand=True)
        scrollbar_hist.pack(side="right", fill="y")
        
        # Load payment history
        payments = self.load_payments()
        supplier_payments = [p for p in payments if p.get('supplier', '').lower() == supplier.lower()]
        
        total_paid = 0
        for payment in sorted(supplier_payments, key=lambda x: x.get('payment_date', ''), reverse=True):
            try:
                date_str = datetime.fromisoformat(payment['payment_date']).strftime('%Y-%m-%d %H:%M') if payment.get('payment_date') else 'N/A'
            except:
                date_str = 'N/A'
            
            amount = payment.get('amount', 0)
            method = payment.get('method', 'N/A')
            reference = payment.get('reference', 'N/A')
            
            history_tree.insert("", "end", values=(date_str, f"KSH {amount:,.2f}", method, reference))
            total_paid += amount
        
        # Summary
        summary_frame = tk.Frame(history_window)
        summary_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(summary_frame, text=f"Total Payments Made: KSH {total_paid:,.2f} ({len(supplier_payments)} payments)", 
                font=("Arial", 12, "bold"), fg="#4CAF50").pack()
        
        # Close button
        tk.Button(history_window, text="Close", command=history_window.destroy,
                 bg="#9E9E9E", fg="white", font=("Arial", 10, "bold")).pack(pady=10)
    
    def show_monthly_sales_graph(self):
        # Redirect to dashboard update since graph is now integrated
        self.update_dashboard()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = FullScreenApp()
    app.run()
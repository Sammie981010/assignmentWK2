import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import json
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Global variables
sales_items = []
total_amount = 0.0

def get_sales_file():
    return os.path.join(os.path.dirname(__file__), "sales.json")

def load_sales():
    try:
        if os.path.exists(get_sales_file()):
            with open(get_sales_file(), 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading sales: {e}")
        return []

def save_sales(sales):
    try:
        with open(get_sales_file(), 'w') as f:
            json.dump(sales, f, indent=2, default=str)
        return True
    except Exception as e:
        print(f"Error saving sales: {e}")
        return False

def init_sales_storage():
    try:
        if not os.path.exists(get_sales_file()):
            save_sales([])
        return True
    except Exception as e:
        print(f"Error initializing sales storage: {e}")
        return False

def add_item_to_sale(item_entry, qty_entry, price_entry, items_tree, total_label):
    global sales_items, total_amount
    
    item = item_entry.get().strip()
    qty = qty_entry.get().strip()
    price = price_entry.get().strip()
    
    if not item or not qty or not price:
        messagebox.showerror("Error", "All fields are required")
        return
    
    try:
        qty_val = int(qty)
        price_val = float(price)
        if qty_val <= 0 or price_val <= 0:
            raise ValueError("Values must be positive")
    except ValueError:
        messagebox.showerror("Error", "Quantity must be a positive integer and Price must be a positive number")
        return
    
    item_total = qty_val * price_val
    
    # Add to items list
    sales_items.append({
        "item": item,
        "quantity": qty_val,
        "price": price_val,
        "total": item_total
    })
    
    # Add to tree view
    items_tree.insert("", "end", values=(item, qty_val, f"KSH {price_val:.2f}", f"KSH {item_total:.2f}"))
    
    # Update total
    total_amount += item_total
    total_label.config(text=f"Total: KSH {total_amount:.2f}")
    
    # Clear entries
    item_entry.delete(0, tk.END)
    qty_entry.delete(0, tk.END)
    price_entry.delete(0, tk.END)

def remove_selected_item(items_tree, total_label):
    global sales_items, total_amount
    
    selected = items_tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select an item to remove")
        return
    
    # Get selected item index
    item_index = items_tree.index(selected[0])
    
    # Remove from total
    total_amount -= sales_items[item_index]['total']
    
    # Remove from list and tree
    sales_items.pop(item_index)
    items_tree.delete(selected[0])
    
    # Update total
    total_label.config(text=f"Total: KSH {total_amount:.2f}")

def save_sale(customer_entry, items_tree, total_label):
    global sales_items, total_amount
    
    customer = customer_entry.get().strip()
    
    if not customer:
        messagebox.showerror("Error", "Customer name is required")
        return
    
    if not sales_items:
        messagebox.showerror("Error", "Please add at least one item")
        return
    
    try:
        date_now = datetime.now()
        
        # Load existing sales
        sales = load_sales()
        
        # Create new sale
        new_sale = {
            "id": len(sales) + 1,
            "customer_name": customer,
            "items": sales_items.copy(),
            "total_amount": total_amount,
            "sale_date": date_now.isoformat()
        }
        
        sales.append(new_sale)
        
        # Save to file
        if save_sales(sales):
            messagebox.showinfo("Success", f"Sale saved!\n\nCustomer: {customer}\nItems: {len(sales_items)}\nTotal: KSH {total_amount:.2f}")
            
            # Clear everything
            customer_entry.delete(0, tk.END)
            for item in items_tree.get_children():
                items_tree.delete(item)
            sales_items.clear()
            total_amount = 0.0
            total_label.config(text="Total: KSH 0.00")
        else:
            messagebox.showerror("Error", "Could not save sale to file")
    
    except Exception as e:
        print(f"Error saving sale: {e}")
        messagebox.showerror("Error", f"Could not save sale:\n{e}")

def download_sales_pdf():
    try:
        sales = load_sales()
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
        
        # Create PDF
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        
        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "Sales Report - Decent Foods")
        c.drawString(50, height - 70, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        y = height - 120
        grand_total = 0
        
        for sale in sales:
            # Sale header
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, f"Sale #{sale['id']} - {sale['customer_name']}")
            c.drawString(400, y, sale['sale_date'][:10])
            y -= 20
            
            # Items header
            c.setFont("Helvetica-Bold", 10)
            c.drawString(70, y, "Item")
            c.drawString(250, y, "Qty")
            c.drawString(300, y, "Price")
            c.drawString(350, y, "Total")
            y -= 15
            
            # Items
            c.setFont("Helvetica", 9)
            for item in sale['items']:
                c.drawString(70, y, item['item'][:20])
                c.drawString(250, y, str(item['quantity']))
                c.drawString(300, y, f"KSH {item['price']:.2f}")
                c.drawString(350, y, f"KSH {item['total']:.2f}")
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
        
        c.save()
        messagebox.showinfo("Success", f"PDF saved successfully!\nLocation: {filename}")
        
    except ImportError:
        messagebox.showerror("Error", "ReportLab library not installed.\nInstall with: pip install reportlab")
    except Exception as e:
        messagebox.showerror("Error", f"Could not create PDF: {e}")

def open_sales_window(parent):
    global sales_items, total_amount
    
    # Initialize storage
    if not init_sales_storage():
        messagebox.showerror("Storage Error", "Cannot initialize sales storage.")
        return
    
    # Reset global variables
    sales_items = []
    total_amount = 0.0
    
    sales_win = tk.Toplevel(parent)
    sales_win.title("Sales Entry - CESS FOODS")
    sales_win.geometry("550x450")
    sales_win.resizable(True, True)
    
    # Title
    title_frame = tk.Frame(sales_win, bg="#2E86AB", height=40)
    title_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=0, pady=0)
    title_frame.grid_propagate(False)
    
    tk.Label(title_frame, text="CESS FOODS - SALES", font=("Arial", 12, "bold"), 
             bg="#2E86AB", fg="white").pack(pady=8)
    
    # Customer info
    customer_frame = tk.Frame(sales_win)
    customer_frame.grid(row=1, column=0, columnspan=3, padx=15, pady=5, sticky="ew")
    
    tk.Label(customer_frame, text="Customer:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=3, pady=3, sticky="w")
    customer_entry = tk.Entry(customer_frame, width=35, font=("Arial", 10))
    customer_entry.grid(row=0, column=1, padx=3, pady=3)
    
    # Item entry section
    item_frame = tk.LabelFrame(sales_win, text="Add Items", font=("Arial", 9, "bold"), padx=5, pady=5)
    item_frame.grid(row=2, column=0, columnspan=3, padx=15, pady=5, sticky="ew")
    
    tk.Label(item_frame, text="Item:").grid(row=0, column=0, padx=3, pady=3, sticky="w")
    item_entry = tk.Entry(item_frame, width=15, font=("Arial", 9))
    item_entry.grid(row=0, column=1, padx=3, pady=3)
    
    tk.Label(item_frame, text="Qty:").grid(row=0, column=2, padx=3, pady=3, sticky="w")
    qty_entry = tk.Entry(item_frame, width=8, font=("Arial", 9))
    qty_entry.grid(row=0, column=3, padx=3, pady=3)
    
    tk.Label(item_frame, text="Price (KSH):").grid(row=0, column=4, padx=3, pady=3, sticky="w")
    price_entry = tk.Entry(item_frame, width=8, font=("Arial", 9))
    price_entry.grid(row=0, column=5, padx=3, pady=3)
    
    # Live calculator for item total
    item_total_label = tk.Label(item_frame, text="Item Total: KSH 0.00", font=("Arial", 9, "bold"), fg="#2E86AB")
    item_total_label.grid(row=1, column=0, columnspan=2, padx=3, pady=3, sticky="w")
    
    def update_item_total(*args):
        try:
            q = float(qty_entry.get() or 0)
            p = float(price_entry.get() or 0)
            item_total_label.config(text=f"Item Total: KSH {q*p:.2f}")
        except:
            item_total_label.config(text="Item Total: KSH 0.00")
    
    qty_entry.bind("<KeyRelease>", update_item_total)
    price_entry.bind("<KeyRelease>", update_item_total)
    
    # Add item button
    tk.Button(item_frame, text="Add Item", 
              command=lambda: add_item_to_sale(item_entry, qty_entry, price_entry, items_tree, total_label),
              bg="#4CAF50", fg="white", font=("Arial", 9, "bold")).grid(row=1, column=4, columnspan=2, padx=3, pady=3)
    
    # Items list
    list_frame = tk.LabelFrame(sales_win, text="Sale Items", font=("Arial", 9, "bold"), padx=5, pady=5)
    list_frame.grid(row=3, column=0, columnspan=3, padx=15, pady=5, sticky="ew")
    
    # Treeview for items
    columns = ("Item", "Quantity", "Price", "Total")
    items_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=4)
    
    for col in columns:
        items_tree.heading(col, text=col)
        items_tree.column(col, width=100, anchor="center")
    
    items_tree.grid(row=0, column=0, columnspan=2, padx=3, pady=3)
    
    # Remove item button
    tk.Button(list_frame, text="Remove Selected", 
              command=lambda: remove_selected_item(items_tree, total_label),
              bg="#f44336", fg="white", font=("Arial", 8)).grid(row=1, column=0, padx=3, pady=3, sticky="w")
    
    # Total section
    total_frame = tk.Frame(sales_win, bg="#f8f9fa", relief="ridge", bd=2)
    total_frame.grid(row=4, column=0, columnspan=3, padx=15, pady=5, sticky="ew")
    
    total_label = tk.Label(total_frame, text="Total: KSH 0.00", 
                          font=("Arial", 12, "bold"), bg="#f8f9fa", fg="#2E86AB")
    total_label.pack(pady=5)
    
    # Buttons
    button_frame = tk.Frame(sales_win)
    button_frame.grid(row=5, column=0, columnspan=3, pady=10)
    
    tk.Button(button_frame, text="Save Sale", 
              command=lambda: save_sale(customer_entry, items_tree, total_label),
              bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), 
              width=12, height=1).pack(side=tk.LEFT, padx=5)
    
    tk.Button(button_frame, text="Download PDF", 
              command=download_sales_pdf,
              bg="#FF6B35", fg="white", font=("Arial", 10, "bold"), 
              width=12, height=1).pack(side=tk.LEFT, padx=5)
    
    tk.Button(button_frame, text="Close", 
              command=sales_win.destroy,
              bg="#6c757d", fg="white", font=("Arial", 10, "bold"), 
              width=12, height=1).pack(side=tk.LEFT, padx=5)
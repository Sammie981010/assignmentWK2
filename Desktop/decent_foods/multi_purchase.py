import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import json
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Global variables
purchase_items = []
total_amount = 0.0

def get_data_file():
    return os.path.join(os.path.dirname(__file__), "purchases.json")

def load_purchases():
    try:
        if os.path.exists(get_data_file()):
            with open(get_data_file(), 'r') as f:
                return json.load(f)
        return []
    except:
        return []

def save_purchases(purchases):
    try:
        with open(get_data_file(), 'w') as f:
            json.dump(purchases, f, indent=2, default=str)
        return True
    except:
        return False

def add_item_to_purchase(supplier_entry, item_entry, qty_entry, price_entry, items_tree, total_label):
    global purchase_items, total_amount
    
    supplier = supplier_entry.get().strip()
    item = item_entry.get().strip()
    qty = qty_entry.get().strip()
    price = price_entry.get().strip()
    
    if not supplier or not item or not qty or not price:
        messagebox.showerror("Error", "All fields are required")
        return
    
    try:
        qty_val = int(qty)
        price_val = float(price)
        if qty_val <= 0 or price_val <= 0:
            raise ValueError("Values must be positive")
    except ValueError:
        messagebox.showerror("Error", "Quantity must be positive integer, Price must be positive number")
        return
    
    item_total = qty_val * price_val
    
    purchase_items.append({
        "supplier": supplier,
        "item": item,
        "quantity": qty_val,
        "price": price_val,
        "total": item_total
    })
    
    items_tree.insert("", "end", values=(supplier, item, qty_val, f"KSH {price_val:.2f}", f"KSH {item_total:.2f}"))
    
    total_amount += item_total
    total_label.config(text=f"Total: KSH {total_amount:.2f}")
    
    # Clear entries except supplier
    item_entry.delete(0, tk.END)
    qty_entry.delete(0, tk.END)
    price_entry.delete(0, tk.END)

def remove_selected_item(items_tree, total_label):
    global purchase_items, total_amount
    
    selected = items_tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select an item to remove")
        return
    
    item_index = items_tree.index(selected[0])
    total_amount -= purchase_items[item_index]['total']
    purchase_items.pop(item_index)
    items_tree.delete(selected[0])
    total_label.config(text=f"Total: KSH {total_amount:.2f}")

def save_purchase(supplier_entry, items_tree, total_label):
    global purchase_items, total_amount
    
    if not purchase_items:
        messagebox.showerror("Error", "Please add at least one item")
        return
    
    try:
        date_now = datetime.now()
        purchases = load_purchases()
        
        for item in purchase_items:
            new_purchase = {
                "id": len(purchases) + 1,
                "supplier": item["supplier"],
                "item": item["item"],
                "quantity": item["quantity"],
                "price": item["price"],
                "total": item["total"],
                "purchase_date": date_now.isoformat()
            }
            purchases.append(new_purchase)
        
        if save_purchases(purchases):
            messagebox.showinfo("Success", f"Purchase saved!\nItems: {len(purchase_items)}\nTotal: KSH {total_amount:.2f}")
            
            # Clear everything
            supplier_entry.delete(0, tk.END)
            for item in items_tree.get_children():
                items_tree.delete(item)
            purchase_items.clear()
            total_amount = 0.0
            total_label.config(text="Total: KSH 0.00")
        else:
            messagebox.showerror("Error", "Could not save purchase")
    
    except Exception as e:
        messagebox.showerror("Error", f"Could not save purchase: {e}")

def download_pdf():
    try:
        purchases = load_purchases()
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
        
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "Purchase Report - CESS FOODS")
        c.drawString(50, height - 70, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        c.setFont("Helvetica-Bold", 10)
        y = height - 120
        c.drawString(50, y, "Supplier")
        c.drawString(150, y, "Item")
        c.drawString(250, y, "Qty")
        c.drawString(300, y, "Price")
        c.drawString(370, y, "Total")
        c.drawString(450, y, "Date")
        
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
        
        y -= 10
        c.setFont("Helvetica-Bold", 12)
        c.drawString(320, y, f"Grand Total: KSH {grand_total:.2f}")
        
        c.save()
        messagebox.showinfo("Success", f"PDF saved!\nLocation: {filename}")
        
    except Exception as e:
        messagebox.showerror("Error", f"Could not create PDF: {e}")

def open_purchase_window(parent):
    global purchase_items, total_amount
    
    purchase_items = []
    total_amount = 0.0
    
    purchase_win = tk.Toplevel(parent)
    purchase_win.title("Multi-Item Purchase - CESS FOODS")
    purchase_win.geometry("600x500")
    purchase_win.resizable(True, True)
    
    # Title
    title_frame = tk.Frame(purchase_win, bg="#2E86AB", height=40)
    title_frame.pack(fill="x")
    title_frame.pack_propagate(False)
    
    tk.Label(title_frame, text="CESS FOODS - PURCHASES", font=("Arial", 12, "bold"), 
             bg="#2E86AB", fg="white").pack(pady=8)
    
    # Item entry section
    item_frame = tk.LabelFrame(purchase_win, text="Add Items", font=("Arial", 9, "bold"), padx=5, pady=5)
    item_frame.pack(fill="x", padx=15, pady=5)
    
    tk.Label(item_frame, text="Supplier:").grid(row=0, column=0, padx=3, pady=3, sticky="w")
    supplier_entry = tk.Entry(item_frame, width=15, font=("Arial", 9))
    supplier_entry.grid(row=0, column=1, padx=3, pady=3)
    
    tk.Label(item_frame, text="Item:").grid(row=0, column=2, padx=3, pady=3, sticky="w")
    item_entry = tk.Entry(item_frame, width=15, font=("Arial", 9))
    item_entry.grid(row=0, column=3, padx=3, pady=3)
    
    tk.Label(item_frame, text="Qty:").grid(row=1, column=0, padx=3, pady=3, sticky="w")
    qty_entry = tk.Entry(item_frame, width=8, font=("Arial", 9))
    qty_entry.grid(row=1, column=1, padx=3, pady=3)
    
    tk.Label(item_frame, text="Price (KSH):").grid(row=1, column=2, padx=3, pady=3, sticky="w")
    price_entry = tk.Entry(item_frame, width=8, font=("Arial", 9))
    price_entry.grid(row=1, column=3, padx=3, pady=3)
    
    # Live calculator
    item_total_label = tk.Label(item_frame, text="Item Total: KSH 0.00", font=("Arial", 9, "bold"), fg="#2E86AB")
    item_total_label.grid(row=2, column=0, columnspan=2, padx=3, pady=3, sticky="w")
    
    def update_item_total(*args):
        try:
            q = float(qty_entry.get() or 0)
            p = float(price_entry.get() or 0)
            item_total_label.config(text=f"Item Total: KSH {q*p:.2f}")
        except:
            item_total_label.config(text="Item Total: KSH 0.00")
    
    qty_entry.bind("<KeyRelease>", update_item_total)
    price_entry.bind("<KeyRelease>", update_item_total)
    
    tk.Button(item_frame, text="Add Item", 
              command=lambda: add_item_to_purchase(supplier_entry, item_entry, qty_entry, price_entry, items_tree, total_label),
              bg="#4CAF50", fg="white", font=("Arial", 9, "bold")).grid(row=2, column=2, columnspan=2, padx=3, pady=3)
    
    # Items list
    list_frame = tk.LabelFrame(purchase_win, text="Purchase Items", font=("Arial", 9, "bold"), padx=5, pady=5)
    list_frame.pack(fill="both", expand=True, padx=15, pady=5)
    
    columns = ("Supplier", "Item", "Quantity", "Price", "Total")
    items_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
    
    for col in columns:
        items_tree.heading(col, text=col)
        items_tree.column(col, width=100, anchor="center")
    
    items_tree.pack(fill="both", expand=True, padx=3, pady=3)
    
    tk.Button(list_frame, text="Remove Selected", 
              command=lambda: remove_selected_item(items_tree, total_label),
              bg="#f44336", fg="white", font=("Arial", 8)).pack(pady=3)
    
    # Total section
    total_frame = tk.Frame(purchase_win, bg="#f8f9fa", relief="ridge", bd=2)
    total_frame.pack(fill="x", padx=15, pady=5)
    
    total_label = tk.Label(total_frame, text="Total: KSH 0.00", 
                          font=("Arial", 12, "bold"), bg="#f8f9fa", fg="#2E86AB")
    total_label.pack(pady=5)
    
    # Buttons
    button_frame = tk.Frame(purchase_win)
    button_frame.pack(pady=10)
    
    tk.Button(button_frame, text="Save Purchase", 
              command=lambda: save_purchase(supplier_entry, items_tree, total_label),
              bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), 
              width=12, height=1).pack(side=tk.LEFT, padx=5)
    
    tk.Button(button_frame, text="Download PDF", 
              command=download_pdf,
              bg="#FF6B35", fg="white", font=("Arial", 10, "bold"), 
              width=12, height=1).pack(side=tk.LEFT, padx=5)
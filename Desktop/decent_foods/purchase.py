import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Global variables for entry widgets
entry_supplier = None
entry_item = None
entry_qty = None
entry_price = None
entry_total = None
label_grand_total = None

def get_data_file():
    return os.path.join(os.path.dirname(__file__), "purchases.json")

def load_purchases():
    try:
        if os.path.exists(get_data_file()):
            with open(get_data_file(), 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading purchases: {e}")
        return []

def save_purchases(purchases):
    try:
        with open(get_data_file(), 'w') as f:
            json.dump(purchases, f, indent=2, default=str)
        return True
    except Exception as e:
        print(f"Error saving purchases: {e}")
        return False

def init_storage():
    try:
        if not os.path.exists(get_data_file()):
            save_purchases([])
        print("Storage initialized successfully")
        return True
    except Exception as e:
        print(f"Error initializing storage: {e}")
        return False

def calculate_total(*args):
    try:
        qty = entry_qty.get().strip()
        price = entry_price.get().strip()
        
        if qty and price:
            qty_val = float(qty)
            price_val = float(price)
            total = qty_val * price_val
            
            entry_total.config(state="normal")
            entry_total.delete(0, tk.END)
            entry_total.insert(0, f"{total:.2f}")
            entry_total.config(state="readonly")
        else:
            entry_total.config(state="normal")
            entry_total.delete(0, tk.END)
            entry_total.insert(0, "0.00")
            entry_total.config(state="readonly")
    except ValueError:
        entry_total.config(state="normal")
        entry_total.delete(0, tk.END)
        entry_total.insert(0, "0.00")
        entry_total.config(state="readonly")

def update_grand_total():
    purchases = load_purchases()
    grand_total = sum(purchase['total'] for purchase in purchases)
    label_grand_total.config(text=f"Grand Total: ${grand_total:.2f}")

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
        
        # Create PDF
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        
        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "Purchase Report - Decent Foods")
        c.drawString(50, height - 70, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Headers
        c.setFont("Helvetica-Bold", 10)
        y = height - 120
        c.drawString(50, y, "ID")
        c.drawString(80, y, "Supplier")
        c.drawString(180, y, "Item")
        c.drawString(280, y, "Qty")
        c.drawString(320, y, "Price")
        c.drawString(370, y, "Total")
        c.drawString(420, y, "Date")
        
        # Data
        c.setFont("Helvetica", 9)
        y -= 20
        grand_total = 0
        
        for purchase in purchases:
            if y < 50:
                c.showPage()
                y = height - 50
            
            c.drawString(50, y, str(purchase['id']))
            c.drawString(80, y, purchase['supplier'][:12])
            c.drawString(180, y, purchase['item'][:12])
            c.drawString(280, y, str(purchase['quantity']))
            c.drawString(320, y, f"${purchase['price']:.2f}")
            c.drawString(370, y, f"${purchase['total']:.2f}")
            c.drawString(420, y, purchase['purchase_date'][:10])
            
            grand_total += purchase['total']
            y -= 15
        
        # Grand total
        y -= 10
        c.setFont("Helvetica-Bold", 12)
        c.drawString(320, y, f"Grand Total: ${grand_total:.2f}")
        
        c.save()
        messagebox.showinfo("Success", f"PDF saved successfully!\nLocation: {filename}")
        
    except ImportError:
        messagebox.showerror("Error", "ReportLab library not installed.\nInstall with: pip install reportlab")
    except Exception as e:
        messagebox.showerror("Error", f"Could not create PDF: {e}")

def save_purchase():
    supplier = entry_supplier.get().strip()
    item = entry_item.get().strip()
    qty = entry_qty.get().strip()
    price = entry_price.get().strip()

    if not supplier or not item or not qty or not price:
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

    try:
        total = qty_val * price_val
        date_now = datetime.now()

        # Load existing purchases
        purchases = load_purchases()
        
        # Add new purchase
        new_purchase = {
            "id": len(purchases) + 1,
            "supplier": supplier,
            "item": item,
            "quantity": qty_val,
            "price": price_val,
            "total": total,
            "purchase_date": date_now.isoformat()
        }
        
        purchases.append(new_purchase)
        
        # Save to file
        if save_purchases(purchases):
            messagebox.showinfo("Success", f"Purchase saved!\n\nSupplier: {supplier}\nItem: {item}\nTotal: ${total:.2f}\nTime: {date_now.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Clear entries
            entry_supplier.delete(0, tk.END)
            entry_item.delete(0, tk.END)
            entry_qty.delete(0, tk.END)
            entry_price.delete(0, tk.END)
            entry_total.config(state="normal")
            entry_total.delete(0, tk.END)
            entry_total.insert(0, "0.00")
            entry_total.config(state="readonly")
            
            # Update grand total
            update_grand_total()
        else:
            messagebox.showerror("Error", "Could not save purchase to file")

    except Exception as e:
        print(f"Error saving purchase: {e}")
        messagebox.showerror("Error", f"Could not save purchase:\n{e}")

def clear_form():
    """Clear all form fields"""
    0entry_supplier.delete(0, tk.END)
    entry_item.delete(0, tk.END)
    entry_qty.delete(0, tk.END)
    entry_price.delete(0, tk.END)
    entry_total.config(state="normal")
    entry_total.delete(0, tk.END)
    entry_total.insert(0, "0.00")
    entry_total.config(state="readonly")

def open_purchase_window(parent):
    global entry_supplier, entry_item, entry_qty, entry_price, entry_total, label_grand_total
    
    # Initialize file storage
    if not init_storage():
        messagebox.showerror("Storage Error", "Cannot initialize data storage.")
        return
    
    purchase_win = tk.Toplevel(parent)
    purchase_win.title("Purchase Entry - CESS FOODS")
    purchase_win.geometry("450x300")
    purchase_win.resizable(True, True)

    # Title
    title_frame = tk.Frame(purchase_win, bg="#2E86AB", height=40)
    title_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
    title_frame.grid_propagate(False)
    
    tk.Label(title_frame, text="CESS FOODS - PURCHASES", font=("Arial", 12, "bold"), 
             bg="#2E86AB", fg="white").pack(pady=8)

    # Form fields
    tk.Label(purchase_win, text="Supplier:", font=("Arial", 9)).grid(row=1, column=0, padx=5, pady=2, sticky="w")
    entry_supplier = tk.Entry(purchase_win, width=25, font=("Arial", 9))
    entry_supplier.grid(row=1, column=1, padx=5, pady=2)

    tk.Label(purchase_win, text="Item:", font=("Arial", 9)).grid(row=2, column=0, padx=5, pady=2, sticky="w")
    entry_item = tk.Entry(purchase_win, width=25, font=("Arial", 9))
    entry_item.grid(row=2, column=1, padx=5, pady=2)

    tk.Label(purchase_win, text="Quantity:", font=("Arial", 9)).grid(row=3, column=0, padx=5, pady=2, sticky="w")
    entry_qty = tk.Entry(purchase_win, width=25, font=("Arial", 9))
    entry_qty.grid(row=3, column=1, padx=5, pady=2)

    tk.Label(purchase_win, text="Price (KSH):", font=("Arial", 9)).grid(row=4, column=0, padx=5, pady=2, sticky="w")
    entry_price = tk.Entry(purchase_win, width=25, font=("Arial", 9))
    entry_price.grid(row=4, column=1, padx=5, pady=2)

    tk.Label(purchase_win, text="Total (KSH):", font=("Arial", 9)).grid(row=5, column=0, padx=5, pady=2, sticky="w")
    entry_total = tk.Entry(purchase_win, width=25, state="readonly", font=("Arial", 9, "bold"), 
                          bg="#f0f0f0", fg="#2E86AB")
    entry_total.grid(row=5, column=1, padx=5, pady=2)
    entry_total.config(state="normal")
    entry_total.insert(0, "0.00")
    entry_total.config(state="readonly")

    # Bind live calculator
    entry_qty.bind('<KeyRelease>', calculate_total)
    entry_price.bind('<KeyRelease>', calculate_total)

    # Grand total display
    label_grand_total = tk.Label(purchase_win, text="Grand Total: $0.00", 
                                font=("Arial", 10, "bold"), fg="#2E86AB")
    label_grand_total.grid(row=6, column=0, columnspan=2, pady=5)

    # Buttons
    button_frame = tk.Frame(purchase_win)
    button_frame.grid(row=7, column=0, columnspan=2, pady=5)
    
    tk.Button(button_frame, text="Save Purchase", command=save_purchase, 
              bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), 
              width=12, height=1).pack(side=tk.LEFT, padx=5)
    
    tk.Button(button_frame, text="Clear", command=clear_form, 
              bg="#FFC107", fg="black", font=("Arial", 10, "bold"), 
              width=12, height=1).pack(side=tk.LEFT, padx=5)
    
    tk.Button(button_frame, text="Download PDF", command=download_pdf, 
              bg="#FF6B35", fg="white", font=("Arial", 10, "bold"), 
              width=12, height=1).pack(side=tk.LEFT, padx=5)
    
    # Update grand total on window open
    update_grand_total()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    open_purchase_window(root)
    root.mainloop()
import tkinter as tk
from tkinter import messagebox
from fullscreen_app import FullScreenApp

# User credentials
USERS = {"admin": "admin123", "user": "user123"}

def login_window():
    root = tk.Tk()
    root.title("CESS FOODS - Login")
    root.geometry("450x550")
    root.configure(bg="#E3F2FD")  # Light blue background
    root.resizable(False, False)
    
    # Center the window
    root.eval('tk::PlaceWindow . center')
    
    # Main container
    main_frame = tk.Frame(root, bg="#E3F2FD")
    main_frame.pack(fill="both", expand=True, padx=40, pady=40)
    
    # Logo/Title section
    title_frame = tk.Frame(main_frame, bg="#1976D2", relief="raised", bd=3)
    title_frame.pack(fill="x", pady=(0, 20))
    
    tk.Label(title_frame, text="🍽️", font=("Arial", 24), bg="#1976D2", fg="white").pack(pady=5)
    tk.Label(title_frame, text="CESS FOODS", font=("Arial", 18, "bold"), bg="#1976D2", fg="white").pack()
    tk.Label(title_frame, text="Management System", font=("Arial", 10), bg="#1976D2", fg="#BBDEFB").pack(pady=(0, 8))
    
    # Login form container
    form_frame = tk.Frame(main_frame, bg="white", relief="raised", bd=2)
    form_frame.pack(fill="x", pady=20)
    
    # Form title
    tk.Label(form_frame, text="Welcome Back!", font=("Arial", 18, "bold"), bg="white", fg="#1976D2").pack(pady=(20, 10))
    tk.Label(form_frame, text="Please sign in to continue", font=("Arial", 10), bg="white", fg="#666").pack(pady=(0, 20))
    
    # Username field
    tk.Label(form_frame, text="Username", font=("Arial", 11, "bold"), bg="white", fg="#333").pack(anchor="w", padx=30, pady=(10, 5))
    username_entry = tk.Entry(form_frame, font=("Arial", 12), relief="solid", bd=1, bg="#F5F5F5", fg="black")
    username_entry.pack(fill="x", padx=30, pady=(0, 15), ipady=8)
    username_entry.config(insertbackground="black")  # Ensure cursor is visible
    
    # Password field
    tk.Label(form_frame, text="Password", font=("Arial", 11, "bold"), bg="white", fg="#333").pack(anchor="w", padx=30, pady=(0, 5))
    password_entry = tk.Entry(form_frame, show="*", font=("Arial", 12), relief="solid", bd=1, bg="#F5F5F5", fg="black")
    password_entry.pack(fill="x", padx=30, pady=(0, 20), ipady=8)
    password_entry.config(insertbackground="black")  # Ensure cursor is visible
    
    def attempt_login():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        if USERS.get(username) == password:
            root.destroy()
            app = FullScreenApp()
            app.run()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")
            password_entry.delete(0, tk.END)
    
    # Login button
    login_btn = tk.Button(form_frame, text="LOGIN", command=attempt_login,
                         font=("Arial", 12, "bold"), bg="#1976D2", fg="white",
                         relief="flat", cursor="hand2", width=20, height=2)
    login_btn.pack(pady=20)
    
    # Hover effects
    def on_enter(e):
        login_btn.config(bg="#1565C0")
    def on_leave(e):
        login_btn.config(bg="#1976D2")
    
    login_btn.bind("<Enter>", on_enter)
    login_btn.bind("<Leave>", on_leave)
    
    # Footer
    footer_frame = tk.Frame(main_frame, bg="#E3F2FD")
    footer_frame.pack(fill="x", pady=(20, 0))
    
    tk.Label(footer_frame, text="Default Login: admin / admin123", 
             font=("Arial", 9), bg="#E3F2FD", fg="#666").pack()
    tk.Label(footer_frame, text="© 2024 CESS FOODS. All rights reserved.", 
             font=("Arial", 8), bg="#E3F2FD", fg="#999").pack(pady=(5, 0))
    
    # Enter key binding
    def on_enter_key(event):
        attempt_login()
    
    root.bind('<Return>', on_enter_key)
    username_entry.focus()
    
    root.mainloop()

if __name__ == "__main__":
    login_window()

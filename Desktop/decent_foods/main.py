#!/usr/bin/env python3
"""
CESS FOODS Management System
Desktop Application Entry Point
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

def main():
    """Main entry point for the desktop application"""
    try:
        # Import and run the login window
        from login import login_window
        login_window()
    except ImportError as e:
        messagebox.showerror("Import Error", f"Failed to import required modules:\n{e}")
        sys.exit(1)
    except Exception as e:
        messagebox.showerror("Application Error", f"An error occurred:\n{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox
import subprocess

def insert_data():
    """Collect name and age from entry fields, insert them as JSON via the C++ database app."""
    name = name_entry.get().strip()
    age = age_entry.get().strip()

    if not name or not age:
        messagebox.showerror("Error", "Please fill in both name and age.")
        return

    # Construct JSON data (very simplistic; no validation here).
    json_data = f'{{"name":"{name}","age":{age}}}'

    # Call the C++ insert command:
    #  ./mydbapp MyDatabase insert <json_data>
    try:
        result = subprocess.run(
            ["/var/www/html/jocarsa-cyan/cyan.out", "MyDatabase", "insert", json_data], 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            messagebox.showinfo("Success", f"Inserted: {json_data}")
        else:
            messagebox.showerror("Error inserting data", result.stderr)
    except Exception as e:
        messagebox.showerror("Exception", str(e))

def retrieve_data():
    """Retrieve all data from the database via the C++ app and display in the text box."""
    try:
        result = subprocess.run(
            ["/var/www/html/jocarsa-cyan/cyan.out", "MyDatabase", "select"], 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            # Display the output in the text widget
            results_text.delete("1.0", tk.END)  # Clear existing text
            results_text.insert(tk.END, result.stdout)
        else:
            messagebox.showerror("Error retrieving data", result.stderr)
    except Exception as e:
        messagebox.showerror("Exception", str(e))

# Create the main window
root = tk.Tk()
root.title("Simple JSON Database GUI")

# Labels and entry fields
tk.Label(root, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
name_entry = tk.Entry(root, width=30)
name_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="Age:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
age_entry = tk.Entry(root, width=30)
age_entry.grid(row=1, column=1, padx=5, pady=5)

# Buttons
insert_btn = tk.Button(root, text="Insert", command=insert_data)
insert_btn.grid(row=2, column=0, padx=5, pady=10, sticky="ew")

retrieve_btn = tk.Button(root, text="Retrieve", command=retrieve_data)
retrieve_btn.grid(row=2, column=1, padx=5, pady=10, sticky="ew")

# Text widget for displaying results
results_text = tk.Text(root, width=60, height=10)
results_text.grid(row=3, column=0, columnspan=2, padx=5, pady=10)

root.mainloop()

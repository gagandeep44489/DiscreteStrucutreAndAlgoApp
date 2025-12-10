import tkinter as tk
from tkinter import messagebox, ttk
from sympy import symbols, sympify, simplify_logic

def simplify_expression():
    expr = input_box.get()

    if not expr.strip():
        messagebox.showerror("Input Error", "Please enter a Boolean expression.")
        return

    try:
        # Simplify expression using SymPy
        simplified = simplify_logic(sympify(expr), form="dnf")
        result_box.config(state="normal")
        result_box.delete("1.0", tk.END)
        result_box.insert(tk.END, str(simplified))
        result_box.config(state="disabled")

    except Exception as e:
        messagebox.showerror("Error", f"Invalid Boolean Expression.\n{e}")


# ---------------- GUI ----------------

root = tk.Tk()
root.title("Boolean Expression Simplifier")
root.geometry("600x400")
root.resizable(False, False)

title_label = tk.Label(
    root,
    text="Boolean Expression Simplifier",
    font=("Arial", 18, "bold")
)
title_label.pack(pady=10)

# Input Frame
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

input_label = tk.Label(
    input_frame,
    text="Enter Expression:",
    font=("Arial", 12)
)
input_label.grid(row=0, column=0, sticky="w")

input_box = tk.Entry(input_frame, width=50, font=("Arial", 12))
input_box.grid(row=0, column=1, padx=10)

# Buttons
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

simplify_btn = tk.Button(
    btn_frame,
    text="Simplify",
    font=("Arial", 12, "bold"),
    width=12,
    command=simplify_expression
)
simplify_btn.grid(row=0, column=0, padx=10)

quit_btn = tk.Button(
    btn_frame,
    text="Exit",
    font=("Arial", 12),
    width=12,
    command=root.quit
)
quit_btn.grid(row=0, column=1, padx=10)

# Result Frame
result_label = tk.Label(
    root,
    text="Simplified Expression:",
    font=("Arial", 12)
)
result_label.pack()

result_box = tk.Text(root, height=10, width=70, font=("Arial", 12))
result_box.pack(pady=10)
result_box.config(state="disabled")

root.mainloop()

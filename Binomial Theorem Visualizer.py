import tkinter as tk
from tkinter import ttk, messagebox
import math

def generate_pascals_triangle(n):
    triangle = []
    for i in range(n + 1):
        row = [1] * (i + 1)
        for j in range(1, i):
            row[j] = triangle[i - 1][j - 1] + triangle[i - 1][j]
        triangle.append(row)
    return triangle

def expand_binomial(a, b, n):
    terms = []
    triangle = generate_pascals_triangle(n)
    coefficients = triangle[n]

    for k in range(n + 1):
        coeff = coefficients[k]
        term = f"{coeff} * {a}^{n-k} * {b}^{k}"
        value = coeff * (a ** (n - k)) * (b ** k)
        terms.append((term, value))

    return terms, coefficients

def visualize():
    try:
        a = float(entry_a.get())
        b = float(entry_b.get())
        n = int(entry_n.get())

        if n < 0 or n > 20:
            messagebox.showerror("Error", "Power n must be between 0 and 20.")
            return

        terms, coefficients = expand_binomial(a, b, n)

        result_text.delete(1.0, tk.END)

        result_text.insert(tk.END, f"Pascal's Triangle Row for n={n}:\n{coefficients}\n\n")
        result_text.insert(tk.END, f"Expansion of (a + b)^{n}:\n\n")

        full_expansion = []
        for t, v in terms:
            full_expansion.append(t)
            result_text.insert(tk.END, f"{t} = {v}\n")

        result_text.insert(tk.END, "\nFinal Expansion:\n")
        result_text.insert(tk.END, " + ".join(full_expansion))

    except ValueError:
        messagebox.showerror("Error", "Please enter valid numerical values.")

# ----------- GUI PART --------------
root = tk.Tk()
root.title("Binomial Theorem Visualizer")
root.geometry("650x520")
root.resizable(False, False)

title = tk.Label(root, text="Binomial Theorem Visualizer", font=("Arial", 20, "bold"))
title.pack(pady=10)

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Value of a:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5)
entry_a = tk.Entry(frame, width=10, font=("Arial", 12))
entry_a.grid(row=0, column=1)

tk.Label(frame, text="Value of b:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5)
entry_b = tk.Entry(frame, width=10, font=("Arial", 12))
entry_b.grid(row=1, column=1)

tk.Label(frame, text="Power n:", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=5)
entry_n = tk.Entry(frame, width=10, font=("Arial", 12))
entry_n.grid(row=2, column=1)

btn = tk.Button(root, text="Visualize Expansion", command=visualize,
                font=("Arial", 14), bg="#4CAF50", fg="white", width=20)
btn.pack(pady=15)

result_text = tk.Text(root, height=18, width=75, font=("Courier", 10))
result_text.pack()

root.mainloop()

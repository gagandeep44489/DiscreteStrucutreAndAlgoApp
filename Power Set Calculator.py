import tkinter as tk
from tkinter import messagebox
from itertools import combinations

def calculate_power_set():
    elements = entry.get().strip()
    
    if not elements:
        messagebox.showerror("Input Error", "Please enter at least one element.")
        return
    
    # Split input and remove duplicates
    items = list(set([e.strip() for e in elements.split(",") if e.strip() != ""]))
    n = len(items)
    
    if n > 15:
        messagebox.showwarning("Warning", "Large sets may take time to compute.")
    
    power_set = []
    
    for r in range(n + 1):
        for subset in combinations(items, r):
            power_set.append(subset)
    
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, f"Original Set: {set(items)}\n\n")
    output_text.insert(tk.END, f"Total Subsets: {len(power_set)} (2^{n})\n\n")
    output_text.insert(tk.END, "Power Set:\n\n")
    
    for subset in power_set:
        output_text.insert(tk.END, f"{set(subset)}\n")

# GUI Setup
root = tk.Tk()
root.title("Power Set Calculator")
root.geometry("600x500")

title_label = tk.Label(root, text="Power Set Calculator", font=("Arial", 16, "bold"))
title_label.pack(pady=10)

input_label = tk.Label(root, text="Enter elements separated by commas:")
input_label.pack()

entry = tk.Entry(root, width=50)
entry.pack(pady=5)

calculate_button = tk.Button(root, text="Generate Power Set", command=calculate_power_set)
calculate_button.pack(pady=10)

output_text = tk.Text(root, height=20, width=70)
output_text.pack(pady=10)

scrollbar = tk.Scrollbar(root, command=output_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
output_text.config(yscrollcommand=scrollbar.set)

root.mainloop()

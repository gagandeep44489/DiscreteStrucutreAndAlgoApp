import tkinter as tk
from tkinter import messagebox
from itertools import combinations

def generate_subsets():
    input_data = entry_set.get().strip()

    if not input_data:
        messagebox.showerror("Error", "Please enter set elements.")
        return

    elements = [x.strip() for x in input_data.split(",") if x.strip()]
    result_box.delete("1.0", tk.END)

    result_box.insert(tk.END, "Subsets:\n\n")

    count = 0
    for r in range(len(elements) + 1):
        for subset in combinations(elements, r):
            result_box.insert(tk.END, f"{set(subset)}\n")
            count += 1

    result_box.insert(tk.END, f"\nTotal Subsets: {count}")

# GUI Setup
root = tk.Tk()
root.title("Subset Generator")
root.geometry("500x450")

tk.Label(root, text="Enter Set Elements (comma-separated):").pack(pady=5)

entry_set = tk.Entry(root, width=50)
entry_set.pack(pady=5)

tk.Button(root, text="Generate Subsets", command=generate_subsets).pack(pady=10)

result_box = tk.Text(root, height=18, width=55)
result_box.pack(pady=5)

root.mainloop()

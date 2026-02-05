import tkinter as tk
from tkinter import messagebox

# -------------------------
# Perform Set Operations
# -------------------------
def perform_operations():
    try:
        set_a = set(map(int, entry_a.get().split(",")))
        set_b = set(map(int, entry_b.get().split(",")))

        union = set_a | set_b
        intersection = set_a & set_b
        diff_ab = set_a - set_b
        diff_ba = set_b - set_a
        sym_diff = set_a ^ set_b

        result_text.set(
            f"Union (A ∪ B): {union}\n\n"
            f"Intersection (A ∩ B): {intersection}\n\n"
            f"Difference (A − B): {diff_ab}\n\n"
            f"Difference (B − A): {diff_ba}\n\n"
            f"Symmetric Difference: {sym_diff}"
        )

    except ValueError:
        messagebox.showerror(
            "Input Error",
            "Enter comma-separated integers only.\nExample: 1,2,3,4"
        )

# -------------------------
# GUI Setup
# -------------------------
root = tk.Tk()
root.title("Set Operations Visualizer")
root.geometry("500x450")
root.resizable(False, False)

title = tk.Label(
    root,
    text="Set Operations Visualizer",
    font=("Arial", 16, "bold")
)
title.pack(pady=10)

desc = tk.Label(
    root,
    text="Enter elements separated by commas",
    font=("Arial", 10),
    fg="gray"
)
desc.pack()

frame = tk.Frame(root)
frame.pack(pady=15)

tk.Label(frame, text="Set A:", font=("Arial", 11)).grid(row=0, column=0, pady=5, sticky="e")
entry_a = tk.Entry(frame, width=30)
entry_a.grid(row=0, column=1)

tk.Label(frame, text="Set B:", font=("Arial", 11)).grid(row=1, column=0, pady=5, sticky="e")
entry_b = tk.Entry(frame, width=30)
entry_b.grid(row=1, column=1)

btn = tk.Button(
    root,
    text="Perform Set Operations",
    font=("Arial", 12),
    bg="#3498db",
    fg="white",
    command=perform_operations
)
btn.pack(pady=10)

result_text = tk.StringVar()
result_label = tk.Label(
    root,
    textvariable=result_text,
    font=("Arial", 11),
    justify="left",
    wraplength=450
)
result_label.pack(pady=10)

footer = tk.Label(
    root,
    text="Set Theory | Python Desktop App",
    font=("Arial", 9),
    fg="gray"
)
footer.pack(side="bottom", pady=5)

root.mainloop()

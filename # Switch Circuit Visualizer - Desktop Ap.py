# Switch Circuit Visualizer - Desktop App in Python
# Purpose:
# Visualize simple switch-based digital circuits (ON/OFF logic)
# Useful for digital electronics, logic design learning, and education

import tkinter as tk
from tkinter import ttk

# ---------------- Circuit Logic ----------------

def update_output():
    # AND logic: output is ON only if all switches are ON
    if switch1.get() and switch2.get():
        output_label.config(text="OUTPUT: ON", foreground="green")
    else:
        output_label.config(text="OUTPUT: OFF", foreground="red")

# ---------------- Main Window ----------------

root = tk.Tk()
root.title("Switch Circuit Visualizer")
root.geometry("500x350")
root.resizable(False, False)

style = ttk.Style(root)
style.theme_use('clam')

# ---------------- Layout ----------------

frame = ttk.Frame(root, padding=20)
frame.pack(fill=tk.BOTH, expand=True)

header = ttk.Label(frame, text="Switch Circuit Visualizer (AND Circuit)", font=("Segoe UI", 14, "bold"))
header.pack(pady=10)

# Switch Variables
switch1 = tk.BooleanVar()
switch2 = tk.BooleanVar()

# Switches
switch1_cb = ttk.Checkbutton(frame, text="Switch 1", variable=switch1, command=update_output)
switch1_cb.pack(pady=5)

switch2_cb = ttk.Checkbutton(frame, text="Switch 2", variable=switch2, command=update_output)
switch2_cb.pack(pady=5)

# Output Display
output_label = ttk.Label(frame, text="OUTPUT: OFF", font=("Segoe UI", 12, "bold"), foreground="red")
output_label.pack(pady=20)

# Description
desc = ttk.Label(
    frame,
    text="This visualizer simulates a simple AND switch circuit.\n"
         "The output turns ON only when both switches are ON.",
    justify=tk.CENTER
)
desc.pack(pady=10)

root.mainloop()

import tkinter as tk
from tkinter import messagebox

def check_membership():
    elements = set_entry.get().strip()
    test_element = element_entry.get().strip()

    if not elements:
        messagebox.showerror("Input Error", "Please enter set elements.")
        return

    if not test_element:
        messagebox.showerror("Input Error", "Please enter an element to test.")
        return

    # Create set (remove duplicates automatically)
    my_set = set([e.strip() for e in elements.split(",") if e.strip() != ""])

    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, f"Set: {my_set}\n\n")

    if test_element in my_set:
        result_text.insert(tk.END, f"Result: '{test_element}' ∈ Set\n")
    else:
        result_text.insert(tk.END, f"Result: '{test_element}' ∉ Set\n")

# GUI Setup
root = tk.Tk()
root.title("Set Membership Tester")
root.geometry("500x400")

title_label = tk.Label(root, text="Set Membership Tester", font=("Arial", 16, "bold"))
title_label.pack(pady=10)

set_label = tk.Label(root, text="Enter set elements (comma-separated):")
set_label.pack()

set_entry = tk.Entry(root, width=50)
set_entry.pack(pady=5)

element_label = tk.Label(root, text="Enter element to test:")
element_label.pack()

element_entry = tk.Entry(root, width=30)
element_entry.pack(pady=5)

check_button = tk.Button(root, text="Check Membership", command=check_membership)
check_button.pack(pady=10)

result_text = tk.Text(root, height=10, width=60)
result_text.pack(pady=10)

root.mainloop()

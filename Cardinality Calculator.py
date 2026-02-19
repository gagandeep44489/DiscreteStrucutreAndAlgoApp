import tkinter as tk
from tkinter import messagebox

def parse_set(input_text):
    # Split by comma and remove spaces
    elements = input_text.split(",")
    clean_elements = set()
    
    for element in elements:
        element = element.strip()
        if element != "":
            clean_elements.add(element)
    
    return clean_elements

def calculate():
    try:
        set_a = parse_set(entry_a.get())
        set_b = parse_set(entry_b.get())
        
        union_set = set_a.union(set_b)
        intersection_set = set_a.intersection(set_b)
        difference_ab = set_a.difference(set_b)
        difference_ba = set_b.difference(set_a)
        
        result_text.set(
            f"Set A: {set_a}\n"
            f"Set B: {set_b}\n\n"
            f"|A| = {len(set_a)}\n"
            f"|B| = {len(set_b)}\n\n"
            f"A ∪ B = {union_set}\n"
            f"|A ∪ B| = {len(union_set)}\n\n"
            f"A ∩ B = {intersection_set}\n"
            f"|A ∩ B| = {len(intersection_set)}\n\n"
            f"A - B = {difference_ab}\n"
            f"|A - B| = {len(difference_ab)}\n\n"
            f"B - A = {difference_ba}\n"
            f"|B - A| = {len(difference_ba)}"
        )
        
    except Exception as e:
        messagebox.showerror("Error", "Invalid Input")

# Main Window
root = tk.Tk()
root.title("Cardinality Calculator")
root.geometry("500x600")
root.resizable(False, False)

title_label = tk.Label(root, text="Cardinality Calculator", font=("Arial", 16, "bold"))
title_label.pack(pady=10)

# Set A Input
label_a = tk.Label(root, text="Enter elements of Set A (comma separated):")
label_a.pack()

entry_a = tk.Entry(root, width=50)
entry_a.pack(pady=5)

# Set B Input
label_b = tk.Label(root, text="Enter elements of Set B (comma separated):")
label_b.pack()

entry_b = tk.Entry(root, width=50)
entry_b.pack(pady=5)

# Calculate Button
calc_button = tk.Button(root, text="Calculate Cardinality", command=calculate)
calc_button.pack(pady=10)

# Result Area
result_text = tk.StringVar()
result_label = tk.Label(root, textvariable=result_text, justify="left")
result_label.pack(pady=10)

root.mainloop()

import tkinter as tk
from tkinter import messagebox

def parse_set(input_text):
    elements = input_text.split(",")
    return set(e.strip() for e in elements if e.strip() != "")

def parse_relation(input_text):
    pairs = input_text.split(";")
    relation = set()
    
    for pair in pairs:
        pair = pair.strip()
        if pair:
            pair = pair.replace("(", "").replace(")", "")
            a, b = pair.split(",")
            relation.add((a.strip(), b.strip()))
    
    return relation

def is_reflexive(A, R):
    for a in A:
        if (a, a) not in R:
            return False
    return True

def is_irreflexive(A, R):
    for a in A:
        if (a, a) in R:
            return False
    return True

def is_symmetric(R):
    for (a, b) in R:
        if (b, a) not in R:
            return False
    return True

def is_antisymmetric(R):
    for (a, b) in R:
        if a != b and (b, a) in R:
            return False
    return True

def is_transitive(R):
    for (a, b) in R:
        for (c, d) in R:
            if b == c and (a, d) not in R:
                return False
    return True

def check_properties():
    try:
        A = parse_set(entry_set.get())
        R = parse_relation(entry_relation.get())
        
        result = f"Set A: {A}\nRelation R: {R}\n\n"
        
        result += f"Reflexive: {is_reflexive(A, R)}\n"
        result += f"Irreflexive: {is_irreflexive(A, R)}\n"
        result += f"Symmetric: {is_symmetric(R)}\n"
        result += f"Antisymmetric: {is_antisymmetric(R)}\n"
        result += f"Transitive: {is_transitive(R)}\n"
        
        result_text.set(result)
        
    except:
        messagebox.showerror("Error", "Invalid Input Format")

# GUI Setup
root = tk.Tk()
root.title("Relation Property Checker")
root.geometry("550x600")
root.resizable(False, False)

title_label = tk.Label(root, text="Relation Property Checker", font=("Arial", 16, "bold"))
title_label.pack(pady=10)

# Set Input
label_set = tk.Label(root, text="Enter elements of Set A (comma separated):")
label_set.pack()

entry_set = tk.Entry(root, width=60)
entry_set.pack(pady=5)

# Relation Input
label_relation = tk.Label(root, text="Enter relation R (e.g., (1,1);(1,2);(2,2)):")
label_relation.pack()

entry_relation = tk.Entry(root, width=60)
entry_relation.pack(pady=5)

# Button
check_button = tk.Button(root, text="Check Properties", command=check_properties)
check_button.pack(pady=10)

# Result Area
result_text = tk.StringVar()
result_label = tk.Label(root, textvariable=result_text, justify="left")
result_label.pack(pady=10)

root.mainloop()

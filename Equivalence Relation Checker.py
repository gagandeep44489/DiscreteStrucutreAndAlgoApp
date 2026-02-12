import tkinter as tk
from tkinter import messagebox

def check_relation():
    try:
        # Get set elements
        elements_input = entry_set.get()
        elements = set(elements_input.split(","))

        # Get relation pairs
        relation_input = entry_relation.get()
        pairs = relation_input.split(";")
        relation = set()

        for pair in pairs:
            a, b = pair.strip().split(",")
            relation.add((a.strip(), b.strip()))

        reflexive = True
        symmetric = True
        transitive = True

        # Check Reflexive
        for element in elements:
            if (element, element) not in relation:
                reflexive = False
                break

        # Check Symmetric
        for (a, b) in relation:
            if (b, a) not in relation:
                symmetric = False
                break

        # Check Transitive
        for (a, b) in relation:
            for (c, d) in relation:
                if b == c and (a, d) not in relation:
                    transitive = False
                    break

        result_text = (
            f"Reflexive: {reflexive}\n"
            f"Symmetric: {symmetric}\n"
            f"Transitive: {transitive}\n\n"
        )

        if reflexive and symmetric and transitive:
            result_text += "The relation IS an Equivalence Relation."
        else:
            result_text += "The relation is NOT an Equivalence Relation."

        result_label.config(text=result_text)

    except:
        messagebox.showerror("Error", "Enter valid input format.")

# GUI Setup
root = tk.Tk()
root.title("Equivalence Relation Checker")
root.geometry("500x400")

tk.Label(root, text="Equivalence Relation Checker", font=("Arial", 16)).pack(pady=10)

tk.Label(root, text="Enter Set Elements (comma separated)").pack()
entry_set = tk.Entry(root, width=50)
entry_set.pack(pady=5)

tk.Label(root, text="Enter Relation Pairs (a,b;c,d;...)").pack()
entry_relation = tk.Entry(root, width=50)
entry_relation.pack(pady=5)

tk.Button(root, text="Check Relation", command=check_relation).pack(pady=20)

result_label = tk.Label(root, text="", font=("Arial", 12))
result_label.pack(pady=10)

root.mainloop()

import tkinter as tk
from tkinter import messagebox
import networkx as nx
import matplotlib.pyplot as plt

def check_partial_order():
    try:
        elements_input = entry_set.get()
        elements = set(e.strip() for e in elements_input.split(","))

        relation_input = entry_relation.get()
        pairs = relation_input.split(";")
        relation = set()

        for pair in pairs:
            a, b = pair.strip().split(",")
            relation.add((a.strip(), b.strip()))

        reflexive = True
        antisymmetric = True
        transitive = True

        # Reflexive Check
        for element in elements:
            if (element, element) not in relation:
                reflexive = False
                break

        # Antisymmetric Check
        for (a, b) in relation:
            if a != b and (b, a) in relation:
                antisymmetric = False
                break

        # Transitive Check
        for (a, b) in relation:
            for (c, d) in relation:
                if b == c and (a, d) not in relation:
                    transitive = False
                    break

        result_text = (
            f"Reflexive: {reflexive}\n"
            f"Antisymmetric: {antisymmetric}\n"
            f"Transitive: {transitive}\n\n"
        )

        if reflexive and antisymmetric and transitive:
            result_text += "The relation IS a Partial Order."
        else:
            result_text += "The relation is NOT a Partial Order."

        result_label.config(text=result_text)

        # Visualize Graph
        G = nx.DiGraph()
        G.add_nodes_from(elements)
        G.add_edges_from(relation)

        plt.figure()
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_size=2000)
        plt.title("Relation Graph Visualization")
        plt.show()

    except:
        messagebox.showerror("Error", "Invalid input format.")

# GUI Setup
root = tk.Tk()
root.title("Partial Order Relation Visualizer")
root.geometry("550x450")

tk.Label(root, text="Partial Order Relation Visualizer", font=("Arial", 16)).pack(pady=10)

tk.Label(root, text="Enter Set Elements (comma separated)").pack()
entry_set = tk.Entry(root, width=60)
entry_set.pack(pady=5)

tk.Label(root, text="Enter Relation Pairs (a,b;c,d;...)").pack()
entry_relation = tk.Entry(root, width=60)
entry_relation.pack(pady=5)

tk.Button(root, text="Check & Visualize", command=check_partial_order).pack(pady=20)

result_label = tk.Label(root, text="", font=("Arial", 12))
result_label.pack(pady=10)

root.mainloop()

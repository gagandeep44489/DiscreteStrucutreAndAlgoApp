import tkinter as tk
from tkinter import messagebox
import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations

class LatticeVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Lattice Visualizer")

        # Input for elements
        tk.Label(root, text="Enter Elements (comma separated):").pack()
        self.elements_entry = tk.Entry(root, width=50)
        self.elements_entry.pack()

        # Input for relations
        tk.Label(root, text="Enter Relations (a<=b format, comma separated):").pack()
        self.relations_entry = tk.Entry(root, width=50)
        self.relations_entry.pack()

        tk.Button(root, text="Visualize Lattice", command=self.visualize).pack(pady=10)

    def visualize(self):
        elements = self.elements_entry.get().split(",")
        relations = self.relations_entry.get().split(",")

        elements = [e.strip() for e in elements]
        relations = [r.strip() for r in relations]

        G = nx.DiGraph()

        for e in elements:
            G.add_node(e)

        for rel in relations:
            if "<=" in rel:
                a, b = rel.split("<=")
                G.add_edge(a.strip(), b.strip())

        try:
            pos = nx.spring_layout(G)
            nx.draw(G, pos, with_labels=True, node_color="lightblue",
                    node_size=2000, font_size=10, arrows=True)
            plt.title("Lattice Hasse Diagram")
            plt.show()

            self.check_lattice(G)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def check_lattice(self, G):
        minimal = [n for n in G.nodes if G.in_degree(n) == 0]
        maximal = [n for n in G.nodes if G.out_degree(n) == 0]

        msg = ""
        if len(minimal) == 1:
            msg += f"Least Element: {minimal[0]}\n"
        else:
            msg += "No unique least element\n"

        if len(maximal) == 1:
            msg += f"Greatest Element: {maximal[0]}"
        else:
            msg += "No unique greatest element"

        messagebox.showinfo("Lattice Check", msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = LatticeVisualizer(root)
    root.mainloop()
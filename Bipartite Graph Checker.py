import tkinter as tk
from tkinter import messagebox, simpledialog
import networkx as nx
import matplotlib.pyplot as plt


class BipartiteGraphChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("Bipartite Graph Checker App")
        
        self.graph = nx.Graph()
        
        tk.Button(root, text="Add Node", width=25, command=self.add_node).pack(pady=5)
        tk.Button(root, text="Add Edge", width=25, command=self.add_edge).pack(pady=5)
        tk.Button(root, text="Show Graph", width=25, command=self.show_graph).pack(pady=5)
        tk.Button(root, text="Check Bipartite", width=25, command=self.check_bipartite).pack(pady=5)
        tk.Button(root, text="Exit", width=25, command=root.quit).pack(pady=5)

    def add_node(self):
        node = simpledialog.askstring("Add Node", "Enter node name:")
        if node:
            self.graph.add_node(node)
            messagebox.showinfo("Success", f"Node '{node}' added!")

    def add_edge(self):
        u = simpledialog.askstring("Add Edge", "Enter first node:")
        v = simpledialog.askstring("Add Edge", "Enter second node:")
        
        if u and v:
            self.graph.add_edge(u, v)
            messagebox.showinfo("Success", f"Edge '{u} - {v}' added!")

    def show_graph(self):
        plt.figure(figsize=(6, 5))
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, with_labels=True, node_size=800, font_size=10)
        plt.title("Graph Visualization")
        plt.show()

    def check_bipartite(self):
        try:
            is_bip = nx.is_bipartite(self.graph)
            
            if is_bip:
                color_map = nx.bipartite.color(self.graph)
                set1 = [node for node in color_map if color_map[node] == 0]
                set2 = [node for node in color_map if color_map[node] == 1]

                messagebox.showinfo(
                    "Bipartite Result",
                    f"Graph is Bipartite!\n\nSet 1: {set1}\nSet 2: {set2}"
                )
            else:
                messagebox.showerror("Not Bipartite", "Graph is NOT bipartite!")
        except nx.NetworkXError:
            messagebox.showerror("Error", "Graph must be connected or have no isolated nodes!")


if __name__ == "__main__":
    root = tk.Tk()
    app = BipartiteGraphChecker(root)
    root.mainloop()

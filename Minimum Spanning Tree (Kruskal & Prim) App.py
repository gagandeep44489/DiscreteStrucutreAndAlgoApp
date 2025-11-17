import tkinter as tk
from tkinter import messagebox, ttk
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import heapq


# ----------------- Algorithms -------------------

class UnionFind:
    def __init__(self):
        self.parent = {}
        self.rank = {}

    def find(self, x):
        if self.parent.get(x, x) != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent.get(x, x)

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank.get(ra, 0) < self.rank.get(rb, 0):
            self.parent[ra] = rb
        elif self.rank.get(ra, 0) > self.rank.get(rb, 0):
            self.parent[rb] = ra
        else:
            self.parent[rb] = ra
            self.rank[ra] = self.rank.get(ra, 0) + 1
        return True


def kruskal(nodes, edges):
    uf = UnionFind()
    for n in nodes:
        uf.parent[n] = n
        uf.rank[n] = 0

    sorted_edges = sorted(edges, key=lambda e: e[2])
    mst = []
    total = 0

    for u, v, w in sorted_edges:
        if uf.union(u, v):
            mst.append((u, v, w))
            total += w

    return mst, total


def prim(nodes, edges, start=None):
    if not nodes:
        return [], 0

    graph = {n: [] for n in nodes}
    for u, v, w in edges:
        graph[u].append((w, v))
        graph[v].append((w, u))

    if start is None:
        start = next(iter(nodes))

    visited = set([start])
    heap = []
    for w, v in graph[start]:
        heapq.heappush(heap, (w, start, v))

    mst = []
    total = 0
    while heap and len(visited) < len(nodes):
        w, u, v = heapq.heappop(heap)
        if v in visited:
            continue

        visited.add(v)
        mst.append((u, v, w))
        total += w

        for w2, nbr in graph[v]:
            if nbr not in visited:
                heapq.heappush(heap, (w2, v, nbr))

    return mst, total


# ---------------- GUI App -------------------

class MSTApp:
    def __init__(self, root):
        self.root = root
        root.title("Minimum Spanning Tree (Kruskal & Prim) - Desktop App")
        root.geometry("900x650")

        self.nodes = set()
        self.edges = []

        # Input Frame
        frame = tk.Frame(root, pady=5)
        frame.pack()

        tk.Label(frame, text="Node U:").grid(row=0, column=0)
        self.u_entry = tk.Entry(frame, width=5)
        self.u_entry.grid(row=0, column=1)

        tk.Label(frame, text="Node V:").grid(row=0, column=2)
        self.v_entry = tk.Entry(frame, width=5)
        self.v_entry.grid(row=0, column=3)

        tk.Label(frame, text="Weight:").grid(row=0, column=4)
        self.w_entry = tk.Entry(frame, width=5)
        self.w_entry.grid(row=0, column=5)

        tk.Button(frame, text="Add Edge", command=self.add_edge).grid(row=0, column=6, padx=10)
        tk.Button(frame, text="Clear", command=self.clear_graph).grid(row=0, column=7, padx=10)

        # Buttons
        tk.Button(root, text="Run Kruskal", width=20, command=self.run_kruskal).pack(pady=5)
        tk.Button(root, text="Run Prim", width=20, command=self.run_prim).pack(pady=5)

        # Output Frame
        self.output_box = tk.Text(root, height=10, width=80, font=("Courier", 12))
        self.output_box.pack(pady=10)

        # Graph Canvas
        self.fig = plt.Figure(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack()

    # ---------------- Functions ----------------

    def add_edge(self):
        try:
            u = self.u_entry.get()
            v = self.v_entry.get()
            w = float(self.w_entry.get())

            if u == "" or v == "":
                messagebox.showerror("Error", "Node cannot be empty")
                return

            self.nodes.update([u, v])
            self.edges.append((u, v, w))

            self.output_box.insert(tk.END, f"Added edge: {u} - {v} (w={w})\n")
            self.draw_graph()

        except ValueError:
            messagebox.showerror("Error", "Weight must be a number")

    def clear_graph(self):
        self.nodes = set()
        self.edges = []
        self.output_box.delete("1.0", tk.END)
        self.fig.clear()
        self.canvas.draw()

    def run_kruskal(self):
        mst, total = kruskal(self.nodes, self.edges)
        self.display_result("Kruskal", mst, total)
        self.draw_graph(mst)

    def run_prim(self):
        mst, total = prim(self.nodes, self.edges)
        self.display_result("Prim", mst, total)
        self.draw_graph(mst)

    def display_result(self, algo, mst, total):
        self.output_box.insert(tk.END, f"\n--- {algo} MST ---\n")
        for u, v, w in mst:
            self.output_box.insert(tk.END, f"{u} - {v} | w={w}\n")
        self.output_box.insert(tk.END, f"Total Weight = {total}\n\n")

    def draw_graph(self, highlight_edges=None):
        self.fig.clear()
        G = nx.Graph()

        for u, v, w in self.edges:
            G.add_edge(u, v, weight=w)

        pos = nx.spring_layout(G, seed=42)
        ax = self.fig.add_subplot(111)

        nx.draw(G, pos, ax=ax, with_labels=True, node_size=700)
        labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, ax=ax)

        if highlight_edges:
            nx.draw_networkx_edges(
                G, pos,
                edgelist=[(u, v) for u, v, w in highlight_edges],
                width=3, edge_color="red",
                ax=ax
            )

        self.canvas.draw()


# ---------------- Run App -------------------

root = tk.Tk()
app = MSTApp(root)
root.mainloop()

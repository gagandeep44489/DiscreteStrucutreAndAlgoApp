#!/usr/bin/env python3
"""
Shortest Path Visualizer (Desktop) — Tkinter + networkx + matplotlib
Save as shortest_path_app.py and run: python shortest_path_app.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import heapq

# ---------------- Algorithms -----------------

def dijkstra(nodes, edges, source, target):
    """Return (path_list, total_weight) or (None, None) if no path."""
    if source not in nodes or target not in nodes:
        return None, None
    # build adjacency
    g = {n: [] for n in nodes}
    for u, v, w in edges:
        g[u].append((v, w))
        g[v].append((u, w))  # undirected

    dist = {n: float('inf') for n in nodes}
    prev = {n: None for n in nodes}
    dist[source] = 0
    heap = [(0, source)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        if u == target:
            break
        for v, w in g[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, v))

    if dist[target] == float('inf'):
        return None, None

    # reconstruct path
    path = []
    cur = target
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return path, dist[target]


def bfs_shortest_path(nodes, edges, source, target):
    """Unweighted shortest path via BFS. Returns (path, length) or (None, None)."""
    if source not in nodes or target not in nodes:
        return None, None
    g = {n: [] for n in nodes}
    for u, v, w in edges:
        g[u].append(v)
        g[v].append(u)
    from collections import deque
    q = deque([source])
    prev = {source: None}
    while q:
        u = q.popleft()
        if u == target:
            break
        for v in g[u]:
            if v not in prev:
                prev[v] = u
                q.append(v)
    if target not in prev:
        return None, None
    # reconstruct
    path = []
    cur = target
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    # length = number of edges
    return path, len(path) - 1


# ---------------- GUI App -----------------

class ShortestPathApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Shortest Path Visualizer — Dijkstra & BFS")
        self.geometry("1000x680")

        self.edges = []   # list of (u, v, w)
        self.nodes = set()

        self._build_ui()
        self._init_plot()

    def _build_ui(self):
        # Top input frame
        top = ttk.Frame(self, padding=8)
        top.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(top, text="Node U:").grid(row=0, column=0, padx=4, sticky=tk.W)
        self.ent_u = ttk.Entry(top, width=8)
        self.ent_u.grid(row=0, column=1, padx=4)

        ttk.Label(top, text="Node V:").grid(row=0, column=2, padx=4, sticky=tk.W)
        self.ent_v = ttk.Entry(top, width=8)
        self.ent_v.grid(row=0, column=3, padx=4)

        ttk.Label(top, text="Weight:").grid(row=0, column=4, padx=4, sticky=tk.W)
        self.ent_w = ttk.Entry(top, width=8)
        self.ent_w.grid(row=0, column=5, padx=4)

        ttk.Button(top, text="Add Edge", command=self.add_edge).grid(row=0, column=6, padx=6)
        ttk.Button(top, text="Delete Last", command=self.delete_last).grid(row=0, column=7, padx=6)
        ttk.Button(top, text="Clear", command=self.clear_graph).grid(row=0, column=8, padx=6)

        # Controls frame (algorithm + nodes)
        controls = ttk.Frame(self, padding=8)
        controls.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(controls, text="Source:").grid(row=0, column=0, padx=4, sticky=tk.W)
        self.src_var = tk.StringVar(value="")
        self.src_menu = ttk.OptionMenu(controls, self.src_var, "")
        self.src_menu.grid(row=0, column=1, padx=4)

        ttk.Label(controls, text="Target:").grid(row=0, column=2, padx=4, sticky=tk.W)
        self.tgt_var = tk.StringVar(value="")
        self.tgt_menu = ttk.OptionMenu(controls, self.tgt_var, "")
        self.tgt_menu.grid(row=0, column=3, padx=4)

        ttk.Label(controls, text="Algorithm:").grid(row=0, column=4, padx=8, sticky=tk.W)
        self.algo_var = tk.StringVar(value="Dijkstra")
        algo_menu = ttk.OptionMenu(controls, self.algo_var, "Dijkstra", "Dijkstra", "BFS")
        algo_menu.grid(row=0, column=5, padx=4)

        ttk.Button(controls, text="Find Shortest Path", command=self.find_shortest_path).grid(row=0, column=6, padx=8)

        # Left side: edges list + results
        left = ttk.Frame(self, padding=8)
        left.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(left, text="Edges (u — v | w):").pack(anchor=tk.W)
        self.lst_edges = tk.Listbox(left, width=28, height=18)
        self.lst_edges.pack(pady=4)
        self.lst_edges.bind("<Delete>", lambda e: self.delete_selected_edge())

        ttk.Button(left, text="Delete Selected Edge", command=self.delete_selected_edge).pack(pady=4)

        ttk.Label(left, text="Result:").pack(anchor=tk.W, pady=(10,0))
        self.txt_result = tk.Text(left, width=30, height=8)
        self.txt_result.pack(pady=4)

        # Right side: graph visualization
        right = ttk.Frame(self, padding=6)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(7,6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _init_plot(self):
        self.ax.clear()
        self.ax.set_title("Graph (empty)")
        self.ax.axis("off")
        self.canvas.draw()

    # ---------- Graph operations ----------
    def add_edge(self):
        u = self.ent_u.get().strip()
        v = self.ent_v.get().strip()
        w_str = self.ent_w.get().strip()

        if not u or not v or not w_str:
            messagebox.showwarning("Input error", "Please fill u, v and weight.")
            return
        if u == v:
            messagebox.showwarning("Invalid", "Self-loops not allowed.")
            return
        try:
            w = float(w_str)
        except ValueError:
            messagebox.showwarning("Input error", "Weight must be a number.")
            return

        # avoid duplicate undirected edge
        for a,b,_ in self.edges:
            if (a==u and b==v) or (a==v and b==u):
                messagebox.showwarning("Duplicate", "Edge already exists. Delete it first to change weight.")
                return

        self.edges.append((u, v, w))
        self.nodes.update([u, v])
        self.lst_edges.insert(tk.END, f"{u} — {v} | w={w}")
        self.ent_u.delete(0, tk.END); self.ent_v.delete(0, tk.END); self.ent_w.delete(0, tk.END)
        self._update_node_menus()
        self._draw_graph()

    def delete_selected_edge(self):
        sel = self.lst_edges.curselection()
        if not sel:
            return
        idx = sel[0]
        self.lst_edges.delete(idx)
        self.edges.pop(idx)
        self._recompute_nodes()
        self._update_node_menus()
        self._draw_graph()

    def delete_last(self):
        if not self.edges:
            return
        removed = self.edges.pop()
        self.lst_edges.delete(tk.END)
        self._recompute_nodes()
        self._update_node_menus()
        self._draw_graph()
        self.txt_result.insert(tk.END, f"Deleted edge: {removed[0]} — {removed[1]} | w={removed[2]}\n")

    def clear_graph(self):
        if not messagebox.askyesno("Clear", "Clear all edges and nodes?"):
            return
        self.edges.clear()
        self.nodes.clear()
        self.lst_edges.delete(0, tk.END)
        self.txt_result.delete("1.0", tk.END)
        self._update_node_menus()
        self._draw_graph()

    def _recompute_nodes(self):
        nodes = set()
        for u, v, _ in self.edges:
            nodes.add(u); nodes.add(v)
        self.nodes = nodes

    def _update_node_menus(self):
        # rebuild OptionMenu menus for source/target
        menu_src = self.src_menu["menu"]
        menu_tgt = self.tgt_menu["menu"]
        menu_src.delete(0, "end")
        menu_tgt.delete(0, "end")
        node_list = sorted(list(self.nodes))
        if not node_list:
            self.src_var.set("")
            self.tgt_var.set("")
            menu_src.add_command(label="", command=lambda: self.src_var.set(""))
            menu_tgt.add_command(label="", command=lambda: self.tgt_var.set(""))
            return
        # set default values if current not present
        if self.src_var.get() not in node_list:
            self.src_var.set(node_list[0])
        if self.tgt_var.get() not in node_list:
            self.tgt_var.set(node_list[-1])
        for n in node_list:
            menu_src.add_command(label=n, command=lambda v=n: self.src_var.set(v))
            menu_tgt.add_command(label=n, command=lambda v=n: self.tgt_var.set(v))

    # ---------- Drawing ----------
    def _draw_graph(self, highlight_path=None):
        self.ax.clear()
        G = nx.Graph()
        for n in self.nodes:
            G.add_node(n)
        for u, v, w in self.edges:
            G.add_edge(u, v, weight=w)

        if len(G.nodes) == 0:
            self.ax.set_title("Graph (empty)")
            self.ax.axis("off")
            self.canvas.draw()
            return

        pos = nx.spring_layout(G, seed=42)
        # draw nodes and edges
        nx.draw_networkx_nodes(G, pos, ax=self.ax, node_size=600)
        nx.draw_networkx_edges(G, pos, ax=self.ax, alpha=0.5)
        nx.draw_networkx_labels(G, pos, ax=self.ax)
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=self.ax)

        # highlight path if exists (path is list of nodes)
        if highlight_path:
            # build path edge list
            path_edges = []
            for i in range(len(highlight_path)-1):
                path_edges.append( (highlight_path[i], highlight_path[i+1]) )
            nx.draw_networkx_nodes(G, pos, nodelist=highlight_path, node_color='lightgreen', ax=self.ax, node_size=700)
            nx.draw_networkx_edges(G, pos, edgelist=path_edges, width=4.0, edge_color='red', ax=self.ax)

        self.ax.set_title("Graph — shortest path highlighted (if found)")
        self.ax.axis("off")
        self.canvas.draw()

    # ---------- Run algorithm ----------
    def find_shortest_path(self):
        src = self.src_var.get()
        tgt = self.tgt_var.get()
        algo = self.algo_var.get()

        self.txt_result.delete("1.0", tk.END)

        if not src or not tgt:
            messagebox.showwarning("Select nodes", "Please select Source and Target nodes.")
            return
        if src == tgt:
            messagebox.showinfo("Same node", "Source and Target are same. Shortest path is the node itself.")
            self._draw_graph(highlight_path=[src])
            self.txt_result.insert(tk.END, f"Path: [{src}]\nDistance: 0\n")
            return

        if algo == "Dijkstra":
            path, dist = dijkstra(self.nodes, self.edges, src, tgt)
            if path is None:
                self.txt_result.insert(tk.END, "No path found between selected nodes.\n")
                self._draw_graph()
                return
            self.txt_result.insert(tk.END, f"Algorithm: Dijkstra (weighted)\n")
            self.txt_result.insert(tk.END, f"Path: {' -> '.join(path)}\nTotal weight: {dist}\n")
            self._draw_graph(highlight_path=path)

        else:  # BFS (unweighted)
            path, length = bfs_shortest_path(self.nodes, self.edges, src, tgt)
            if path is None:
                self.txt_result.insert(tk.END, "No path found between selected nodes.\n")
                self._draw_graph()
                return
            self.txt_result.insert(tk.END, f"Algorithm: BFS (unweighted)\n")
            self.txt_result.insert(tk.END, f"Path: {' -> '.join(path)}\nEdges count: {length}\n")
            self._draw_graph(highlight_path=path)


# ---------------- Run -----------------
if __name__ == "__main__":
    app = ShortestPathApp()
    app.mainloop()

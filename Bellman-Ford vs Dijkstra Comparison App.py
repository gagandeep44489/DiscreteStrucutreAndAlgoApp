"""
Bellman-Ford vs Dijkstra Comparison App (Tkinter)
Save as: bf_vs_dijkstra.py
Run:      python bf_vs_dijkstra.py

Features:
 - Paste a list of weighted edges (one per line) like: A B 5
 - Choose a source node and run:
     * Dijkstra (fast, requires non-negative weights)
     * Bellman-Ford (handles negative weights, detects negative cycles)
 - Shows distances & predecessor trees for both algorithms side-by-side
 - Flags when Dijkstra's result is invalid due to negative edges
 - Optionally draw the graph (requires networkx & matplotlib)
 - Single-file, pure Python (Tkinter). Optional visualization dependencies:
     pip install networkx matplotlib
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import heapq
import time

# Optional visualization
HAS_VIS = True
try:
    import networkx as nx
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
except Exception:
    HAS_VIS = False

# -----------------------
# Graph utilities
# -----------------------
class Graph:
    def __init__(self):
        # adjacency: u -> list of (v, weight)
        self.adj = {}
        self.nodes_set = set()
        self.edges = []  # list of (u,v,w)

    def clear(self):
        self.adj = {}
        self.nodes_set = set()
        self.edges = []

    def add_edge(self, u, v, w, directed=False):
        self.nodes_set.add(u)
        self.nodes_set.add(v)
        if u not in self.adj:
            self.adj[u] = []
        self.adj[u].append((v, w))
        self.edges.append((u, v, w))
        if not directed:
            # add reverse
            if v not in self.adj:
                self.adj[v] = []
            self.adj[v].append((u, w))
            self.edges.append((v, u, w))  # duplicated for undirected convenience

    def nodes(self):
        return sorted(list(self.nodes_set))

    def parse_edges_text(self, text, directed=False):
        """
        Parse text containing edges. Each non-empty line should be:
           node1 node2 weight
        weight can be integer or float. Lines starting with # ignored.
        """
        self.clear()
        lines = text.strip().splitlines()
        for i, line in enumerate(lines, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 3:
                raise ValueError(f"Line {i}: expected 'u v w', got: {line}")
            u = parts[0]
            v = parts[1]
            try:
                w = float(parts[2])
            except ValueError:
                raise ValueError(f"Line {i}: weight must be number: {parts[2]}")
            self.add_edge(u, v, w, directed=directed)
        return True

    def has_negative_edge(self):
        for (_, _, w) in self.edges:
            if w < 0:
                return True
        return False

# -----------------------
# Algorithms
# -----------------------
def dijkstra(graph, source):
    """
    Standard Dijkstra. Returns (dist, prev, elapsed_time_seconds)
    dist: dict node -> distance (math.inf if unreachable)
    prev: dict node -> predecessor (or None)
    """
    start_time = time.perf_counter()
    dist = {node: math.inf for node in graph.nodes()}
    prev = {node: None for node in graph.nodes()}
    if source not in dist:
        return dist, prev, 0.0
    dist[source] = 0.0
    heap = [(0.0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in graph.adj.get(u, []):
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, v))
    elapsed = time.perf_counter() - start_time
    return dist, prev, elapsed

def bellman_ford(graph, source):
    """
    Bellman-Ford algorithm.
    Returns (dist, prev, negative_cycle_detected (bool), elapsed_time_seconds)
    dist: dict node -> distance (math.inf if unreachable)
    prev: dict node -> predecessor (or None)
    """
    start_time = time.perf_counter()
    nodes = graph.nodes()
    dist = {node: math.inf for node in nodes}
    prev = {node: None for node in nodes}
    if source not in dist:
        return dist, prev, False, 0.0
    dist[source] = 0.0
    n = len(nodes)
    # Relax edges n-1 times
    for i in range(n - 1):
        updated = False
        for u, v, w in graph.edges:
            if dist[u] != math.inf and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                prev[v] = u
                updated = True
        if not updated:
            break
    # Check for negative cycles
    negative_cycle = False
    for u, v, w in graph.edges:
        if dist[u] != math.inf and dist[u] + w < dist[v]:
            negative_cycle = True
            break
    elapsed = time.perf_counter() - start_time
    return dist, prev, negative_cycle, elapsed

def reconstruct_path(prev, target):
    if target not in prev:
        return None
    path = []
    cur = target
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return path

# -----------------------
# GUI
# -----------------------
class BFvsDijkstraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bellman-Ford vs Dijkstra Comparison")
        self.graph = Graph()
        self.directed = tk.BooleanVar(value=False)
        self._build_ui()

    def _build_ui(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.grid(sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Left: edges input
        left = ttk.Frame(frm)
        left.grid(row=0, column=0, sticky="nsew", padx=(0,10))
        left.columnconfigure(0, weight=1)

        ttk.Label(left, text="Edges (one per line: u v w)").grid(row=0, column=0, sticky="w")
        self.edges_txt = tk.Text(left, width=40, height=18)
        self.edges_txt.grid(row=1, column=0, sticky="nsew", pady=5)
        sample = ("# Example (directed or undirected depending on setting)\n"
                  "A B 4\n"
                  "A C 2\n"
                  "B C -3\n"
                  "B D 2\n"
                  "C D 4\n")
        self.edges_txt.insert("1.0", sample)

        btn_fr = ttk.Frame(left)
        btn_fr.grid(row=2, column=0, sticky="ew", pady=5)
        ttk.Button(btn_fr, text="Load from file", command=self.load_from_file).grid(row=0, column=0, padx=2)
        ttk.Button(btn_fr, text="Build Graph", command=self.build_graph).grid(row=0, column=1, padx=2)
        ttk.Button(btn_fr, text="Clear", command=self.clear_edges).grid(row=0, column=2, padx=2)
        ttk.Checkbutton(btn_fr, text="Directed graph", variable=self.directed).grid(row=0, column=3, padx=6)

        # Right: controls and results
        right = ttk.Frame(frm)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)

        # Source selection
        src_fr = ttk.Frame(right)
        src_fr.grid(row=0, column=0, sticky="ew")
        ttk.Label(src_fr, text="Source node:").grid(row=0, column=0, sticky="w")
        self.src_entry = ttk.Entry(src_fr, width=10)
        self.src_entry.grid(row=0, column=1, padx=(6,12))
        ttk.Button(src_fr, text="Run Algorithms", command=self.run_algorithms).grid(row=0, column=2)

        # Results panes
        results_label = ttk.Label(right, text="Results")
        results_label.grid(row=1, column=0, sticky="w", pady=(8,0))

        self.results_txt = tk.Text(right, width=60, height=18)
        self.results_txt.grid(row=2, column=0, sticky="nsew", pady=5)

        # Visualization
        vis_fr = ttk.Frame(frm)
        vis_fr.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(8,0))
        vis_fr.columnconfigure(0, weight=1)
        if HAS_VIS:
            self.fig = plt.Figure(figsize=(8,3))
            self.canvas = FigureCanvasTkAgg(self.fig, master=vis_fr)
            self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
            vis_btn = ttk.Button(vis_fr, text="Draw Graph", command=self.draw_graph)
            vis_btn.grid(row=1, column=0, sticky="e", pady=4)
        else:
            ttk.Label(vis_fr, text="(Graph visualization disabled — install networkx & matplotlib to enable.)", foreground="gray").grid(row=0, column=0, sticky="w")

        footer = ttk.Label(frm, text="Tip: Build Graph after editing edges. Dijkstra requires non-negative edges for correctness.", foreground="blue")
        footer.grid(row=3, column=0, columnspan=2, sticky="w", pady=(8,0))

    # -----------------------
    # UI callbacks
    # -----------------------
    def load_from_file(self):
        path = filedialog.askopenfilename(title="Open edges file", filetypes=[("Text files","*.txt"), ("All files","*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = f.read()
            self.edges_txt.delete("1.0", "end")
            self.edges_txt.insert("1.0", data)
            messagebox.showinfo("Loaded", f"Loaded edges from {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load file: {e}")

    def build_graph(self):
        txt = self.edges_txt.get("1.0", "end").strip()
        try:
            self.graph.parse_edges_text(txt, directed=self.directed.get())
            nodes = ", ".join(self.graph.nodes())
            self.results_txt.insert("end", f"Graph built. Nodes: {nodes}\n")
        except Exception as e:
            messagebox.showerror("Parse error", str(e))

    def clear_edges(self):
        self.edges_txt.delete("1.0", "end")
        self.graph.clear()
        self.results_txt.insert("end", "Cleared graph.\n")

    def run_algorithms(self):
        # ensure graph
        if not self.graph.nodes():
            try:
                self.build_graph()
            except Exception:
                messagebox.showerror("Graph missing", "Please build a graph first.")
                return
        source = self.src_entry.get().strip()
        if not source:
            messagebox.showerror("Input", "Enter a source node.")
            return
        # Run Dijkstra
        d_dist, d_prev, d_time = dijkstra(self.graph, source)
        # Run Bellman-Ford
        bf_dist, bf_prev, bf_neg_cycle, bf_time = bellman_ford(self.graph, source)

        self.results_txt.insert("end", "---- Algorithm Comparison ----\n")
        self.results_txt.insert("end", f"Source: {source}\n")
        self.results_txt.insert("end", f"Dijkstra time: {d_time:.6f} s    Bellman-Ford time: {bf_time:.6f} s\n")
        if self.graph.has_negative_edge():
            self.results_txt.insert("end", "Graph contains negative-weight edges. Dijkstra may be incorrect.\n")
        self.results_txt.insert("end", "\nNode\tDijkstra\t\tBellman-Ford\t\tPath (BF)\n")
        self.results_txt.insert("end", "-"*72 + "\n")
        for node in sorted(self.graph.nodes()):
            dval = d_dist.get(node, math.inf)
            bfval = bf_dist.get(node, math.inf)
            dstr = "∞" if dval == math.inf else f"{dval:.3f}"
            bfstr = "∞" if bfval == math.inf else f"{bfval:.3f}"
            # Reconstruct BF path for display
            path = reconstruct_path(bf_prev, node)
            pstr = "-" .join(path) if path else "—"
            self.results_txt.insert("end", f"{node}\t{dstr:<12}\t{bfstr:<12}\t{pstr}\n")
        if bf_neg_cycle:
            self.results_txt.insert("end", "\nBellman-Ford detected a NEGATIVE CYCLE — shortest paths may not be defined.\n")
        self.results_txt.insert("end", "------------------------------\n\n")
        # Scroll to end
        self.results_txt.see("end")

    def draw_graph(self):
        if not HAS_VIS:
            messagebox.showwarning("Missing packages", "Install networkx and matplotlib to draw graph.")
            return
        if not self.graph.nodes():
            messagebox.showinfo("Graph empty", "Build the graph first.")
            return
        G = nx.DiGraph() if self.directed.get() else nx.Graph()
        for u, v, w in self.graph.edges:
            # In undirected case edges list contains duplicates; add only once per unordered pair
            if not self.directed.get():
                if G.has_edge(u, v) or G.has_edge(v, u):
                    continue
            G.add_edge(u, v, weight=w)
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_title("Graph (edge weights shown)")
        pos = nx.spring_layout(G, seed=42)
        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=300)
        nx.draw_networkx_labels(G, pos, ax=ax)
        nx.draw_networkx_edges(G, pos, ax=ax, arrows=self.directed.get())
        edge_labels = {(u, v): f"{d['weight']}" for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax)
        ax.axis('off')
        self.canvas.draw()

# -----------------------
# Main
# -----------------------
def main():
    root = tk.Tk()
    app = BFvsDijkstraApp(root)
    root.geometry("1000x700")
    root.mainloop()

if __name__ == "__main__":
    main()

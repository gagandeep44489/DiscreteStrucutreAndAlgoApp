"""
Path Cost Comparator - single-file desktop app (Tkinter)

Features:
 - Paste a list of weighted edges (one per line) like: A B 5
 - Enter path(s) in format: A-B-C or A,B,C (both supported)
 - Click "Compare Paths" to compute total cost for each path and see which is cheaper
 - Optional: click "Shortest path (Dijkstra)" to compute shortest path between two nodes
 - Optional graph visualization if `networkx` and `matplotlib` are installed

Run:
    python path_cost_comparator.py

Dependencies (optional for visualization):
    pip install networkx matplotlib
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import heapq
import sys

# Try imports for optional visualization
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
        # adjacency: node -> list of (neighbor, weight)
        self.adj = {}

    def add_edge(self, u, v, w, directed=False):
        if u not in self.adj: self.adj[u] = []
        if v not in self.adj: self.adj[v] = []
        self.adj[u].append((v, w))
        if not directed:
            self.adj[v].append((u, w))

    def nodes(self):
        return list(self.adj.keys())

    def parse_edges_text(self, text):
        """
        Parse text containing edges. Each non-empty line should be:
           node1 node2 weight
        weight can be integer or float. Lines starting with # ignored.
        """
        self.adj = {}
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
            self.add_edge(u, v, w)
        return True

    def dijkstra(self, source):
        """
        Return (dist, prev) where dist[node] = shortest distance from source,
        prev[node] = predecessor on shortest path (or None).
        Uses a binary heap.
        """
        dist = {node: math.inf for node in self.adj}
        prev = {node: None for node in self.adj}
        if source not in self.adj:
            return dist, prev
        dist[source] = 0.0
        heap = [(0.0, source)]
        while heap:
            d, u = heapq.heappop(heap)
            if d > dist[u]:
                continue
            for v, w in self.adj.get(u, []):
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(heap, (nd, v))
        return dist, prev

    def path_cost(self, path_nodes):
        """
        Given list of nodes [A,B,C,...], compute the cost along edges A->B, B->C...
        Returns (cost, missing_edge) where missing_edge is None or (u,v) that wasn't present.
        """
        cost = 0.0
        for i in range(len(path_nodes)-1):
            u = path_nodes[i]
            v = path_nodes[i+1]
            found = False
            if u not in self.adj:
                return None, (u, v)
            for nb, w in self.adj[u]:
                if nb == v:
                    cost += w
                    found = True
                    break
            if not found:
                return None, (u, v)
        return cost, None

    def shortest_path(self, source, target):
        dist, prev = self.dijkstra(source)
        if dist.get(target, math.inf) == math.inf:
            return None, None  # no path
        # reconstruct path
        path = []
        cur = target
        while cur is not None:
            path.append(cur)
            cur = prev[cur]
        path.reverse()
        return path, dist[target]

# -----------------------
# GUI
# -----------------------
class PathComparatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Path Cost Comparator")
        self.graph = Graph()
        self._build_ui()

    def _build_ui(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.grid(sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Left: edge input
        left = ttk.Frame(frm)
        left.grid(row=0, column=0, sticky="nsew", padx=(0,10))
        left.columnconfigure(0, weight=1)

        ttk.Label(left, text="Edges (one per line: u v w)").grid(row=0, column=0, sticky="w")
        self.edges_txt = tk.Text(left, width=40, height=15)
        self.edges_txt.grid(row=1, column=0, sticky="nsew", pady=5)
        sample = ("# Example graph (undirected)\n"
                  "A B 5\n"
                  "B C 3\n"
                  "A C 10\n"
                  "C D 1\n"
                  "B D 8\n")
        self.edges_txt.insert("1.0", sample)

        btn_fr = ttk.Frame(left)
        btn_fr.grid(row=2, column=0, sticky="ew", pady=5)
        ttk.Button(btn_fr, text="Load from file", command=self.load_from_file).grid(row=0, column=0, padx=2)
        ttk.Button(btn_fr, text="Build Graph", command=self.build_graph).grid(row=0, column=1, padx=2)
        ttk.Button(btn_fr, text="Clear", command=self.clear_edges).grid(row=0, column=2, padx=2)

        # Right: paths and results
        right = ttk.Frame(frm)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)

        ttk.Label(right, text="Paths to compare (one per line). Use A-B-C or A,B,C").grid(row=0, column=0, sticky="w")
        self.paths_txt = tk.Text(right, width=40, height=8)
        self.paths_txt.grid(row=1, column=0, sticky="nsew", pady=5)
        self.paths_txt.insert("1.0", "A-B-C\nA-C\n")

        btn2 = ttk.Frame(right)
        btn2.grid(row=2, column=0, sticky="ew", pady=5)
        ttk.Button(btn2, text="Compare Paths", command=self.compare_paths).grid(row=0, column=0, padx=2)
        ttk.Button(btn2, text="Shortest path (Dijkstra)", command=self.shortest_path_dialog).grid(row=0, column=1, padx=2)

        ttk.Label(right, text="Results:").grid(row=3, column=0, sticky="w")
        self.results_txt = tk.Text(right, width=40, height=10, state="normal")
        self.results_txt.grid(row=4, column=0, sticky="nsew", pady=5)

        # Bottom: visualization if available
        vis_fr = ttk.Frame(frm)
        vis_fr.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(10,0))
        vis_fr.columnconfigure(0, weight=1)

        if HAS_VIS:
            self.fig = plt.Figure(figsize=(6,3))
            self.canvas = FigureCanvasTkAgg(self.fig, master=vis_fr)
            self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
            ttk.Button(vis_fr, text="Draw Graph", command=self.draw_graph).grid(row=1, column=0, sticky="e", pady=4)
        else:
            ttk.Label(vis_fr, text="(Graph visualization not available — install networkx & matplotlib to enable it.)", foreground="gray").grid(row=0, column=0, sticky="w")

        # Footer: instructions
        footer = ttk.Label(frm, text="Tip: Build Graph after editing edges. Paths can contain nodes separated by '-' or ','", foreground="blue")
        footer.grid(row=2, column=0, columnspan=2, sticky="w", pady=(8,0))

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
            self.graph.parse_edges_text(txt)
            self.results_txt.insert("end", "Graph built. Nodes: " + ", ".join(sorted(self.graph.nodes())) + "\n")
        except Exception as e:
            messagebox.showerror("Parse error", str(e))

    def clear_edges(self):
        self.edges_txt.delete("1.0", "end")
        self.graph = Graph()
        self.results_txt.insert("end", "Cleared graph.\n")

    def _parse_path_line(self, line):
        line = line.strip()
        if not line:
            return None
        if '-' in line:
            parts = [p.strip() for p in line.split('-') if p.strip()]
        elif ',' in line:
            parts = [p.strip() for p in line.split(',') if p.strip()]
        else:
            # single node or space-separated
            parts = [p.strip() for p in line.split() if p.strip()]
        return parts if len(parts) >= 1 else None

    def compare_paths(self):
        # Ensure graph exists
        if not self.graph.adj:
            try:
                self.build_graph()
            except Exception:
                messagebox.showerror("Graph missing", "Please build a graph first.")
                return

        lines = self.paths_txt.get("1.0", "end").splitlines()
        results = []
        for line in lines:
            pl = self._parse_path_line(line)
            if not pl:
                continue
            cost, missing = self.graph.path_cost(pl)
            if missing is not None:
                results.append((line.strip(), None, f"Missing edge {missing[0]} -> {missing[1]}"))
            else:
                results.append((line.strip(), cost, None))

        # display
        if not results:
            self.results_txt.insert("end", "No paths to compare.\n")
            return

        # find min among valid ones
        valid = [(r[0], r[1]) for r in results if r[1] is not None]
        self.results_txt.insert("end", "---- Comparison ----\n")
        if valid:
            min_cost = min(v[1] for v in valid)
            for r in results:
                path_label = r[0]
                cost = r[1]
                err = r[2]
                if err:
                    self.results_txt.insert("end", f"{path_label} : ERROR -> {err}\n")
                else:
                    mark = " <-- cheapest" if abs(cost - min_cost) < 1e-9 else ""
                    self.results_txt.insert("end", f"{path_label} : cost = {cost}{mark}\n")
        else:
            for r in results:
                self.results_txt.insert("end", f"{r[0]} : ERROR -> {r[2]}\n")

        self.results_txt.insert("end", "--------------------\n")

    def shortest_path_dialog(self):
        # simple dialog to request source and target then compute shortest path
        dlg = tk.Toplevel(self.root)
        dlg.title("Dijkstra shortest path")
        ttk.Label(dlg, text="Source node:").grid(row=0, column=0, padx=6, pady=6)
        src_ent = ttk.Entry(dlg)
        src_ent.grid(row=0, column=1, padx=6, pady=6)
        ttk.Label(dlg, text="Target node:").grid(row=1, column=0, padx=6, pady=6)
        tgt_ent = ttk.Entry(dlg)
        tgt_ent.grid(row=1, column=1, padx=6, pady=6)

        def compute():
            src = src_ent.get().strip()
            tgt = tgt_ent.get().strip()
            if not src or not tgt:
                messagebox.showerror("Input", "Enter both source and target")
                return
            if not self.graph.adj:
                try:
                    self.build_graph()
                except Exception:
                    messagebox.showerror("Graph missing", "Please build a graph first.")
                    return
            path, cost = self.graph.shortest_path(src, tgt)
            if path is None:
                self.results_txt.insert("end", f"No path from {src} to {tgt}\n")
            else:
                self.results_txt.insert("end", f"Shortest {src} -> {tgt}: {'-'.join(path)} (cost {cost})\n")
            dlg.destroy()

        ttk.Button(dlg, text="Compute", command=compute).grid(row=2, column=0, columnspan=2, pady=8)

    def draw_graph(self):
        if not HAS_VIS:
            messagebox.showwarning("Missing packages", "Install networkx and matplotlib to draw graph.")
            return
        if not self.graph.adj:
            messagebox.showinfo("Graph empty", "Build the graph first.")
            return

        G = nx.Graph()
        for u in self.graph.adj:
            for v, w in self.graph.adj[u]:
                # to avoid duplicate edges in undirected graph, only add if u<=v pair
                if G.has_edge(u, v):
                    continue
                G.add_edge(u, v, weight=w)
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_title("Graph (weights shown)")
        pos = nx.spring_layout(G, seed=42)
        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=400)
        nx.draw_networkx_labels(G, pos, ax=ax)
        nx.draw_networkx_edges(G, pos, ax=ax)
        # labels as weights
        edge_labels = {(u, v): f"{d['weight']}" for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax)
        ax.axis('off')
        self.canvas.draw()


# -----------------------
# Main
# -----------------------
def main():
    root = tk.Tk()
    app = PathComparatorApp(root)
    root.geometry("900x700")
    root.mainloop()

if __name__ == "__main__":
    main()

"""
Hamiltonian Cycle Detector — Tkinter Desktop App
Save as: hamiltonian_detector.py
Run: python hamiltonian_detector.py
Requires: Python 3.8+ (standard library only)

Features:
- Add edges (u, v) for undirected or directed graphs (selectable)
- Visualize graph on a simple circular layout
- Find a Hamiltonian cycle (visits every vertex once and returns to start)
- Option to search for one cycle or all cycles (careful: all cycles can be exponential)
- Load sample graphs and clear graph
- Results displayed in the log; found cycle is highlighted on the canvas
"""

import tkinter as tk
from tkinter import ttk, messagebox
from collections import defaultdict, deque
import math
import threading

class Graph:
    def __init__(self, directed=False):
        self.directed = directed
        self.adj = defaultdict(set)  # adjacency set for quick membership tests
        self.nodes_set = set()

    def add_edge(self, u, v):
        u = int(u); v = int(v)
        self.nodes_set.add(u); self.nodes_set.add(v)
        self.adj[u].add(v)
        if not self.directed:
            self.adj[v].add(u)

    def remove_edge(self, u, v):
        u = int(u); v = int(v)
        if v in self.adj.get(u, set()):
            self.adj[u].remove(v)
        if not self.directed and u in self.adj.get(v, set()):
            self.adj[v].remove(u)
        # prune isolated nodes
        for n in [u, v]:
            if not self.adj[n]:
                self.adj.pop(n, None)
                # keep nodes_set: we still consider nodes that were created

    def nodes(self):
        # include nodes that appear in adjacency or isolated nodes set
        s = set(self.nodes_set) | set(self.adj.keys())
        for u in list(self.adj.keys()):
            s.update(self.adj[u])
        return sorted(s)

    def clear(self):
        self.adj.clear()
        self.nodes_set.clear()

class HamiltonianFinder:
    def __init__(self, graph: Graph):
        self.graph = graph
        # results
        self.found_cycles = []
        self._stop = False

    def stop(self):
        self._stop = True

    def _is_neighbor(self, u, v):
        return v in self.graph.adj.get(u, set())

    def find_one_cycle(self):
        """Find one Hamiltonian cycle (if any). Returns list of vertices in order (closing to start)."""
        nodes = self.graph.nodes()
        if not nodes:
            return None, "Graph empty."
        n = len(nodes)
        # map node to index to have deterministic order
        nodes_sorted = nodes
        visited = set()

        def backtrack(path):
            if self._stop:
                return None
            if len(path) == n:
                # check return to start for cycle
                if self._is_neighbor(path[-1], path[0]):
                    return path + [path[0]]
                return None
            last = path[-1]
            # try neighbors in sorted order for determinism
            for nbr in sorted(self.graph.adj.get(last, [])):
                if nbr not in visited:
                    visited.add(nbr)
                    path.append(nbr)
                    res = backtrack(path)
                    if res:
                        return res
                    path.pop()
                    visited.remove(nbr)
            return None

        # Try starting at each node (often unnecessary for connected graphs)
        for start in nodes_sorted:
            visited.clear()
            visited.add(start)
            res = backtrack([start])
            if res:
                return res, "Hamiltonian cycle found."
            if self._stop:
                return None, "Search stopped."
        return None, "No Hamiltonian cycle exists."

    def find_all_cycles(self, limit=None):
        """Find all distinct Hamiltonian cycles (as vertex lists closed to start).
        Note: For undirected graphs cycles that are rotations/reversals are considered the same; we canonicalize."""
        self.found_cycles = []
        nodes = self.graph.nodes()
        if not nodes:
            return [], "Graph empty."
        n = len(nodes)
        nodes_sorted = nodes
        visited = set()
        cycles_set = set()
        limit_val = limit if (limit and isinstance(limit, int) and limit > 0) else None

        def canonical_cycle(cycle):
            # cycle is closed (last == first). return canonical tuple representation to dedupe
            cyc = cycle[:-1]  # remove duplicate last
            # generate rotations and reversed rotations and choose minimal tuple
            best = None
            L = len(cyc)
            for i in range(L):
                rot = tuple(cyc[i:] + cyc[:i])
                if best is None or rot < best:
                    best = rot
            # reversed
            rc = list(reversed(cyc))
            for i in range(L):
                rot = tuple(rc[i:] + rc[:i])
                if rot < best:
                    best = rot
            return best

        def backtrack(path):
            if self._stop:
                return
            if len(path) == n:
                if self._is_neighbor(path[-1], path[0]):
                    cycle = path + [path[0]]
                    canon = canonical_cycle(cycle)
                    if canon not in cycles_set:
                        cycles_set.add(canon)
                        self.found_cycles.append(list(canon) + [canon[0]])
                        # stop if reached limit
                        if limit_val and len(self.found_cycles) >= limit_val:
                            self._stop = True
                            return
                return
            last = path[-1]
            for nbr in sorted(self.graph.adj.get(last, [])):
                if nbr not in visited:
                    visited.add(nbr)
                    path.append(nbr)
                    backtrack(path)
                    path.pop()
                    visited.remove(nbr)
                    if self._stop:
                        return

        for start in nodes_sorted:
            visited.clear()
            visited.add(start)
            backtrack([start])
            if self._stop:
                break
        return self.found_cycles, f"Found {len(self.found_cycles)} cycle(s)." if self.found_cycles else "No Hamiltonian cycle exists."

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hamiltonian Cycle Detector")
        self.geometry("1000x650")
        self.graph = Graph(directed=False)
        self.finder = HamiltonianFinder(self.graph)
        self.node_positions = {}
        self.search_thread = None
        self._build_ui()

    def _build_ui(self):
        left = ttk.Frame(self, padding=8)
        left.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(left, text="Graph Type:").pack(anchor=tk.W)
        self.graph_type = tk.StringVar(value="Undirected")
        ttk.Radiobutton(left, text="Undirected", variable=self.graph_type, value="Undirected",
                        command=self.on_graph_type_change).pack(anchor=tk.W)
        ttk.Radiobutton(left, text="Directed", variable=self.graph_type, value="Directed",
                        command=self.on_graph_type_change).pack(anchor=tk.W)

        ttk.Separator(left, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=6)

        frm = ttk.Frame(left)
        frm.pack(anchor=tk.W, pady=4)
        ttk.Label(frm, text="u:").grid(row=0, column=0)
        self.e_u = ttk.Entry(frm, width=6); self.e_u.grid(row=0, column=1)
        ttk.Label(frm, text="v:").grid(row=0, column=2)
        self.e_v = ttk.Entry(frm, width=6); self.e_v.grid(row=0, column=3)
        ttk.Button(frm, text="Add Edge", command=self.add_edge).grid(row=0, column=4, padx=6)
        ttk.Button(frm, text="Remove Edge", command=self.remove_edge).grid(row=0, column=5, padx=6)

        ttk.Label(left, text="Edges:").pack(anchor=tk.W, pady=(8,0))
        self.edges_list = tk.Listbox(left, width=36, height=12)
        self.edges_list.pack()

        ttk.Button(left, text="Clear Graph", command=self.clear_graph).pack(pady=6)
        ttk.Button(left, text="Load sample (simple cycle)", command=self.load_sample_cycle).pack(pady=2)
        ttk.Button(left, text="Load sample (no cycle)", command=self.load_sample_no_cycle).pack(pady=2)
        ttk.Button(left, text="Load sample (directed cycle)", command=self.load_sample_directed).pack(pady=2)

        ttk.Separator(left, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=6)

        # options
        self.search_mode = tk.StringVar(value="One")
        ttk.Label(left, text="Search Mode:").pack(anchor=tk.W)
        ttk.Radiobutton(left, text="Find One Cycle", variable=self.search_mode, value="One").pack(anchor=tk.W)
        ttk.Radiobutton(left, text="Find All Cycles (limit)", variable=self.search_mode, value="All").pack(anchor=tk.W)
        self.limit_entry = ttk.Entry(left, width=8)
        self.limit_entry.insert(0, "10")
        ttk.Label(left, text="Limit (for All):").pack(anchor=tk.W)
        self.limit_entry.pack(anchor=tk.W)

        ttk.Button(left, text="Find Hamiltonian Cycle(s)", command=self.start_search).pack(pady=6)
        ttk.Button(left, text="Stop Search", command=self.stop_search).pack(pady=2)

        ttk.Separator(left, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=6)

        self.log = tk.Text(self, height=8)
        self.log.pack(side=tk.BOTTOM, fill=tk.X)

        right = ttk.Frame(self, padding=8)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(right, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def on_graph_type_change(self):
        t = self.graph_type.get()
        self.graph = Graph(directed=(t == "Directed"))
        self.finder = HamiltonianFinder(self.graph)
        self.edges_list.delete(0, tk.END)
        self.redraw()

    def add_edge(self):
        try:
            u = int(self.e_u.get()); v = int(self.e_v.get())
        except Exception:
            messagebox.showerror("Input error", "Please enter integer node ids for u and v.")
            return
        self.graph.add_edge(u, v)
        label = f"{u} -> {v}" if self.graph.directed else f"{u} -- {v}"
        self.edges_list.insert(tk.END, label)
        self.redraw()

    def remove_edge(self):
        try:
            u = int(self.e_u.get()); v = int(self.e_v.get())
        except Exception:
            messagebox.showerror("Input error", "Please enter integer node ids for u and v.")
            return
        self.graph.remove_edge(u, v)
        # refresh listbox
        self.edges_list.delete(0, tk.END)
        for u in sorted(self.graph.adj.keys()):
            for v in sorted(self.graph.adj[u]):
                label = f"{u} -> {v}" if self.graph.directed else f"{u} -- {v}"
                self.edges_list.insert(tk.END, label)
        self.redraw()

    def clear_graph(self):
        self.graph.clear()
        self.edges_list.delete(0, tk.END)
        self.log.delete(1.0, tk.END)
        self.redraw()

    def load_sample_cycle(self):
        self.graph = Graph(directed=False)
        self.edges_list.delete(0, tk.END)
        # simple 5-cycle
        edges = [(0,1),(1,2),(2,3),(3,4),(4,0)]
        for u,v in edges:
            self.graph.add_edge(u,v)
            self.edges_list.insert(tk.END, f"{u} -- {v}")
        self.finder = HamiltonianFinder(self.graph)
        self.redraw()

    def load_sample_no_cycle(self):
        self.graph = Graph(directed=False)
        self.edges_list.delete(0, tk.END)
        # a path-like graph that is not Hamiltonian
        edges = [(0,1),(1,2),(2,3)]
        for u,v in edges:
            self.graph.add_edge(u,v)
            self.edges_list.insert(tk.END, f"{u} -- {v}")
        self.finder = HamiltonianFinder(self.graph)
        self.redraw()

    def load_sample_directed(self):
        self.graph = Graph(directed=True)
        self.edges_list.delete(0, tk.END)
        # simple directed Hamiltonian cycle 0->1->2->0 and an extra node 3 isolated
        edges = [(0,1),(1,2),(2,0)]
        for u,v in edges:
            self.graph.add_edge(u,v)
            self.edges_list.insert(tk.END, f"{u} -> {v}")
        self.finder = HamiltonianFinder(self.graph)
        self.redraw()

    def start_search(self):
        if self.search_thread and self.search_thread.is_alive():
            messagebox.showinfo("Search running", "Search already running. Please stop it first.")
            return
        self.log.delete(1.0, tk.END)
        self.finder = HamiltonianFinder(self.graph)
        mode = self.search_mode.get()
        if mode == "One":
            self.search_thread = threading.Thread(target=self._search_one)
            self.search_thread.start()
        else:
            try:
                limit = int(self.limit_entry.get())
                if limit <= 0:
                    raise ValueError()
            except Exception:
                messagebox.showerror("Input error", "Please enter a positive integer for limit.")
                return
            self.search_thread = threading.Thread(target=self._search_all, args=(limit,))
            self.search_thread.start()

    def stop_search(self):
        if self.finder:
            self.finder.stop()
            self.log.insert(tk.END, "Stopping search...\n")

    def _search_one(self):
        self.log.insert(tk.END, "Searching for one Hamiltonian cycle...\n")
        cycle, msg = self.finder.find_one_cycle()
        if cycle:
            self.log.insert(tk.END, msg + "\n")
            self.log.insert(tk.END, "Cycle: " + " -> ".join(map(str, cycle)) + "\n")
            self.redraw(highlight_cycle=cycle)
        else:
            self.log.insert(tk.END, "Result: " + msg + "\n")
            self.redraw()

    def _search_all(self, limit):
        self.log.insert(tk.END, f"Searching for all Hamiltonian cycles (limit {limit})...\n")
        cycles, msg = self.finder.find_all_cycles(limit=limit)
        if cycles:
            self.log.insert(tk.END, msg + "\n")
            for i, cyc in enumerate(cycles, 1):
                self.log.insert(tk.END, f"{i}: " + " -> ".join(map(str, cyc)) + "\n")
            # highlight first found cycle
            self.redraw(highlight_cycle=cycles[0])
        else:
            self.log.insert(tk.END, "Result: " + msg + "\n")
            self.redraw()

    def redraw(self, highlight_cycle=None):
        self.canvas.delete('all')
        nodes = self.graph.nodes()
        if not nodes:
            return
        # circle layout
        w = self.canvas.winfo_width() or 800
        h = self.canvas.winfo_height() or 500
        cx, cy = w//2, h//2
        r = min(w, h)//2 - 90
        pos = {}
        n = len(nodes)
        for i, node in enumerate(nodes):
            ang = 2*math.pi*i/n
            x = cx + int(r*math.cos(ang))
            y = cy + int(r*math.sin(ang))
            pos[node] = (x, y)
            self.canvas.create_oval(x-20, y-20, x+20, y+20, fill='#f7f7f7', outline='#333')
            self.canvas.create_text(x, y, text=str(node), font=('Arial', 11, 'bold'))
        self.node_positions = pos

        # draw edges
        drawn = set()
        for u in sorted(self.graph.adj.keys()):
            for v in sorted(self.graph.adj[u]):
                if not self.graph.directed:
                    if (v, u) in drawn:
                        continue
                self._draw_edge(u, v, pos, highlight_cycle)
                drawn.add((u, v))

        # if highlight_cycle is provided, draw polyline
        if highlight_cycle and len(highlight_cycle) > 1:
            coords = []
            for node in highlight_cycle:
                if node in pos:
                    coords.append(pos[node])
            # draw connecting lines
            for i in range(len(coords)-1):
                x1, y1 = coords[i]; x2, y2 = coords[i+1]
                self.canvas.create_line(x1, y1, x2, y2, fill='red', width=3, arrow=tk.LAST if self.graph.directed else None)

    def _draw_edge(self, u, v, pos, highlight_cycle):
        if u not in pos or v not in pos:
            return
        x1, y1 = pos[u]; x2, y2 = pos[v]
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy)
        if d == 0:
            return
        ox = dx/d*22; oy = dy/d*22
        start = (x1 + ox, y1 + oy)
        end = (x2 - ox, y2 - oy)
        is_high = False
        if highlight_cycle:
            for a, b in zip(highlight_cycle, highlight_cycle[1:]):
                if a == u and b == v:
                    is_high = True
                    break
                if not self.graph.directed and a == v and b == u:
                    is_high = True
                    break
        color = 'red' if is_high else 'black'
        width = 3 if is_high else 1
        if self.graph.directed:
            self.canvas.create_line(start[0], start[1], end[0], end[1], arrow=tk.LAST, fill=color, width=width)
        else:
            self.canvas.create_line(start[0], start[1], end[0], end[1], fill=color, width=width)

if __name__ == '__main__':
    app = App()
    app.mainloop()

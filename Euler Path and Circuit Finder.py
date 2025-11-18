"""
Euler Path & Circuit Finder — Tkinter Desktop App
Save: euler_finder.py
Run: python euler_finder.py
Requires: Python 3.8+ (only standard library)
Features:
 - Add edges (u, v) with optional multiple edges
 - Choose Directed / Undirected graph mode
 - Find Euler Circuit or Euler Path if exists (Hierholzer's algorithm)
 - Visualize graph and highlight the found path
 - Load sample graphs and clear graph
"""

import tkinter as tk
from tkinter import ttk, messagebox
from collections import defaultdict, deque
import math

class Multigraph:
    """
    Supports multiedges. Stores edges with unique ids.
    For undirected graphs, edges are stored once but referenced from both endpoints.
    For directed graphs, edges are stored as (u->v).
    """
    def __init__(self, directed=False):
        self.directed = directed
        self.adj = defaultdict(list)   # node -> list of (neighbor, edge_id)
        self.edges = {}                # edge_id -> (u, v, used_flag)
        self.next_eid = 0

    def add_edge(self, u, v):
        u, v = int(u), int(v)
        eid = self.next_eid
        self.next_eid += 1
        self.edges[eid] = [u, v, False]
        self.adj[u].append((v, eid))
        if not self.directed:
            self.adj[v].append((u, eid))
        return eid

    def nodes(self):
        s = set(self.adj.keys())
        for eid,(u,v,_) in self.edges.items():
            s.add(u); s.add(v)
        return sorted(s)

    def clear(self):
        self.adj.clear()
        self.edges.clear()
        self.next_eid = 0

    def degree_info(self):
        if self.directed:
            indeg = defaultdict(int)
            outdeg = defaultdict(int)
            for eid,(u,v,_) in self.edges.items():
                outdeg[u] += 1
                indeg[v] += 1
            return indeg, outdeg
        else:
            deg = defaultdict(int)
            for eid,(u,v,_) in self.edges.items():
                deg[u] += 1
                deg[v] += 1
            return deg

    def copy_edge_usage(self):
        # reset used flag for algorithm (but keep data)
        for eid in self.edges:
            self.edges[eid][2] = False

class EulerFinder:
    @staticmethod
    def find_euler_undirected(graph: Multigraph):
        # Check connectivity of nodes with edges (ignore isolated vertices)
        nodes_with_edges = {u for eid,(u,v,_) in graph.edges.items() for u in (u,v)}
        if not nodes_with_edges:
            return None, "Graph has no edges."

        # degree counts
        deg = graph.degree_info()
        odd = [n for n in deg if deg[n] % 2 == 1]
        if len(odd) not in (0, 2):
            return None, f"No Euler path/circuit: {len(odd)} vertices have odd degree."

        # choose start: if odd exist -> one of them, else any vertex with edges
        if odd:
            start = odd[0]
        else:
            start = next(iter(nodes_with_edges))

        # Hierholzer's algorithm using edge usage flags
        graph.copy_edge_usage()
        stack = [start]
        path = []
        # adjacency iterators for efficiency
        adj_iter = {u: deque(graph.adj[u]) for u in graph.adj}

        while stack:
            v = stack[-1]
            # find unused edge from v
            while adj_iter.get(v):
                u, eid = adj_iter[v].popleft()
                if not graph.edges[eid][2]:
                    # mark used (for undirected mark once; representation stored once)
                    graph.edges[eid][2] = True
                    # determine neighbor (because stored u,v)
                    _, vv, _ = graph.edges[eid]
                    # push the neighbor
                    # for undirected graph, neighbor is u==v? careful:
                    if v == graph.edges[eid][0]:
                        neighbor = graph.edges[eid][1]
                    else:
                        neighbor = graph.edges[eid][0]
                    stack.append(neighbor)
                    break
            else:
                # no more unused edges from v
                path.append(stack.pop())

        # path contains vertices in reverse order of traversal
        path.reverse()

        # verify all edges used
        for eid in graph.edges:
            if not graph.edges[eid][2]:
                return None, "Graph is disconnected: some edges not reachable."

        # path is Euler trail/circuit vertices
        return path, "Euler path/circuit found."

    @staticmethod
    def find_euler_directed(graph: Multigraph):
        # For directed graphs: indeg == outdeg for every node -> circuit;
        # for path, exactly one vertex has outdeg = indeg +1 (start),
        # one has indeg = outdeg +1 (end), others equal.
        indeg, outdeg = graph.degree_info()
        nodes = set(indeg.keys()) | set(outdeg.keys())
        if not nodes:
            return None, "Graph has no edges."

        start_candidates = []
        end_candidates = []
        for n in nodes:
            in_d = indeg.get(n, 0)
            out_d = outdeg.get(n, 0)
            if out_d - in_d == 1:
                start_candidates.append(n)
            elif in_d - out_d == 1:
                end_candidates.append(n)
            elif in_d == out_d:
                continue
            else:
                return None, "Degree condition fails for directed Euler path/circuit."

        if not ((len(start_candidates) == len(end_candidates) == 0) or (len(start_candidates) == len(end_candidates) == 1)):
            return None, "Directed Euler path/circuit not possible (degree mismatch)."

        # choose start
        if start_candidates:
            start = start_candidates[0]
        else:
            # any vertex with outgoing edge
            start = next((n for n in nodes if outdeg.get(n,0) > 0), None)
            if start is None:
                return None, "Graph has no edges."

        # Hierholzer for directed: use adjacency deque, track used edges
        graph.copy_edge_usage()
        adj_iter = {u: deque([(v, eid) for (v, eid) in graph.adj[u]]) for u in graph.adj}
        stack = [start]
        path = []
        while stack:
            v = stack[-1]
            while adj_iter.get(v):
                u, eid = adj_iter[v].popleft()
                if not graph.edges[eid][2]:
                    graph.edges[eid][2] = True
                    # neighbor is u (since stored u->v)
                    _, vv, _ = graph.edges[eid]
                    # if stored as (src,dst), then neighbor = dst if v == src else ??? For directed it's straightforward:
                    neighbor = graph.edges[eid][1] if v == graph.edges[eid][0] else graph.edges[eid][1]
                    stack.append(neighbor)
                    break
            else:
                path.append(stack.pop())

        path.reverse()
        # verify all edges used
        for eid in graph.edges:
            if not graph.edges[eid][2]:
                return None, "Graph is disconnected: some edges not reachable."

        return path, "Directed Euler path/circuit found."

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Euler Path & Circuit Finder")
        self.geometry("1000x650")
        self.graph = Multigraph(directed=False)
        self.node_positions = {}
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

        ttk.Label(left, text="Edges:").pack(anchor=tk.W, pady=(8,0))
        self.edges_list = tk.Listbox(left, width=36, height=12)
        self.edges_list.pack()

        ttk.Button(left, text="Clear Graph", command=self.clear_graph).pack(pady=6)
        ttk.Button(left, text="Load sample (Euler circuit undirected)", command=self.load_sample_circuit).pack(pady=2)
        ttk.Button(left, text="Load sample (Euler path undirected)", command=self.load_sample_path).pack(pady=2)
        ttk.Button(left, text="Load sample (Directed)", command=self.load_sample_directed).pack(pady=2)

        ttk.Separator(left, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=6)
        ttk.Button(left, text="Find Euler Path/Circuit", command=self.find_euler).pack(pady=6)

        self.log = tk.Text(self, height=6)
        self.log.pack(side=tk.BOTTOM, fill=tk.X)

        right = ttk.Frame(self, padding=8)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(right, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def on_graph_type_change(self):
        t = self.graph_type.get()
        if t == "Directed":
            self.graph = Multigraph(directed=True)
        else:
            self.graph = Multigraph(directed=False)
        self.edges_list.delete(0, tk.END)
        self.redraw()

    def add_edge(self):
        try:
            u = int(self.e_u.get()); v = int(self.e_v.get())
        except Exception:
            messagebox.showerror("Input error", "Please enter integer node ids for u and v.")
            return
        eid = self.graph.add_edge(u, v)
        if self.graph.directed:
            self.edges_list.insert(tk.END, f"{u} -> {v} (id:{eid})")
        else:
            self.edges_list.insert(tk.END, f"{u} -- {v} (id:{eid})")
        self.redraw()

    def clear_graph(self):
        self.graph.clear()
        self.edges_list.delete(0, tk.END)
        self.log.delete(1.0, tk.END)
        self.redraw()

    def load_sample_circuit(self):
        # classic undirected Euler circuit (triangle + loop)
        self.graph = Multigraph(directed=False)
        self.edges_list.delete(0, tk.END)
        for u,v in [(0,1),(1,2),(2,0),(0,3),(3,0)]:
            eid = self.graph.add_edge(u,v)
            self.edges_list.insert(tk.END, f"{u} -- {v} (id:{eid})")
        self.redraw()

    def load_sample_path(self):
        # undirected Euler path (two odd-degree vertices)
        self.graph = Multigraph(directed=False)
        self.edges_list.delete(0, tk.END)
        for u,v in [(0,1),(1,2),(2,3),(3,1),(1,4)]:
            eid = self.graph.add_edge(u,v)
            self.edges_list.insert(tk.END, f"{u} -- {v} (id:{eid})")
        self.redraw()

    def load_sample_directed(self):
        # directed Euler path example
        self.graph = Multigraph(directed=True)
        self.edges_list.delete(0, tk.END)
        for u,v in [(0,1),(1,2),(2,0),(0,3),(3,4),(4,0)]:
            eid = self.graph.add_edge(u,v)
            self.edges_list.insert(tk.END, f"{u} -> {v} (id:{eid})")
        self.redraw()

    def find_euler(self):
        self.log.delete(1.0, tk.END)
        if self.graph.directed:
            path, msg = EulerFinder.find_euler_directed(self.graph)
        else:
            path, msg = EulerFinder.find_euler_undirected(self.graph)
        if path is None:
            self.log.insert(tk.END, "Result: " + msg + "\n")
            messagebox.showinfo("No Euler Path/Circuit", msg)
            self.redraw()
            return
        # path is a list of vertices in order
        self.log.insert(tk.END, msg + "\n")
        self.log.insert(tk.END, "Euler trail/circuit (vertices):\n")
        self.log.insert(tk.END, " -> ".join(map(str, path)) + "\n")
        # highlight the path on canvas
        self.redraw(highlight_path=path)

    def redraw(self, highlight_path=None):
        self.canvas.delete('all')
        nodes = self.graph.nodes()
        if not nodes:
            return
        # circle layout
        w = self.canvas.winfo_width() or 800
        h = self.canvas.winfo_height() or 500
        cx, cy = w//2, h//2
        r = min(w,h)//2 - 90
        pos = {}
        n = len(nodes)
        for i,node in enumerate(nodes):
            ang = 2*math.pi*i/n
            x = cx + int(r*math.cos(ang))
            y = cy + int(r*math.sin(ang))
            pos[node] = (x,y)
            self.canvas.create_oval(x-20,y-20,x+20,y+20, fill='#f7f7f7', outline='#333')
            self.canvas.create_text(x,y, text=str(node), font=('Arial', 11, 'bold'))
        self.node_positions = pos

        # draw edges
        for eid,(u,v,_) in self.graph.edges.items():
            if not self.graph.directed:
                self._draw_edge_undirected(u, v, eid, pos, highlight_path)
            else:
                self._draw_edge_directed(u, v, eid, pos, highlight_path)

        # if highlight_path provided, draw the connecting polyline on top
        if highlight_path and len(highlight_path) > 1:
            # create list of coordinates in order
            coords = []
            for node in highlight_path:
                if node in pos:
                    coords.append(pos[node])
            # draw lines connecting vertices
            for i in range(len(coords)-1):
                x1,y1 = coords[i]; x2,y2 = coords[i+1]
                self.canvas.create_line(x1,y1,x2,y2, fill='red', width=3, arrow=tk.LAST)

    def _draw_edge_undirected(self, u, v, eid, pos, highlight_path):
        if u not in pos or v not in pos: return
        x1,y1 = pos[u]; x2,y2 = pos[v]
        dx,dy = x2-x1, y2-y1
        d = math.hypot(dx,dy)
        if d == 0: return
        ox = dx/d*22; oy = dy/d*22
        start = (x1+ox, y1+oy); end = (x2-ox, y2-oy)
        # check if edge belongs to highlighted consecutive pair
        is_high = False
        if highlight_path:
            for a,b in zip(highlight_path, highlight_path[1:]):
                if (a==u and b==v) or (a==v and b==u):
                    is_high = True
                    break
        color = 'red' if is_high else 'black'
        width = 3 if is_high else 1
        self.canvas.create_line(start[0], start[1], end[0], end[1], fill=color, width=width)
        mx, my = (start[0]+end[0])/2, (start[1]+end[1])/2
        self.canvas.create_text(mx, my-12, text=f"id:{eid}", font=('Arial', 9))

    def _draw_edge_directed(self, u, v, eid, pos, highlight_path):
        if u not in pos or v not in pos: return
        x1,y1 = pos[u]; x2,y2 = pos[v]
        dx,dy = x2-x1, y2-y1
        d = math.hypot(dx,dy)
        if d == 0: return
        ox = dx/d*22; oy = dy/d*22
        start = (x1+ox, y1+oy); end = (x2-ox, y2-oy)
        is_high = False
        if highlight_path:
            for a,b in zip(highlight_path, highlight_path[1:]):
                if a==u and b==v:
                    is_high = True
                    break
        color = 'red' if is_high else 'black'
        width = 3 if is_high else 1
        self.canvas.create_line(start[0], start[1], end[0], end[1], arrow=tk.LAST, fill=color, width=width)
        mx, my = (start[0]+end[0])/2, (start[1]+end[1])/2
        self.canvas.create_text(mx, my-12, text=f"id:{eid}", font=('Arial', 9))

if __name__ == '__main__':
    app = App()
    app.mainloop()

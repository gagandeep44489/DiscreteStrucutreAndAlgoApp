"""
Ford-Fulkerson / Edmonds-Karp Simulator (Tkinter)
Save as: ford_fulkerson_sim.py
Run: python ford_fulkerson_sim.py
Requires: Python 3.8+ (no external packages)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque, defaultdict
import math

class FlowGraph:
    def __init__(self):
        # adjacency list: u -> {v: capacity}
        self.adj = defaultdict(dict)

    def add_edge(self, u, v, cap):
        if cap <= 0:
            raise ValueError("Capacity must be positive")
        # accumulate parallel edges
        self.adj[u][v] = self.adj[u].get(v, 0) + cap
        # ensure node exists
        if v not in self.adj:
            _ = self.adj[v]

    def nodes(self):
        s = set(self.adj.keys())
        for u in self.adj:
            s.update(self.adj[u].keys())
        return sorted(s)

    def build_residual(self):
        R = defaultdict(dict)
        for u in self.adj:
            for v, cap in self.adj[u].items():
                R[u][v] = cap
                if u not in R[v]:
                    R[v][u] = 0
        return R

    def edmonds_karp(self, source, sink):
        R = self.build_residual()
        max_flow = 0
        steps = []  # list of (path_edges, bottleneck, snapshot_residual)
        while True:
            parent = {}
            q = deque([source])
            parent[source] = None
            # BFS
            while q and sink not in parent:
                u = q.popleft()
                for v, cap in R[u].items():
                    if v not in parent and cap > 0:
                        parent[v] = u
                        q.append(v)
            if sink not in parent:
                break
            # reconstruct path and find bottleneck
            path = []
            v = sink
            bottleneck = math.inf
            while v != source:
                u = parent[v]
                path.append((u, v))
                bottleneck = min(bottleneck, R[u][v])
                v = u
            path.reverse()
            # apply flow
            for u, v in path:
                R[u][v] -= bottleneck
                R[v][u] = R.get(v, {}).get(u, 0) + bottleneck
            max_flow += bottleneck
            # copy minimal snapshot of residual for this step
            snapshot = {u: dict(R[u]) for u in R}
            steps.append((path, bottleneck, snapshot))
        return max_flow, steps


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ford-Fulkerson Simulator")
        self.geometry("1000x620")
        self.graph = FlowGraph()
        self.current_steps = []
        self.step_index = 0
        self._build_ui()

    def _build_ui(self):
        left = ttk.Frame(self, padding=8)
        left.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(left, text="Add edge (directed)").pack(anchor=tk.W)
        frm = ttk.Frame(left)
        frm.pack(anchor=tk.W, pady=4)
        ttk.Label(frm, text="u:").grid(row=0, column=0)
        self.e_u = ttk.Entry(frm, width=4); self.e_u.grid(row=0, column=1)
        ttk.Label(frm, text="v:").grid(row=0, column=2)
        self.e_v = ttk.Entry(frm, width=4); self.e_v.grid(row=0, column=3)
        ttk.Label(frm, text="cap:").grid(row=0, column=4)
        self.e_cap = ttk.Entry(frm, width=6); self.e_cap.grid(row=0, column=5)
        ttk.Button(frm, text="Add Edge", command=self.add_edge).grid(row=0, column=6, padx=6)

        ttk.Label(left, text="Edges:").pack(anchor=tk.W, pady=(8,0))
        self.edges_list = tk.Listbox(left, width=34, height=12)
        self.edges_list.pack()

        ttk.Button(left, text="Clear Graph", command=self.clear_graph).pack(pady=6)

        sep = ttk.Separator(left, orient=tk.HORIZONTAL); sep.pack(fill=tk.X, pady=6)

        ttk.Label(left, text="Source:").pack(anchor=tk.W)
        self.e_source = ttk.Entry(left, width=6); self.e_source.pack(anchor=tk.W)
        ttk.Label(left, text="Sink:").pack(anchor=tk.W)
        self.e_sink = ttk.Entry(left, width=6); self.e_sink.pack(anchor=tk.W)

        ttk.Button(left, text="Compute Max Flow", command=self.compute_flow).pack(pady=6)

        step_frm = ttk.Frame(left); step_frm.pack(pady=6)
        ttk.Button(step_frm, text="Prev Step", command=self.prev_step).grid(row=0, column=0)
        ttk.Button(step_frm, text="Next Step", command=self.next_step).grid(row=0, column=1)
        self.step_label = ttk.Label(step_frm, text="Step: 0/0"); self.step_label.grid(row=0, column=2, padx=6)

        ttk.Button(left, text="Load sample graph", command=self.load_sample).pack(pady=4)

        right = ttk.Frame(self, padding=8); right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(right, bg='white'); self.canvas.pack(fill=tk.BOTH, expand=True)

        self.log = tk.Text(self, height=6); self.log.pack(fill=tk.X)
        self.node_positions = {}

    def add_edge(self):
        try:
            u = int(self.e_u.get()); v = int(self.e_v.get()); cap = int(self.e_cap.get())
        except Exception:
            messagebox.showerror("Input error", "Please enter integer u, v, and capacity")
            return
        try:
            self.graph.add_edge(u, v, cap)
        except ValueError as e:
            messagebox.showerror("Value error", str(e)); return
        self.edges_list.insert(tk.END, f"{u} -> {v} : {cap}")
        self.draw_graph()

    def clear_graph(self):
        self.graph = FlowGraph()
        self.edges_list.delete(0, tk.END)
        self.current_steps = []
        self.step_index = 0
        self.canvas.delete('all')
        self.log.delete(1.0, tk.END)

    def load_sample(self):
        self.clear_graph()
        edges = [
            (0,1,16),(0,2,13),(1,2,10),(2,1,4),
            (1,3,12),(3,2,9),(2,4,14),(4,3,7),(3,5,20),(4,5,4)
        ]
        for u,v,c in edges:
            self.graph.add_edge(u,v,c)
            self.edges_list.insert(tk.END, f"{u} -> {v} : {c}")
        self.draw_graph()

    def compute_flow(self):
        try:
            source = int(self.e_source.get()); sink = int(self.e_sink.get())
        except Exception:
            messagebox.showerror("Input error", "Please enter integer source and sink nodes")
            return
        if source == sink:
            messagebox.showerror("Input error", "Source and sink must be different"); return
        max_flow, steps = self.graph.edmonds_karp(source, sink)
        self.log.delete(1.0, tk.END)
        self.log.insert(tk.END, f"Max flow: {max_flow}\n")
        for i,(path,flow,res) in enumerate(steps,1):
            self.log.insert(tk.END, f"Step {i}: path={path} flow={flow}\n")
        self.current_steps = steps
        self.step_index = 0
        self.update_step_label()
        if steps:
            self.show_step(0)
        else:
            self.draw_graph()

    def prev_step(self):
        if not self.current_steps: return
        if self.step_index > 0:
            self.step_index -= 1
            self.show_step(self.step_index)
            self.update_step_label()

    def next_step(self):
        if not self.current_steps: return
        if self.step_index < len(self.current_steps)-1:
            self.step_index += 1
            self.show_step(self.step_index)
            self.update_step_label()

    def update_step_label(self):
        total = len(self.current_steps)
        self.step_label.config(text=f"Step: {self.step_index+1}/{total}" if total else "Step: 0/0")

    def show_step(self, idx):
        path,flow,res = self.current_steps[idx]
        self.draw_graph(residual=res, highlight_path=path)

    def draw_graph(self, residual=None, highlight_path=None):
        self.canvas.delete('all')
        nodes = self.graph.nodes()
        if not nodes: return
        w = self.canvas.winfo_width() or 800
        h = self.canvas.winfo_height() or 500
        cx, cy = w//2, h//2
        r = min(w,h)//2 - 90
        n = len(nodes)
        pos = {}
        for i,node in enumerate(nodes):
            ang = 2*math.pi*i/n
            x = cx + int(r*math.cos(ang))
            y = cy + int(r*math.sin(ang))
            pos[node] = (x,y)
            self.canvas.create_oval(x-18,y-18,x+18,y+18, fill='#f7f7f7', outline='#000')
            self.canvas.create_text(x,y, text=str(node))
        self.node_positions = pos

        if residual is None:
            for u in self.graph.adj:
                for v,cap in self.graph.adj[u].items():
                    self._draw_edge(u,v,cap,pos,highlight_path, residual_mode=False)
        else:
            for u in residual:
                for v,cap in residual[u].items():
                    if cap > 0:
                        self._draw_edge(u,v,cap,pos,highlight_path, residual_mode=True)

    def _draw_edge(self, u, v, cap, pos, highlight_path, residual_mode=False):
        if u not in pos or v not in pos: return
        x1,y1 = pos[u]; x2,y2 = pos[v]
        dx,dy = x2-x1, y2-y1
        d = math.hypot(dx,dy)
        if d == 0: return
        ox = dx/d*22; oy = dy/d*22
        start = (x1+ox, y1+oy); end = (x2-ox, y2-oy)
        color = 'black'; width = 2
        if highlight_path and (u,v) in highlight_path:
            color = 'red'; width = 3
        if residual_mode:
            dash = (4,4)
            self.canvas.create_line(start[0], start[1], end[0], end[1], arrow=tk.LAST, dash=dash, width=width)
            mx, my = (start[0]+end[0])/2, (start[1]+end[1])/2
            self.canvas.create_text(mx, my-10, text=str(cap), font=('Arial', 10))
        else:
            self.canvas.create_line(start[0], start[1], end[0], end[1], arrow=tk.LAST, fill=color, width=width)
            mx, my = (start[0]+end[0])/2, (start[1]+end[1])/2
            self.canvas.create_text(mx, my-10, text=str(cap), font=('Arial', 10))

if __name__ == '__main__':
    app = App()
    app.mainloop()

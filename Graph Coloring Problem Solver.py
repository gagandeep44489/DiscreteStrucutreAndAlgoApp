#!/usr/bin/env python3
"""
Graph Coloring Problem Solver - Desktop app (Tkinter)

Features:
- Enter graph as edges (one per line) like "0 1" or "A B"
- Optionally enter number of colors (k). If left blank, app will search for minimum k.
- Solve using backtracking (exact) with simple heuristics (degree ordering).
- Visualize result with networkx + matplotlib inside a Tk window.
- Export result (coloring) to clipboard / copyable text.

Author: Generated for user (example)
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import networkx as nx
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import threading
import queue

# ---------- Graph parsing helpers ----------
def parse_edges(text):
    """
    Parse edges from multiline text. Each line: "u v"
    Node labels can be strings; returned graph uses nodes as strings.
    """
    G = nx.Graph()
    for ln in text.strip().splitlines():
        ln = ln.strip()
        if not ln:
            continue
        parts = ln.split()
        if len(parts) < 2:
            # ignore single node lines but add node
            G.add_node(parts[0])
            continue
        u, v = parts[0], parts[1]
        G.add_edge(u, v)
    return G

# ---------- Coloring solver ----------
def order_nodes_by_degree(G):
    return sorted(G.nodes(), key=lambda n: G.degree(n), reverse=True)

def can_color_with_k(G, k, node_order=None, time_limit=None):
    """
    Backtracking exact solver. Returns (True, coloring) if coloring found, else (False, None).
    node_order optional: list of nodes to consider in order.
    """
    if node_order is None:
        node_order = order_nodes_by_degree(G)
    n = len(node_order)
    coloring = {}
    adjacency = {n: set(G[n]) for n in G.nodes()}

    def backtrack(idx):
        if idx == n:
            return True
        node = node_order[idx]
        used = {coloring[nb] for nb in adjacency[node] if nb in coloring}
        for color in range(k):
            if color in used:
                continue
            coloring[node] = color
            if backtrack(idx + 1):
                return True
            del coloring[node]
        return False

    ok = backtrack(0)
    return ok, (coloring if ok else None)

def find_chromatic_number(G, max_k=None):
    """
    Try increasing k from 1..max_k (or n) until a coloring is found.
    Returns (k, coloring).
    """
    n = G.number_of_nodes()
    max_try = max_k or n
    node_order = order_nodes_by_degree(G)
    for k in range(1, max_try + 1):
        ok, coloring = can_color_with_k(G, k, node_order)
        if ok:
            return k, coloring
    return None, None

# ---------- UI ----------
class GraphColoringApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Coloring Problem Solver")
        self._build_ui()
        self.solve_thread = None
        self.result_queue = queue.Queue()

    def _build_ui(self):
        frm = ttk.Frame(self.root, padding=8)
        frm.pack(fill=tk.BOTH, expand=True)

        # Input area
        input_label = ttk.Label(frm, text="Enter edges (one per line):  u v")
        input_label.pack(anchor=tk.W)
        self.input_text = scrolledtext.ScrolledText(frm, width=40, height=10)
        self.input_text.pack(fill=tk.X)
        sample = "0 1\n0 2\n1 2\n1 3\n2 3\n3 4"
        self.input_text.insert("1.0", sample)

        options = ttk.Frame(frm)
        options.pack(fill=tk.X, pady=6)

        ttk.Label(options, text="Number of colors (k):").grid(row=0, column=0, sticky=tk.W)
        self.k_var = tk.StringVar()
        self.k_entry = ttk.Entry(options, textvariable=self.k_var, width=6)
        self.k_entry.grid(row=0, column=1, sticky=tk.W, padx=(4, 20))

        self.find_min_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options, text="Search for minimum k", variable=self.find_min_var).grid(row=0, column=2, sticky=tk.W)

        ttk.Button(options, text="Load from file", command=self.load_file).grid(row=0, column=3, padx=6)
        ttk.Button(options, text="Solve", command=self.on_solve).grid(row=0, column=4, padx=6)

        # Result and visualization area
        bottom = ttk.Frame(frm)
        bottom.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(bottom)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(left, text="Result / Coloring:").pack(anchor=tk.W)
        self.result_text = scrolledtext.ScrolledText(left, width=30, height=12)
        self.result_text.pack(fill=tk.BOTH, expand=True)

        ttk.Button(left, text="Copy result", command=self.copy_result).pack(pady=4)

        right = ttk.Frame(bottom)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        ttk.Label(right, text="Graph visualization:").pack(anchor=tk.W)
        self.fig, self.ax = plt.subplots(figsize=(5,4))
        self.fig.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        # status
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W).pack(fill=tk.X, side=tk.BOTTOM)

        # poll queue
        self.root.after(200, self._poll_queue)

    def load_file(self):
        path = filedialog.askopenfilename(title="Open edge list", filetypes=[("Text files","*.txt"), ("All files","*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert("1.0", text)
        except Exception as e:
            messagebox.showerror("Load error", str(e))

    def on_solve(self):
        txt = self.input_text.get("1.0", tk.END).strip()
        if not txt:
            messagebox.showwarning("Input missing", "Please enter edges in the input area.")
            return
        try:
            G = parse_edges(txt)
            if G.number_of_nodes() == 0:
                messagebox.showwarning("Empty graph", "No nodes found.")
                return
        except Exception as e:
            messagebox.showerror("Parse error", str(e))
            return

        k_input = self.k_var.get().strip()
        k_given = None
        if k_input != "":
            try:
                k_given = int(k_input)
                if k_given < 1:
                    raise ValueError("k must be >= 1")
            except Exception as e:
                messagebox.showerror("Invalid k", f"Invalid number of colors: {e}")
                return

        search_min = self.find_min_var.get()
        # run solver in background thread to avoid freezing UI
        self.status_var.set("Solving...")
        self.result_text.delete("1.0", tk.END)
        self.ax.clear()
        self.canvas.draw()
        self.solve_thread = threading.Thread(target=self._solve_worker, args=(G, k_given, search_min), daemon=True)
        self.solve_thread.start()

    def _solve_worker(self, G, k_given, search_min):
        try:
            if search_min:
                k, coloring = find_chromatic_number(G, max_k=None)
                if k is None:
                    self.result_queue.put(("done", "No coloring found (unexpected).", G, None, None))
                else:
                    self.result_queue.put(("done", f"Found chromatic number k = {k}", G, k, coloring))
            else:
                if k_given is None:
                    # if user didn't give and search_min is off -> default greedy with min colors found by greedy
                    coloring = nx.coloring.greedy_color(G, strategy="largest_first")
                    used = set(coloring.values())
                    k = max(used) + 1 if used else 0
                    self.result_queue.put(("done", f"Greedy coloring used k = {k}", G, k, coloring))
                else:
                    ok, coloring = can_color_with_k(G, k_given)
                    if ok:
                        self.result_queue.put(("done", f"Found a {k_given}-coloring.", G, k_given, coloring))
                    else:
                        self.result_queue.put(("done", f"No {k_given}-coloring exists (tried exact search).", G, k_given, None))
        except Exception as e:
            self.result_queue.put(("error", str(e), None, None, None))

    def _poll_queue(self):
        try:
            while True:
                item = self.result_queue.get_nowait()
                tag = item[0]
                if tag == "done":
                    msg, G, k, coloring = item[1], item[2], item[3], item[4]
                    # Note: ordering in put differs above; handle both shapes
                    # Determine real payload:
                    if isinstance(G, nx.Graph):
                        graph = G
                        k_val = k
                        coloring_map = coloring
                        msg_text = msg
                    else:
                        # fallback if different ordering
                        msg_text = item[1]
                        graph = item[2]
                        k_val = item[3]
                        coloring_map = item[4]
                    if coloring_map is None:
                        self.result_text.insert(tk.END, f"{msg_text}\n")
                        self.status_var.set("Done (no coloring).")
                        # still draw graph uncolored
                        self._draw_graph(graph, {})
                    else:
                        self.status_var.set("Done")
                        self.result_text.insert(tk.END, f"{msg_text}\n\nColoring (node: color):\n")
                        for node, c in sorted(coloring_map.items(), key=lambda x: str(x[0])):
                            self.result_text.insert(tk.END, f"{node}: {c}\n")
                        # draw
                        self._draw_graph(graph, coloring_map)
                elif tag == "error":
                    msg = item[1]
                    messagebox.showerror("Solver error", msg)
                    self.status_var.set("Error")
        except queue.Empty:
            pass
        self.root.after(200, self._poll_queue)

    def _draw_graph(self, G, coloring):
        self.ax.clear()
        pos = nx.spring_layout(G, seed=42)
        # generate color map
        if coloring:
            colors = []
            # normalize integer colors to indices and map to matplotlib colormap
            unique = sorted(set(coloring.values()))
            index_of = {v:i for i,v in enumerate(unique)}
            cmap = plt.get_cmap('tab10')
            for n in G.nodes():
                if n in coloring:
                    colors.append(cmap(index_of[coloring[n]] % 10))
                else:
                    colors.append('#cccccc')
        else:
            colors = '#88ccee'
        nx.draw_networkx(G, pos=pos, ax=self.ax, node_color=colors, with_labels=True, node_size=650, font_size=9)
        self.ax.set_axis_off()
        self.canvas.draw()

    def copy_result(self):
        txt = self.result_text.get("1.0", tk.END).strip()
        if not txt:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(txt)
        messagebox.showinfo("Copied", "Result copied to clipboard.")

def main():
    root = tk.Tk()
    app = GraphColoringApp(root)
    root.geometry("1000x650")
    root.mainloop()

if __name__ == "__main__":
    main()

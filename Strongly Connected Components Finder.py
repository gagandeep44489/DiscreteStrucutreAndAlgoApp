# scc_finder.py
# Strongly Connected Components Finder - Desktop app using Tkinter
# - Built-in Tarjan's algorithm (no external libs required)
# - Optional graph visualization if networkx & matplotlib are installed

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from collections import defaultdict

# Try to import visualization libs; if missing, visualization button will warn.
try:
    import networkx as nx
    import matplotlib.pyplot as plt
    VIS_AVAILABLE = True
except Exception:
    VIS_AVAILABLE = False

# ---------- Tarjan's algorithm (pure Python) ----------
def tarjan_scc(graph):
    """
    graph: dict mapping node -> iterable of neighbors
    returns list of SCCs (each SCC is a list of nodes)
    """
    index = 0
    index_map = {}
    lowlink = {}
    stack = []
    onstack = set()
    sccs = []

    def strongconnect(v):
        nonlocal index
        index_map[v] = index
        lowlink[v] = index
        index += 1
        stack.append(v)
        onstack.add(v)

        for w in graph.get(v, []):
            if w not in index_map:
                strongconnect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif w in onstack:
                lowlink[v] = min(lowlink[v], index_map[w])

        # If v is a root node, pop the stack and generate an SCC
        if lowlink[v] == index_map[v]:
            scc = []
            while True:
                w = stack.pop()
                onstack.remove(w)
                scc.append(w)
                if w == v:
                    break
            sccs.append(scc)

    # Ensure we process all nodes (including isolated)
    for v in list(graph.keys()):
        if v not in index_map:
            strongconnect(v)

    return sccs

# ---------- Utility: parse input ----------
def parse_edges(text):
    """
    Accepts text with one edge per line as: u v
    Nodes allowed to be strings (no spaces).
    Returns a set of nodes and adjacency dict.
    """
    edges = []
    nodes = set()
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    for i, line in enumerate(lines, start=1):
        parts = line.split()
        if len(parts) < 2:
            raise ValueError(f"Line {i}: expected 'u v' but got: '{line}'")
        u = parts[0]
        v = parts[1]
        nodes.add(u); nodes.add(v)
        edges.append((u, v))
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
    # include isolated nodes that might never appear as 'u'
    for n in nodes:
        if n not in graph:
            graph[n] = []
    return graph

# ---------- Optional visualization ----------
def visualize_graph(graph, sccs):
    if not VIS_AVAILABLE:
        messagebox.showinfo("Visualization unavailable",
                            "Visualization requires networkx and matplotlib.\nRun:\n\npip install networkx matplotlib")
        return

    G = nx.DiGraph()
    for u, nbrs in graph.items():
        for v in nbrs:
            G.add_edge(u, v)
    # Ensure isolated nodes are present
    for n in graph.keys():
        if n not in G:
            G.add_node(n)

    # Map node -> scc index for coloring
    node_to_scc = {}
    for idx, scc in enumerate(sccs):
        for node in scc:
            node_to_scc[node] = idx

    # Create a color map where nodes in same SCC have same color
    import math
    colors = []
    for node in G.nodes():
        idx = node_to_scc.get(node, -1)
        # Use a repeating palette by mapping idx to hsv-ish value
        if idx == -1:
            colors.append('lightgray')
        else:
            # simple deterministic color assignment
            hue = (idx * 0.618033988749895) % 1.0  # golden ratio fractional
            # convert hue to an RGB via matplotlib's colormap
            cmap = plt.cm.get_cmap('tab20')
            colors.append(cmap(int(hue * 19)))

    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(G, seed=42)
    nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=12, width=1)
    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=700)
    nx.draw_networkx_labels(G, pos, font_size=9)
    plt.title("Directed Graph — nodes colored by SCC")
    plt.axis('off')
    plt.tight_layout()
    plt.show()

# ---------- Tkinter UI ----------
class SCCFinderApp:
    def __init__(self, root):
        self.root = root
        root.title("Strongly Connected Components Finder")
        root.geometry("900x520")

        mainframe = ttk.Frame(root, padding="8 8 8 8")
        mainframe.pack(fill=tk.BOTH, expand=True)

        # Input frame
        input_frame = ttk.LabelFrame(mainframe, text="Graph Input (one edge per line: u v)")
        input_frame.place(relx=0.01, rely=0.01, relwidth=0.48, relheight=0.78)

        self.input_text = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD)
        self.input_text.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # Default example
        example = ("# Example graph: a cycle 0->1->2->0, and another cycle 3->4->5->3\n"
                   "0 1\n1 2\n2 0\n2 3\n3 4\n4 5\n5 3\n6 7\n")
        self.input_text.insert('1.0', example)

        # Output frame
        output_frame = ttk.LabelFrame(mainframe, text="SCCs (results)")
        output_frame.place(relx=0.50, rely=0.01, relwidth=0.49, relheight=0.78)

        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, state='disabled')
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # Buttons
        btn_frame = ttk.Frame(mainframe)
        btn_frame.place(relx=0.01, rely=0.80, relwidth=0.98, relheight=0.18)

        self.find_btn = ttk.Button(btn_frame, text="Find SCCs", command=self.find_sccs)
        self.find_btn.place(relx=0.01, rely=0.05, relwidth=0.24, relheight=0.3)

        self.visualize_btn = ttk.Button(btn_frame, text="Visualize Graph", command=self.visualize)
        self.visualize_btn.place(relx=0.27, rely=0.05, relwidth=0.24, relheight=0.3)

        self.clear_input_btn = ttk.Button(btn_frame, text="Clear Input", command=lambda: self.input_text.delete('1.0', tk.END))
        self.clear_input_btn.place(relx=0.54, rely=0.05, relwidth=0.22, relheight=0.3)

        self.clear_output_btn = ttk.Button(btn_frame, text="Clear Output", command=lambda: self._set_output(''))
        self.clear_output_btn.place(relx=0.78, rely=0.05, relwidth=0.20, relheight=0.3)

        # Options: sort output?
        self.sort_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(btn_frame, text="Sort SCCs by size (desc)", variable=self.sort_var).place(relx=0.01, rely=0.5)

        # Status bar
        self.status = tk.StringVar()
        self.status.set("Ready")
        ttk.Label(mainframe, textvariable=self.status, relief=tk.SUNKEN, anchor='w').place(relx=0.01, rely=0.96, relwidth=0.98)

    def _set_output(self, text):
        self.output_text.configure(state='normal')
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert('1.0', text)
        self.output_text.configure(state='disabled')

    def find_sccs(self):
        txt = self.input_text.get('1.0', tk.END)
        try:
            graph = parse_edges(txt)
        except Exception as e:
            messagebox.showerror("Parse Error", str(e))
            return

        self.status.set("Computing SCCs...")
        self.root.update_idletasks()

        sccs = tarjan_scc(graph)

        # Optionally sort SCCs by size descending
        if self.sort_var.get():
            sccs.sort(key=lambda x: -len(x))

        out_lines = []
        out_lines.append(f"Total nodes: {len(graph)}")
        out_lines.append(f"Total SCCs: {len(sccs)}\n")
        for i, scc in enumerate(sccs, start=1):
            out_lines.append(f"SCC #{i} (size {len(scc)}): {scc}")
        out_text = "\n".join(out_lines)
        self._set_output(out_text)
        self.status.set("Done")

    def visualize(self):
        txt = self.input_text.get('1.0', tk.END)
        try:
            graph = parse_edges(txt)
        except Exception as e:
            messagebox.showerror("Parse Error", str(e))
            return
        sccs = tarjan_scc(graph)
        visualize_graph(graph, sccs)

# ---------- Run ----------
def main():
    root = tk.Tk()
    app = SCCFinderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

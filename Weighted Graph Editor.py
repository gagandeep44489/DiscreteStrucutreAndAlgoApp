#!/usr/bin/env python3
"""
Weighted Graph Editor - single-file desktop app.

Features:
- Create and edit weighted graphs (directed or undirected)
- Add / remove nodes and edges, edit weights
- Load / Save edge-list CSV (source,target,weight)
- Optional GraphML save/load (if using networkx)
- Visualize the graph with edge weights shown
- Export adjacency matrix to CSV
- Simple Tkinter UI suitable for running in VS Code

Run: python weighted_graph_editor.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import io
import math

# ---------- Helper utilities ----------
def safe_float(x, default=1.0):
    try:
        return float(x)
    except Exception:
        return default

# ---------- Main App ----------
class WeightedGraphEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Weighted Graph Editor")
        self.geometry("1120x720")
        self.minsize(900, 600)

        # Graph: directed by default = False
        self.directed_var = tk.BooleanVar(value=False)
        self.G = nx.Graph()  # will switch to DiGraph when directed_var True
        self.current_file = None
        self.adj_df = None

        self._build_ui()
        self._build_plot_area()
        self._refresh_lists()
        self.log("App started.")

    # ---------- UI ----------
    def _build_ui(self):
        top = ttk.Frame(self, padding=6)
        top.pack(side=tk.TOP, fill=tk.X)

        ttk.Button(top, text="New Graph", command=self.new_graph).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Load CSV", command=self.load_csv).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Save CSV", command=self.save_csv).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Load GraphML", command=self.load_graphml).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Save GraphML", command=self.save_graphml).pack(side=tk.LEFT, padx=4)

        ttk.Separator(top, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=6)
        chk = ttk.Checkbutton(top, text="Directed", variable=self.directed_var, command=self.toggle_directed)
        chk.pack(side=tk.LEFT, padx=4)
        ttk.Label(top, text="  ").pack(side=tk.LEFT, padx=6)

        ttk.Button(top, text="Add Node", command=self.add_node_dialog).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Remove Node", command=self.remove_node).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Add/Edit Edge", command=self.add_edge_dialog).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Remove Edge", command=self.remove_edge).pack(side=tk.LEFT, padx=4)

        ttk.Button(top, text="Build Adjacency Matrix", command=self.build_adj_matrix).pack(side=tk.LEFT, padx=8)
        ttk.Button(top, text="Export Matrix CSV", command=self.export_matrix).pack(side=tk.LEFT, padx=4)

        # Main split: left = controls/lists, right = plot
        main = ttk.Frame(self)
        main.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=6, pady=6)

        left = ttk.Frame(main, width=380)
        left.pack(side=tk.LEFT, fill=tk.Y)

        # Node list
        ttk.Label(left, text="Nodes").pack(anchor=tk.NW)
        self.node_listbox = tk.Listbox(left, height=12, exportselection=False)
        self.node_listbox.pack(fill=tk.X, padx=2, pady=2)
        self.node_listbox.bind('<<ListboxSelect>>', lambda e: self.on_node_select())

        # Edge list
        ttk.Label(left, text="Edges (u -> v : weight)").pack(anchor=tk.NW, pady=(8,0))
        self.edge_listbox = tk.Listbox(left, height=12, exportselection=False)
        self.edge_listbox.pack(fill=tk.X, padx=2, pady=2)
        self.edge_listbox.bind('<<ListboxSelect>>', lambda e: self.on_edge_select())

        # Quick controls for selected node/edge
        control_frame = ttk.Frame(left)
        control_frame.pack(fill=tk.X, pady=(8,0))

        ttk.Button(control_frame, text="Center on Node", command=self.center_on_node).pack(side=tk.LEFT, padx=4)
        ttk.Button(control_frame, text="Highlight Edge", command=self.highlight_edge).pack(side=tk.LEFT, padx=4)

        # Info & log
        ttk.Label(left, text="Graph Info").pack(anchor=tk.NW, pady=(8,0))
        self.info_text = tk.Text(left, height=6, wrap=tk.WORD)
        self.info_text.pack(fill=tk.X, padx=2, pady=2)

        ttk.Label(left, text="Log").pack(anchor=tk.NW, pady=(8,0))
        self.log_text = tk.Text(left, height=8, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

    # ---------- Plot area ----------
    def _build_plot_area(self):
        right = ttk.Frame(self)
        right.place(x=400, y=70, relwidth=0.6, relheight=0.82)

        # Matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(6,6))
        plt.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # small controls
        ctrl = ttk.Frame(right)
        ctrl.pack(fill=tk.X)
        ttk.Button(ctrl, text="Redraw", command=self.redraw).pack(side=tk.LEFT, padx=4, pady=4)
        ttk.Button(ctrl, text="Toggle Labels", command=self.toggle_labels).pack(side=tk.LEFT, padx=4)
        self.show_labels = True

        self._pos = None  # store last layout positions
        self._highlight = None  # (u,v) tuple to highlight

    # ---------- Graph operations ----------
    def new_graph(self):
        self.G = nx.DiGraph() if self.directed_var.get() else nx.Graph()
        self.current_file = None
        self._pos = None
        self._highlight = None
        self._refresh_lists()
        self.log("Created new graph.")

    def toggle_directed(self):
        # convert graph type
        directed = self.directed_var.get()
        if directed and not isinstance(self.G, nx.DiGraph):
            self.G = nx.DiGraph(self.G)  # convert simple
            self.log("Converted graph to Directed.")
        elif not directed and isinstance(self.G, nx.DiGraph):
            self.G = nx.Graph(self.G)
            self.log("Converted graph to Undirected.")
        self._refresh_lists()
        self.redraw()

    def add_node_dialog(self):
        node = simpledialog.askstring("Add Node", "Enter node label (string):", parent=self)
        if node:
            node = str(node).strip()
            if node in self.G:
                messagebox.showinfo("Exists", f"Node '{node}' already exists.")
                return
            self.G.add_node(node)
            self.log(f"Added node: {node}")
            self._refresh_lists()
            self.redraw()

    def remove_node(self):
        sel = self._get_selected(self.node_listbox)
        if sel is None:
            messagebox.showinfo("Select", "Select a node to remove.")
            return
        node = sel
        if messagebox.askyesno("Confirm", f"Remove node '{node}' and its edges?"):
            self.G.remove_node(node)
            self.log(f"Removed node: {node}")
            self._refresh_lists()
            self.redraw()

    def add_edge_dialog(self):
        # dialog for source, target and weight
        u = simpledialog.askstring("Edge - source", "Enter source node:", parent=self)
        if u is None: return
        v = simpledialog.askstring("Edge - target", "Enter target node:", parent=self)
        if v is None: return
        w = simpledialog.askstring("Edge - weight", "Enter weight (number):", initialvalue="1.0", parent=self)
        if w is None: return
        u = str(u).strip(); v = str(v).strip()
        weight = safe_float(w, 1.0)
        if u == "" or v == "":
            messagebox.showwarning("Input", "Source and target cannot be empty.")
            return
        # auto-add nodes if missing
        if u not in self.G:
            self.G.add_node(u); self.log(f"Auto-added node: {u}")
        if v not in self.G:
            self.G.add_node(v); self.log(f"Auto-added node: {v}")
        self.G.add_edge(u, v, weight=weight)
        self.log(f"Added/Updated edge: {u} -> {v} (weight={weight})")
        self._refresh_lists()
        self.redraw()

    def remove_edge(self):
        sel = self.edge_listbox.curselection()
        if not sel:
            messagebox.showinfo("Select", "Select an edge to remove.")
            return
        idx = sel[0]
        text = self.edge_listbox.get(idx)
        # parse u,v from displayed text
        try:
            u_v = text.split(':')[0].strip()
            if '->' in u_v:
                u, v = [s.strip() for s in u_v.split('->')]
            elif '--' in u_v:
                u, v = [s.strip() for s in u_v.split('--')]
            else:
                parts = u_v.split()
                u, v = parts[0], parts[1]
        except Exception:
            messagebox.showerror("Parse error", "Failed to parse edge selection.")
            return
        if messagebox.askyesno("Confirm", f"Remove edge {u} -> {v}?"):
            if self.G.has_edge(u, v):
                self.G.remove_edge(u, v)
                self.log(f"Removed edge: {u} -> {v}")
            else:
                self.log(f"Edge not found: {u} -> {v}")
            self._refresh_lists()
            self.redraw()

    # ---------- Load/Save ----------
    def load_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files","*.csv"), ("All files","*.*")])
        if not path:
            return
        try:
            df = pd.read_csv(path)
        except Exception as e:
            messagebox.showerror("Read error", f"Failed to read CSV: {e}")
            return
        cols = [c.lower() for c in df.columns]
        # detect columns
        src = None; tgt = None; wt = None
        for c in df.columns:
            lc = c.lower()
            if 'source' in lc or 'from' in lc or lc in ('u','node1','a'):
                src = c; break
        for c in df.columns:
            lc = c.lower()
            if 'target' in lc or 'to' in lc or lc in ('v','node2','b'):
                tgt = c; break
        for c in df.columns:
            if 'weight' in c.lower() or 'w' == c.lower():
                wt = c; break
        if src is None or tgt is None:
            # fallback to first two columns
            if len(df.columns) >= 2:
                src, tgt = df.columns[0], df.columns[1]
            else:
                messagebox.showerror("Format", "CSV must contain at least two columns: source, target")
                return
        # Build graph
        directed = self.directed_var.get()
        self.G = nx.DiGraph() if directed else nx.Graph()
        for _, r in df.iterrows():
            u = str(r[src]); v = str(r[tgt])
            if wt is not None and wt in df.columns:
                w = safe_float(r[wt], 1.0)
            else:
                w = 1.0
            if u == "" or v == "":
                continue
            self.G.add_node(u); self.G.add_node(v)
            self.G.add_edge(u, v, weight=w)
        self.current_file = path
        self.log(f"Loaded CSV: {os.path.basename(path)} ({len(self.G.nodes())} nodes, {len(self.G.edges())} edges)")
        self._refresh_lists()
        self.redraw()

    def save_csv(self):
        if self.G is None or len(self.G.nodes()) == 0:
            messagebox.showinfo("Empty", "Graph is empty.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if not path:
            return
        rows = []
        for u,v,data in self.G.edges(data=True):
            w = data.get('weight', 1.0)
            rows.append((u,v,w))
        df = pd.DataFrame(rows, columns=['source','target','weight'])
        try:
            df.to_csv(path, index=False)
            self.log(f"Saved CSV: {path}")
            messagebox.showinfo("Saved", f"Saved to: {path}")
        except Exception as e:
            messagebox.showerror("Save error", f"Failed to save: {e}")

    def load_graphml(self):
        path = filedialog.askopenfilename(filetypes=[("GraphML files","*.graphml"), ("All files","*.*")])
        if not path:
            return
        try:
            G = nx.read_graphml(path)
            # convert nodes to str and ensure weight attribute present
            G2 = nx.DiGraph() if self.directed_var.get() else nx.Graph()
            for n,d in G.nodes(data=True):
                G2.add_node(str(n), **d)
            for u,v,d in G.edges(data=True):
                w = d.get('weight', 1.0)
                try:
                    w = float(w)
                except Exception:
                    w = 1.0
                G2.add_edge(str(u), str(v), weight=w)
            self.G = G2
            self.log(f"Loaded GraphML: {os.path.basename(path)}")
            self._refresh_lists()
            self.redraw()
        except Exception as e:
            messagebox.showerror("Read error", f"Failed to read GraphML: {e}")

    def save_graphml(self):
        path = filedialog.asksaveasfilename(defaultextension=".graphml", filetypes=[("GraphML files","*.graphml")])
        if not path:
            return
        try:
            nx.write_graphml(self.G, path)
            self.log(f"Saved GraphML: {path}")
            messagebox.showinfo("Saved", f"Saved to: {path}")
        except Exception as e:
            messagebox.showerror("Save error", f"Failed to save GraphML: {e}")

    # ---------- Lists & UI refresh ----------
    def _refresh_lists(self):
        # refresh node listbox
        self.node_listbox.delete(0, tk.END)
        for n in sorted(self.G.nodes()):
            self.node_listbox.insert(tk.END, str(n))
        # refresh edge listbox
        self.edge_listbox.delete(0, tk.END)
        for u,v,data in sorted(self.G.edges(data=True)):
            w = data.get('weight', 1.0)
            arrow = '->' if self.directed_var.get() else '--'
            self.edge_listbox.insert(tk.END, f"{u} {arrow} {v} : {w}")
        # update info
        self._update_info()

    def _update_info(self):
        buf = io.StringIO()
        buf.write(f"Nodes: {len(self.G.nodes())}\n")
        buf.write(f"Edges: {len(self.G.edges())}\n")
        # basic stats
        degs = [d for _,d in self.G.degree(weight='weight')]
        if degs:
            buf.write(f"Avg degree (weighted sum): {sum(degs)/len(degs):.3f}\n")
        else:
            buf.write("Avg degree: 0\n")
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, buf.getvalue())

    # ---------- Selection helpers ----------
    def _get_selected(self, listbox):
        sel = listbox.curselection()
        if not sel:
            return None
        return listbox.get(sel[0])

    def on_node_select(self):
        sel = self.node_listbox.curselection()
        if not sel:
            return
        node = self.node_listbox.get(sel[0])
        # show neighbors or details
        neighbors = list(self.G.neighbors(node)) if node in self.G else []
        self.log(f"Selected node: {node} (neighbors: {len(neighbors)})")
        # center view on node
        self.center_on_node(node)

    def on_edge_select(self):
        sel = self.edge_listbox.curselection()
        if not sel:
            return
        text = self.edge_listbox.get(sel[0])
        self.log(f"Selected edge: {text}")

    # ---------- Visualization ----------
    def redraw(self):
        self.ax.clear()
        if self.G is None or len(self.G.nodes()) == 0:
            self.ax.set_title("No graph loaded")
            self.canvas.draw()
            return
        # compute layout (re-use positions if present)
        if self._pos is None or len(self._pos) != len(self.G):
            self._pos = nx.spring_layout(self.G, seed=42)
        pos = self._pos
        # draw edges
        weights = [self.G[u][v].get('weight',1.0) for u,v in self.G.edges()]
        # normalize widths
        widths = []
        if weights:
            minw = min(weights); maxw = max(weights)
            for w in weights:
                if math.isclose(minw, maxw):
                    widths.append(1.5)
                else:
                    widths.append(0.5 + 3.5*(w - minw)/(maxw - minw))
        else:
            widths = 1
        nx.draw_networkx_edges(self.G, pos, ax=self.ax, width=widths, alpha=0.7)
        # draw nodes
        deg = dict(self.G.degree(weight='weight'))
        node_sizes = [100 + 60*deg.get(n,0) for n in self.G.nodes()]
        nx.draw_networkx_nodes(self.G, pos, ax=self.ax, node_size=node_sizes)
        # labels
        if self.show_labels:
            nx.draw_networkx_labels(self.G, pos, ax=self.ax, font_size=9)
        # edge labels (weights)
        edge_labels = {(u,v): f"{self.G[u][v].get('weight',1.0):.2f}" for u,v in self.G.edges()}
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels, ax=self.ax, font_size=8)
        # highlight if requested
        if self._highlight:
            u,v = self._highlight
            if self.G.has_edge(u,v):
                nx.draw_networkx_edges(self.G, pos, edgelist=[(u,v)], ax=self.ax, edge_color='red', width=4.0)
        self.ax.set_axis_off()
        self.canvas.draw()
        self._update_info()

    def toggle_labels(self):
        self.show_labels = not self.show_labels
        self.redraw()

    def center_on_node(self, node_label=None):
        if node_label is None:
            sel = self.node_listbox.curselection()
            if not sel:
                messagebox.showinfo("Select", "Select a node first.")
                return
            node_label = self.node_listbox.get(sel[0])
        # recompute layout with that node centered by using spring with fixed initial pos
        try:
            self._pos = nx.spring_layout(self.G, center=(0,0), seed=42)
            # small trick: nudge positions so chosen node is near center (not perfect but helps)
            if node_label in self._pos:
                cx, cy = self._pos[node_label]
                shiftx, shifty = -cx, -cy
                for k in self._pos:
                    x,y = self._pos[k]
                    self._pos[k] = (x + shiftx, y + shifty)
            self.redraw()
            self.log(f"Centered on node: {node_label}")
        except Exception as e:
            self.log(f"Center failed: {e}")

    def highlight_edge(self):
        sel = self.edge_listbox.curselection()
        if not sel:
            messagebox.showinfo("Select", "Select an edge to highlight.")
            return
        text = self.edge_listbox.get(sel[0])
        try:
            u_v = text.split(':')[0].strip()
            if '->' in u_v:
                u,v = [s.strip() for s in u_v.split('->')]
            elif '--' in u_v:
                u,v = [s.strip() for s in u_v.split('--')]
            else:
                parts = u_v.split()
                u, v = parts[0], parts[1]
            if self.G.has_edge(u,v):
                self._highlight = (u,v)
                self.log(f"Highlighting edge: {u} -> {v}")
                self.redraw()
            else:
                messagebox.showinfo("Not found", "Edge not found in graph.")
        except Exception:
            messagebox.showerror("Parse error", "Failed to parse selected edge.")

    # ---------- Adjacency matrix ----------
    def build_adj_matrix(self):
        if self.G is None or len(self.G.nodes()) == 0:
            messagebox.showinfo("Empty", "Graph is empty.")
            return
        nodes = list(self.G.nodes())
        mat = pd.DataFrame(0.0, index=nodes, columns=nodes)
        for u,v,data in self.G.edges(data=True):
            w = data.get('weight', 1.0)
            mat.at[u, v] = w
            if not isinstance(self.G, nx.DiGraph):
                mat.at[v, u] = w
        self.adj_df = mat
        # show a small preview in a dialog or saveable
        preview = io.StringIO()
        preview.write(f"Adjacency matrix ({mat.shape[0]}x{mat.shape[1]}) created.\n")
        preview.write(mat.head(10).to_string())
        messagebox.showinfo("Matrix Built", f"Adjacency matrix built. Preview printed to log.")
        self.log(preview.getvalue())

    def export_matrix(self):
        if self.adj_df is None:
            messagebox.showinfo("No matrix", "Build the adjacency matrix first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if not path:
            return
        try:
            self.adj_df.to_csv(path)
            self.log(f"Exported adjacency matrix: {path}")
            messagebox.showinfo("Saved", f"Saved adjacency matrix to {path}")
        except Exception as e:
            messagebox.showerror("Export error", f"Failed to export matrix: {e}")

    # ---------- Logging ----------
    def log(self, text):
        self.log_text.insert(tk.END, f"{text}\n")
        self.log_text.see(tk.END)

# ---------- Run ----------
if __name__ == "__main__":
    app = WeightedGraphEditor()
    app.mainloop()

#!/usr/bin/env python3
"""
Adjacency Matrix Generator - single-file desktop app.

Features:
- Load edge-list CSV (columns: source,target[,weight])
- Option: treat graph as directed or undirected
- Build adjacency matrix (weighted or binary)
- Display matrix in a table (Treeview) and as a heatmap
- Visualize graph (NetworkX) with spring layout
- Export matrix to CSV and heatmap to PNG

Run: python adj_matrix_generator.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import io

plt.rcParams.update({"figure.autolayout": True})

class AdjacencyMatrixApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Adjacency Matrix Generator")
        self.geometry("1100x720")
        self.minsize(900, 600)

        self.df_edges = None   # original edge dataframe
        self.adj_df = None     # pandas adjacency matrix
        self.G = None          # networkx graph

        self._make_widgets()
        self._make_plot_area()

    def _make_widgets(self):
        top = ttk.Frame(self, padding=8)
        top.pack(side=tk.TOP, fill=tk.X)

        btn_load = ttk.Button(top, text="Load Edge CSV", command=self.load_edge_csv)
        btn_load.pack(side=tk.LEFT, padx=4)

        btn_load_nodes = ttk.Button(top, text="Load Node List (optional)", command=self.load_node_list)
        btn_load_nodes.pack(side=tk.LEFT, padx=4)

        self.directed_var = tk.BooleanVar(value=False)
        chk_directed = ttk.Checkbutton(top, text="Directed", variable=self.directed_var)
        chk_directed.pack(side=tk.LEFT, padx=8)

        self.weighted_var = tk.BooleanVar(value=False)
        chk_weighted = ttk.Checkbutton(top, text="Weighted (use 'weight' col)", variable=self.weighted_var)
        chk_weighted.pack(side=tk.LEFT, padx=8)

        btn_build = ttk.Button(top, text="Build Matrix", command=self.build_matrix)
        btn_build.pack(side=tk.LEFT, padx=4)

        btn_export = ttk.Button(top, text="Export Matrix CSV", command=self.export_matrix)
        btn_export.pack(side=tk.LEFT, padx=4)

        btn_export_png = ttk.Button(top, text="Export Heatmap PNG", command=self.export_heatmap)
        btn_export_png.pack(side=tk.LEFT, padx=4)

        btn_clear = ttk.Button(top, text="Clear", command=self.clear_all)
        btn_clear.pack(side=tk.LEFT, padx=4)

        info = ttk.Label(top, text="CSV format: source,target[,weight]. Header optional. Node list: one node per line.")
        info.pack(side=tk.LEFT, padx=12)

        # Bottom split: left = plot, right = table + log
        bottom = ttk.Frame(self)
        bottom.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=6, pady=6)

        # Plot area
        self.plot_frame = ttk.Frame(bottom, relief=tk.SUNKEN)
        self.plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Right frame
        right = ttk.Frame(bottom, width=420)
        right.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview for adjacency matrix
        mat_label = ttk.Label(right, text="Adjacency Matrix (preview)")
        mat_label.pack(anchor=tk.NW)
        self.tree = ttk.Treeview(right, show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=(4,8))

        # Row count / info
        self.info_text = tk.Text(right, height=8, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=False)

        # Log
        log_label = ttk.Label(right, text="Log")
        log_label.pack(anchor=tk.NW, pady=(8,0))
        self.log_text = tk.Text(right, height=6, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=False)

    def _make_plot_area(self):
        # create matplotlib figures: one for network visualization, one for heatmap
        self.fig_net, self.ax_net = plt.subplots(figsize=(6,5))
        self.fig_heat, self.ax_heat = plt.subplots(figsize=(6,5))
        # use a single canvas that we'll swap between figures
        self.canvas = FigureCanvasTkAgg(self.fig_net, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # small control to switch view
        ctrl = ttk.Frame(self.plot_frame)
        ctrl.pack(fill=tk.X)
        btn_net = ttk.Button(ctrl, text="Show Graph", command=self.show_network)
        btn_net.pack(side=tk.LEFT, padx=2, pady=4)
        btn_heat = ttk.Button(ctrl, text="Show Heatmap", command=self.show_heatmap)
        btn_heat.pack(side=tk.LEFT, padx=2, pady=4)
        btn_zoom = ttk.Button(ctrl, text="Redraw", command=self.redraw_current)
        btn_zoom.pack(side=tk.LEFT, padx=2, pady=4)

        self._current_view = "net"

    def load_edge_csv(self):
        path = filedialog.askopenfilename(title="Select edge-list CSV", filetypes=[("CSV files","*.csv"),("All files","*.*")])
        if not path:
            return
        try:
            df = pd.read_csv(path)
        except Exception as e:
            messagebox.showerror("Read error", f"Failed to read CSV: {e}")
            return

        # normalize columns
        cols = [c.lower() for c in df.columns]
        if len(cols) < 2:
            messagebox.showerror("Format error", "CSV must contain at least two columns for source and target.")
            return

        # Try to detect source/target column names
        source_col = None
        target_col = None
        for c in df.columns:
            lc = c.lower()
            if 'source' in lc or 'from' in lc or lc == 'u' or lc == 'node1':
                source_col = c
                break
        for c in df.columns:
            lc = c.lower()
            if 'target' in lc or 'to' in lc or lc == 'v' or lc == 'node2':
                target_col = c
                break
        if source_col is None or target_col is None:
            # fallback to first two columns
            source_col, target_col = df.columns[0], df.columns[1]

        # If weight column exists and user will choose weighted, we accept 'weight' column if present
        weight_col = None
        for c in df.columns:
            if 'weight' in c.lower():
                weight_col = c
                break

        # store in expected format
        if weight_col is not None:
            df = df[[source_col, target_col, weight_col]].rename(columns={source_col:'source', target_col:'target', weight_col:'weight'})
        else:
            df = df[[source_col, target_col]].rename(columns={source_col:'source', target_col:'target'})

        # cast to string for nodes
        df['source'] = df['source'].astype(str)
        df['target'] = df['target'].astype(str)
        self.df_edges = df
        self.log(f"Loaded edges: {len(df)} rows from {os.path.basename(path)}. Columns used: {list(df.columns)}")
        # Auto-check weighted if weight column present
        if 'weight' in df.columns:
            self.weighted_var.set(True)
        self.build_matrix()

    def load_node_list(self):
        path = filedialog.askopenfilename(title="Select node list (one node per line)", filetypes=[("Text files","*.txt"),("All files","*.*")])
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                nodes = [line.strip() for line in f if line.strip()]
            if not nodes:
                messagebox.showwarning("Empty file", "Node list file is empty.")
                return
            # If there is an edge dataframe, ensure nodes are included (this file just provides ordering/all nodes)
            if self.df_edges is None:
                # create empty edges DF to be filled later
                self.df_edges = pd.DataFrame(columns=['source','target'])
            # Save nodes ordering in a special attribute
            self._node_list = nodes
            self.log(f"Loaded node list with {len(nodes)} nodes from {os.path.basename(path)}")
            self.build_matrix()
        except Exception as e:
            messagebox.showerror("Read error", f"Failed to read node list: {e}")

    def build_matrix(self):
        if self.df_edges is None or self.df_edges.empty:
            messagebox.showinfo("No data", "Please load an edge CSV first.")
            return

        weighted = self.weighted_var.get()
        directed = self.directed_var.get()

        # Determine node set: from edge list and optionally from provided node list
        nodes = pd.unique(self.df_edges[['source','target']].values.ravel())
        # If user provided node list earlier, use that ordering and include missing nodes
        node_list = getattr(self, '_node_list', None)
        if node_list:
            # include any nodes from edges not in node_list and append them
            extras = [n for n in nodes if n not in node_list]
            nodes_ordered = list(node_list) + extras
        else:
            nodes_ordered = sorted(nodes.astype(str).tolist(), key=lambda x: str(x))

        # create adjacency matrix
        n = len(nodes_ordered)
        mat = pd.DataFrame(0, index=nodes_ordered, columns=nodes_ordered, dtype=float)

        # fill matrix
        if 'weight' in self.df_edges.columns and weighted:
            for _, row in self.df_edges.iterrows():
                s = str(row['source'])
                t = str(row['target'])
                try:
                    w = float(row['weight'])
                except Exception:
                    w = 1.0
                if s not in mat.index or t not in mat.columns:
                    continue
                mat.at[s, t] += w
                if not directed:
                    mat.at[t, s] += w
        else:
            # binary edges
            for _, row in self.df_edges.iterrows():
                s = str(row['source'])
                t = str(row['target'])
                if s not in mat.index or t not in mat.columns:
                    continue
                mat.at[s, t] = 1
                if not directed:
                    mat.at[t, s] = 1

        self.adj_df = mat
        self.log(f"Adjacency matrix built: {n} nodes, directed={directed}, weighted={weighted}")
        self._update_table_preview()
        self._build_networkx_graph()
        self.show_heatmap()

    def _update_table_preview(self, max_preview=50):
        # Clear existing tree
        for i in self.tree.get_children():
            self.tree.delete(i)
        if self.adj_df is None:
            return
        df = self.adj_df.copy()
        # For very large matrices, show only top-left max_preview x max_preview
        if df.shape[0] > max_preview:
            show_idx = df.index[:max_preview]
            dfp = df.loc[show_idx, df.columns[:max_preview]]
            truncated = True
        else:
            dfp = df
            truncated = False

        cols = ['node'] + list(dfp.columns)
        self.tree["columns"] = cols
        for c in cols:
            self.tree.heading(c, text=str(c))
            # small width; allow horizontal scroll
            self.tree.column(c, width=80, anchor=tk.CENTER)

        # insert rows
        for idx, row in dfp.iterrows():
            vs = [str(idx)] + [str(row[c]) for c in dfp.columns]
            self.tree.insert("", tk.END, values=vs)

        if truncated:
            self.log(f"Preview truncated to {max_preview}x{max_preview}. Full matrix still available to export.")
        else:
            self.log("Preview updated.")

        # update info text
        info = io.StringIO()
        info.write(f"Matrix shape: {self.adj_df.shape}\n")
        info.write(f"Nodes: {len(self.adj_df.index)}\n")
        info.write(f"Total edges (non-zero entries): {int((self.adj_df != 0).sum().sum())}\n")
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, info.getvalue())

    def _build_networkx_graph(self):
        if self.adj_df is None:
            return
        directed = self.directed_var.get()
        if directed:
            G = nx.DiGraph()
        else:
            G = nx.Graph()
        # add nodes
        G.add_nodes_from(self.adj_df.index.tolist())
        # add edges with weights if >0
        for u in self.adj_df.index:
            for v in self.adj_df.columns:
                val = self.adj_df.at[u, v]
                if val != 0:
                    if val == 1:
                        G.add_edge(u, v)
                    else:
                        G.add_edge(u, v, weight=float(val))
        self.G = G
        self.log(f"NetworkX graph created: nodes={G.number_of_nodes()}, edges={G.number_of_edges()}")

    def show_network(self):
        if self.G is None or self.G.number_of_nodes() == 0:
            messagebox.showinfo("No graph", "Build matrix first.")
            return
        self._current_view = "net"
        self.fig_net.clf()
        self.ax_net = self.fig_net.subplots()
        self.ax_net.set_title("Graph Visualization (spring layout)")
        pos = nx.spring_layout(self.G, seed=42)
        # node sizes by degree
        deg = dict(self.G.degree())
        node_sizes = [50 + 30*deg[n] for n in self.G.nodes()]
        nx.draw_networkx_edges(self.G, pos, ax=self.ax_net, alpha=0.4)
        nx.draw_networkx_nodes(self.G, pos, ax=self.ax_net, node_size=node_sizes)
        # labels small to avoid clutter
        nx.draw_networkx_labels(self.G, pos, font_size=7)
        self.ax_net.set_axis_off()
        self.canvas.figure = self.fig_net
        self.canvas.draw()

    def show_heatmap(self):
        if self.adj_df is None:
            messagebox.showinfo("No matrix", "Build matrix first.")
            return
        self._current_view = "heat"
        self.fig_heat.clf()
        self.ax_heat = self.fig_heat.subplots()
        self.ax_heat.set_title("Adjacency Matrix Heatmap")
        mat = self.adj_df.values.astype(float)
        # If huge, sample or use imshow with interpolation
        im = self.ax_heat.imshow(mat, aspect='auto', interpolation='nearest')
        # ticks only if small
        n = mat.shape[0]
        if n <= 60:
            self.ax_heat.set_xticks(np.arange(n))
            self.ax_heat.set_yticks(np.arange(n))
            self.ax_heat.set_xticklabels(self.adj_df.columns, rotation=90, fontsize=7)
            self.ax_heat.set_yticklabels(self.adj_df.index, fontsize=7)
        else:
            self.ax_heat.set_xticks([])
            self.ax_heat.set_yticks([])
        self.fig_heat.colorbar(im, ax=self.ax_heat, fraction=0.046, pad=0.04)
        self.canvas.figure = self.fig_heat
        self.canvas.draw()

    def redraw_current(self):
        if self._current_view == "net":
            self.show_network()
        else:
            self.show_heatmap()

    def export_matrix(self):
        if self.adj_df is None:
            messagebox.showinfo("No matrix", "Build matrix first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV file","*.csv")])
        if not path:
            return
        try:
            self.adj_df.to_csv(path)
            messagebox.showinfo("Exported", f"Matrix exported to:\n{path}")
            self.log(f"Matrix exported: {path}")
        except Exception as e:
            messagebox.showerror("Export error", f"Failed to export CSV: {e}")

    def export_heatmap(self):
        if self.adj_df is None:
            messagebox.showinfo("No matrix", "Build matrix first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG image","*.png")])
        if not path:
            return
        try:
            # ensure heatmap is drawn large and saved
            self.fig_heat.savefig(path, dpi=200)
            messagebox.showinfo("Exported", f"Heatmap exported to:\n{path}")
            self.log(f"Heatmap exported: {path}")
        except Exception as e:
            messagebox.showerror("Export error", f"Failed to export PNG: {e}")

    def clear_all(self):
        self.df_edges = None
        self.adj_df = None
        self.G = None
        self._node_list = None
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.info_text.delete(1.0, tk.END)
        self.log_text.delete(1.0, tk.END)
        self.ax_net.clear()
        self.ax_net.set_title("No graph loaded")
        self.canvas.draw()
        self.log("Cleared all data.")

    def log(self, text):
        self.log_text.insert(tk.END, f"{text}\n")
        self.log_text.see(tk.END)

if __name__ == "__main__":
    app = AdjacencyMatrixApp()
    app.mainloop()

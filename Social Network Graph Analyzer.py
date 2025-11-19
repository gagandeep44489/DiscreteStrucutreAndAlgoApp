#!/usr/bin/env python3
"""
Social Network Graph Analyzer
Single-file desktop app using Tkinter, NetworkX, Matplotlib, Pandas.
Save as social_network_analyzer.py and run: python social_network_analyzer.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import csv
import io

# Try importing community (python-louvain); if not available, community detection will be disabled
try:
    import community as community_louvain
    LOUVAIN_AVAILABLE = True
except Exception:
    LOUVAIN_AVAILABLE = False

class SocialNetworkAnalyzer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Social Network Graph Analyzer")
        self.geometry("1100x720")
        self.minsize(900, 600)

        self.graph = nx.Graph()
        self.current_filepath = None
        self.analysis_df = None

        self._create_widgets()
        self._create_plot_area()

    def _create_widgets(self):
        # Top frame for controls
        top = ttk.Frame(self, padding=(8,8))
        top.pack(side=tk.TOP, fill=tk.X)

        btn_load = ttk.Button(top, text="Load Edge List (CSV)", command=self.load_edge_csv)
        btn_load.pack(side=tk.LEFT, padx=4)

        btn_vis = ttk.Button(top, text="Visualize Graph", command=self.visualize_graph)
        btn_vis.pack(side=tk.LEFT, padx=4)

        btn_analyze = ttk.Button(top, text="Analyze Graph", command=self.analyze_graph)
        btn_analyze.pack(side=tk.LEFT, padx=4)

        btn_export = ttk.Button(top, text="Export Analysis CSV", command=self.export_analysis)
        btn_export.pack(side=tk.LEFT, padx=4)

        btn_clear = ttk.Button(top, text="Clear Graph", command=self.clear_graph)
        btn_clear.pack(side=tk.LEFT, padx=4)

        info_label = ttk.Label(top, text="Supported CSV format: source,target (header optional). Additional columns ignored.")
        info_label.pack(side=tk.LEFT, padx=16)

        # Lower frame split: left = plot, right = analysis & log
        bottom = ttk.Frame(self)
        bottom.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Plot area frame
        self.plot_frame = ttk.Frame(bottom, relief=tk.SUNKEN)
        self.plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=6)

        # Analysis / Table / Log frame
        right_frame = ttk.Frame(bottom, width=360)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=6, pady=6)

        # Treeview for node metrics
        tree_label = ttk.Label(right_frame, text="Node Metrics")
        tree_label.pack(anchor=tk.NW)

        cols = ("node", "degree", "deg_centrality", "bet_centrality", "close_centrality", "clustering", "community")
        self.tree = ttk.Treeview(right_frame, columns=cols, show="headings", height=18)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=100, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=False)

        # Text log
        log_label = ttk.Label(right_frame, text="Log / Summary")
        log_label.pack(anchor=tk.NW, pady=(8,0))
        self.log_text = tk.Text(right_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def _create_plot_area(self):
        # create an initial empty matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(6,6))
        plt.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def load_edge_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not path:
            return
        try:
            df = pd.read_csv(path)
        except Exception as e:
            messagebox.showerror("File error", f"Failed to read CSV: {e}")
            return

        # Try to infer columns: look for first two columns whose names include 'source' or 'target' or assume first two
        cols = list(df.columns)
        if len(cols) < 2:
            messagebox.showerror("Format error", "CSV must have at least two columns (source,target).")
            return

        # Heuristics for names
        source_col, target_col = None, None
        for c in cols:
            cl = c.lower()
            if 'source' in cl or 'from' in cl or 'u' == cl:
                source_col = c
                break
        for c in cols:
            cl = c.lower()
            if 'target' in cl or 'to' in cl or 'v' == cl:
                target_col = c
                break

        if source_col is None or target_col is None:
            # fallback to first two columns
            source_col, target_col = cols[0], cols[1]

        edges = df[[source_col, target_col]].dropna().astype(str).values.tolist()
        self.graph = nx.Graph()
        self.graph.add_edges_from(edges)
        self.current_filepath = path
        self.log(f"Loaded {len(self.graph.nodes())} nodes and {len(self.graph.edges())} edges from:\n{os.path.basename(path)}")
        self.visualize_graph()

    def visualize_graph(self, color_by_community=False):
        if self.graph is None or self.graph.number_of_nodes() == 0:
            messagebox.showinfo("No graph", "Load a graph first.")
            return
        self.ax.clear()
        self.ax.set_title("Social Network Graph Visualization")
        # compute layout
        pos = nx.spring_layout(self.graph, seed=42)
        # node coloring: by community if available and requested
        node_colors = None
        if color_by_community and LOUVAIN_AVAILABLE:
            partition = community_louvain.best_partition(self.graph)
            # map communities to integers
            nodes = list(self.graph.nodes())
            node_colors = [partition.get(n, 0) for n in nodes]
        # draw
        nx.draw_networkx_edges(self.graph, pos, alpha=0.4, ax=self.ax)
        if node_colors is None:
            nx.draw_networkx_nodes(self.graph, pos, node_size=120, ax=self.ax)
        else:
            nx.draw_networkx_nodes(self.graph, pos, node_color=node_colors, cmap=plt.cm.tab20, node_size=140, ax=self.ax)
        # small labels for readability
        nx.draw_networkx_labels(self.graph, pos, font_size=8, ax=self.ax)
        self.ax.set_axis_off()
        self.canvas.draw()

    def analyze_graph(self):
        if self.graph is None or self.graph.number_of_nodes() == 0:
            messagebox.showinfo("No graph", "Load a graph first.")
            return

        G = self.graph
        n_nodes = G.number_of_nodes()
        n_edges = G.number_of_edges()
        degrees = dict(G.degree())
        deg_cent = nx.degree_centrality(G)
        try:
            bet_cent = nx.betweenness_centrality(G)
        except Exception:
            bet_cent = {n: 0.0 for n in G.nodes()}
        try:
            close_cent = nx.closeness_centrality(G)
        except Exception:
            close_cent = {n: 0.0 for n in G.nodes()}
        clustering = nx.clustering(G)
        comp = list(nx.connected_components(G))
        num_components = len(comp)
        avg_degree = sum(dict(G.degree()).values()) / float(n_nodes) if n_nodes else 0

        # community detection (optional)
        communities = None
        if LOUVAIN_AVAILABLE:
            try:
                communities = community_louvain.best_partition(G)
                self.log("Louvain community detection applied.")
            except Exception as e:
                communities = None
                self.log(f"Community detection failed: {e}")
        else:
            self.log("python-louvain not installed: community detection skipped.")

        # Build DataFrame
        rows = []
        for node in G.nodes():
            rows.append({
                "node": node,
                "degree": degrees.get(node, 0),
                "deg_centrality": round(deg_cent.get(node, 0.0), 6),
                "bet_centrality": round(bet_cent.get(node, 0.0), 6),
                "close_centrality": round(close_cent.get(node, 0.0), 6),
                "clustering": round(clustering.get(node, 0.0), 6),
                "community": communities.get(node) if communities else ""
            })
        df = pd.DataFrame(rows).sort_values(by="degree", ascending=False)
        self.analysis_df = df

        # populate treeview
        for i in self.tree.get_children():
            self.tree.delete(i)
        for _, r in df.iterrows():
            vals = (str(r["node"]), r["degree"], r["deg_centrality"], r["bet_centrality"], r["close_centrality"], r["clustering"], r["community"])
            self.tree.insert("", tk.END, values=vals)

        # summary log
        self.log_text.delete(1.0, tk.END)
        summary = io.StringIO()
        print(f"Nodes: {n_nodes}", file=summary)
        print(f"Edges: {n_edges}", file=summary)
        print(f"Connected components: {num_components}", file=summary)
        print(f"Average degree: {avg_degree:.3f}", file=summary)
        # top 5 by degree
        top5 = df.sort_values(by="degree", ascending=False).head(5)
        print("\nTop 5 nodes by degree:", file=summary)
        for _, r in top5.iterrows():
            print(f" - {r['node']} (degree {r['degree']})", file=summary)
        if communities:
            unique_comms = sorted(set(communities.values()))
            print(f"\nDetected communities: {len(unique_comms)} (IDs: {unique_comms})", file=summary)

        self.log_text.insert(tk.END, summary.getvalue())
        self.log("Analysis computed.")
        # show visualization colored by community if available
        self.visualize_graph(color_by_community=bool(communities))

    def export_analysis(self):
        if self.analysis_df is None:
            messagebox.showinfo("No data", "Run analysis before exporting.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if not path:
            return
        try:
            self.analysis_df.to_csv(path, index=False)
            messagebox.showinfo("Exported", f"Analysis exported to:\n{path}")
            self.log(f"Exported analysis CSV to: {path}")
        except Exception as e:
            messagebox.showerror("Export error", f"Failed to export: {e}")

    def clear_graph(self):
        self.graph = nx.Graph()
        self.analysis_df = None
        self.current_filepath = None
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.log_text.delete(1.0, tk.END)
        self.ax.clear()
        self.ax.set_title("No graph loaded")
        self.canvas.draw()
        self.log("Graph cleared.")

    def log(self, text):
        self.log_text.insert(tk.END, f"{text}\n")
        self.log_text.see(tk.END)

if __name__ == "__main__":
    app = SocialNetworkAnalyzer()
    app.mainloop()

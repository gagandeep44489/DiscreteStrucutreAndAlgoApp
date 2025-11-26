"""
Airline Route Optimization Tool (Desktop, Tkinter)

Features:
- Add / remove airports (nodes)
- Add / remove routes (edges) with distance and cost attributes
- Load / Save network to CSV files (airports.csv and routes.csv)
- Visualize graph
- Shortest path by distance or cost (Dijkstra)
- Minimum Spanning Tree (Kruskal / Prim)
- Simple TSP heuristic (Nearest Neighbor)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

plt.rcParams["figure.figsize"] = (7, 5)


class AirlineRouteOptimizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Airline Route Optimization Tool")
        self.g = nx.Graph()

        # --- UI layout ---
        left = ttk.Frame(root, padding=8)
        left.grid(row=0, column=0, sticky="ns")
        right = ttk.Frame(root, padding=8)
        right.grid(row=0, column=1, sticky="nsew")
        root.columnconfigure(1, weight=1)
        root.rowconfigure(0, weight=1)

        # Buttons
        ttk.Button(left, text="Add Airport", width=22, command=self.add_airport).pack(pady=4)
        ttk.Button(left, text="Remove Airport", width=22, command=self.remove_airport).pack(pady=4)
        ttk.Button(left, text="Add Route", width=22, command=self.add_route).pack(pady=4)
        ttk.Button(left, text="Remove Route", width=22, command=self.remove_route).pack(pady=4)

        ttk.Separator(left).pack(fill="x", pady=6)
        ttk.Button(left, text="Show Network", width=22, command=self.show_network).pack(pady=4)
        ttk.Button(left, text="Shortest Path", width=22, command=self.shortest_path_dialog).pack(pady=4)
        ttk.Button(left, text="Minimum Spanning Tree", width=22, command=self.show_mst).pack(pady=4)
        ttk.Button(left, text="TSP (Nearest Neighbor)", width=22, command=self.tsp_dialog).pack(pady=4)

        ttk.Separator(left).pack(fill="x", pady=6)
        ttk.Button(left, text="Load Network (CSV)", width=22, command=self.load_network_csv).pack(pady=4)
        ttk.Button(left, text="Save Network (CSV)", width=22, command=self.save_network_csv).pack(pady=4)

        ttk.Separator(left).pack(fill="x", pady=6)
        ttk.Button(left, text="Clear Graph", width=22, command=self.clear_graph).pack(pady=4)
        ttk.Button(left, text="Exit", width=22, command=root.quit).pack(pady=4)

        # Right pane: logs / info
        ttk.Label(right, text="Log / Output:").pack(anchor="w")
        self.log = tk.Text(right, height=20, wrap="word")
        self.log.pack(fill="both", expand=True)

        # Quick demo: helpful hint
        self.log_message("Welcome — Airline Route Optimization Tool ready.\n"
                         "Use 'Add Airport' and 'Add Route' to build your network, or load from CSV.")

    # -------------------------
    # Utility / UI helpers
    # -------------------------
    def log_message(self, msg):
        self.log.insert("end", msg + "\n")
        self.log.see("end")

    def ask_airport_name(self, prompt="Enter airport code/name (unique):"):
        val = simpledialog.askstring("Airport", prompt, parent=self.root)
        if val:
            return val.strip()
        return None

    # -------------------------
    # Graph operations
    # -------------------------
    def add_airport(self):
        name = self.ask_airport_name()
        if not name:
            return
        if name in self.g.nodes:
            messagebox.showwarning("Exists", f"Airport '{name}' already exists.")
            return
        # Optional: store attributes like coordinates later
        self.g.add_node(name)
        self.log_message(f"Added airport: {name}")

    def remove_airport(self):
        name = self.ask_airport_name("Enter airport to remove:")
        if not name: return
        if name not in self.g.nodes:
            messagebox.showerror("Not found", f"Airport '{name}' not found.")
            return
        self.g.remove_node(name)
        self.log_message(f"Removed airport: {name}")

    def add_route(self):
        u = simpledialog.askstring("Route - from", "Enter source airport code/name:", parent=self.root)
        if not u:
            return
        v = simpledialog.askstring("Route - to", "Enter destination airport code/name:", parent=self.root)
        if not v:
            return
        u, v = u.strip(), v.strip()
        if u == v:
            messagebox.showerror("Invalid", "Source and destination cannot be the same.")
            return

        # create nodes if missing
        if u not in self.g.nodes:
            self.g.add_node(u)
            self.log_message(f"Auto-added airport: {u}")
        if v not in self.g.nodes:
            self.g.add_node(v)
            self.log_message(f"Auto-added airport: {v}")

        # ask for numeric attributes
        try:
            dist = float(simpledialog.askstring("Distance", f"Enter distance (km) for {u} - {v}:", parent=self.root))
        except Exception:
            messagebox.showerror("Invalid", "Distance must be numeric.")
            return
        try:
            cost = float(simpledialog.askstring("Cost", f"Enter cost (operational) for {u} - {v}:", parent=self.root))
        except Exception:
            messagebox.showerror("Invalid", "Cost must be numeric.")
            return

        # add/update edge
        self.g.add_edge(u, v, distance=dist, cost=cost)
        self.log_message(f"Added route: {u} <-> {v} (distance={dist}, cost={cost})")

    def remove_route(self):
        u = simpledialog.askstring("Remove Route - from", "Enter source airport:", parent=self.root)
        if not u: return
        v = simpledialog.askstring("Remove Route - to", "Enter destination airport:", parent=self.root)
        if not v: return
        u, v = u.strip(), v.strip()
        if self.g.has_edge(u, v):
            self.g.remove_edge(u, v)
            self.log_message(f"Removed route: {u} - {v}")
        else:
            messagebox.showerror("Not found", f"No route exists between {u} and {v}.")

    def clear_graph(self):
        if messagebox.askyesno("Confirm", "Clear entire graph?"):
            self.g.clear()
            self.log_message("Cleared graph.")

    # -------------------------
    # Visualization
    # -------------------------
    def show_network(self, with_edge_labels=True):
        if len(self.g.nodes) == 0:
            messagebox.showinfo("Empty", "Graph is empty — add airports and routes first.")
            return
        pos = nx.spring_layout(self.g, seed=42)
        plt.figure()
        nx.draw(self.g, pos, with_labels=True, node_size=700, font_size=9)
        if with_edge_labels:
            # show distance on edges as default label
            labels = {}
            for u, v, data in self.g.edges(data=True):
                d = data.get("distance", data.get("cost", ""))
                labels[(u, v)] = f"{d}"
            nx.draw_networkx_edge_labels(self.g, pos, edge_labels=labels, font_size=8)
        plt.title("Airline Network")
        plt.show()

    # -------------------------
    # Shortest path
    # -------------------------
    def shortest_path_dialog(self):
        if len(self.g.nodes) == 0:
            messagebox.showinfo("Empty", "Graph empty.")
            return
        src = simpledialog.askstring("Shortest Path", "Source airport:", parent=self.root)
        if not src: return
        dst = simpledialog.askstring("Shortest Path", "Destination airport:", parent=self.root)
        if not dst: return
        metric = simpledialog.askstring("Metric", "Metric to optimize ('distance' or 'cost'):", initialvalue="distance", parent=self.root)
        if not metric: metric = "distance"
        metric = metric.strip().lower()
        if metric not in ("distance", "cost"):
            messagebox.showerror("Invalid", "Metric must be 'distance' or 'cost'.")
            return
        try:
            path, total = self.compute_shortest_path(src.strip(), dst.strip(), metric)
            self.log_message(f"Shortest path ({metric}) {src} -> {dst}: {path} with total {metric} = {total}")
            # show path subgraph
            self.show_path_subgraph(path)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def compute_shortest_path(self, source, target, metric="distance"):
        if source not in self.g.nodes or target not in self.g.nodes:
            raise ValueError("Source or target airport not in graph.")
        # ensure edges have metric; otherwise default to 1
        for u, v, data in self.g.edges(data=True):
            if metric not in data:
                data[metric] = 1.0
        path = nx.shortest_path(self.g, source=source, target=target, weight=metric)
        total = 0.0
        for a, b in zip(path[:-1], path[1:]):
            total += float(self.g.edges[a, b].get(metric, 1.0))
        return path, total

    def show_path_subgraph(self, path_nodes):
        sub = self.g.subgraph(path_nodes)
        pos = nx.spring_layout(self.g, seed=42)
        plt.figure()
        nx.draw(self.g, pos, with_labels=True, node_size=600, alpha=0.3)
        nx.draw(sub, pos, with_labels=True, node_size=700, edge_color="r", width=2)
        plt.title("Highlighted Path (red)")
        plt.show()

    # -------------------------
    # Minimum Spanning Tree
    # -------------------------
    def show_mst(self):
        if len(self.g.nodes) == 0:
            messagebox.showinfo("Empty", "Graph empty.")
            return
        # use cost as primary metric; fallback to distance
        weight_attr = "cost" if any("cost" in d for _, _, d in self.g.edges(data=True)) else "distance"
        if not any(weight_attr in d for _, _, d in self.g.edges(data=True)):
            # if none have attributes, assign 1
            for u, v in self.g.edges():
                self.g.edges[u, v][weight_attr] = 1.0
        mst = nx.minimum_spanning_tree(self.g, weight=weight_attr)
        total_weight = sum(float(d.get(weight_attr, 0)) for _, _, d in mst.edges(data=True))
        self.log_message(f"Minimum Spanning Tree (by {weight_attr}) total {weight_attr} = {total_weight}")
        # show MST
        pos = nx.spring_layout(self.g, seed=42)
        plt.figure()
        nx.draw(self.g, pos, with_labels=True, node_size=600, alpha=0.2)
        nx.draw(mst, pos, with_labels=True, node_size=700, edge_color="g", width=2)
        edge_labels = {(u, v): f"{d.get(weight_attr)}" for u, v, d in mst.edges(data=True)}
        nx.draw_networkx_edge_labels(mst, pos, edge_labels=edge_labels)
        plt.title(f"Minimum Spanning Tree (weight={weight_attr})")
        plt.show()

    # -------------------------
    # TSP heuristic: Nearest Neighbor
    # -------------------------
    def tsp_dialog(self):
        if len(self.g.nodes) < 2:
            messagebox.showinfo("Too small", "Need at least 2 airports.")
            return
        start = simpledialog.askstring("TSP", "Start airport for route (leave blank to use any):", parent=self.root)
        try:
            route, cost = self.nearest_neighbor_tsp(start.strip() if start else None, weight="distance")
            self.log_message(f"TSP route (nearest neighbor) start={start or 'auto'}: {route} total distance={cost}")
            self.show_path_subgraph(route)
        except Exception as e:
            messagebox.showerror("TSP Error", str(e))

    def nearest_neighbor_tsp(self, start=None, weight="distance"):
        # build complete graph distances (use shortest path distances between nodes as metric)
        nodes = list(self.g.nodes)
        if start and start not in nodes:
            raise ValueError("Start node not in graph.")
        n = len(nodes)
        # precompute shortest path distances between every pair
        dist_matrix = {}
        for u in nodes:
            for v in nodes:
                if u == v:
                    dist_matrix[(u, v)] = 0.0
                else:
                    try:
                        _, d = self.compute_shortest_path(u, v, metric=weight)
                        dist_matrix[(u, v)] = d
                    except Exception:
                        # if no path, set a very large cost
                        dist_matrix[(u, v)] = float("inf")
        # pick start
        if start is None:
            start = nodes[0]
        route = [start]
        unvisited = set(nodes)
        unvisited.remove(start)
        total = 0.0
        current = start
        while unvisited:
            # choose nearest unvisited
            nearest = min(unvisited, key=lambda x: dist_matrix[(current, x)])
            d = dist_matrix[(current, nearest)]
            if d == float("inf"):
                raise ValueError("Graph is disconnected; cannot complete TSP route.")
            route.append(nearest)
            total += d
            unvisited.remove(nearest)
            current = nearest
        # return to start
        back = dist_matrix[(current, start)]
        if back == float("inf"):
            raise ValueError("Graph is disconnected; cannot return to start.")
        route.append(start)
        total += back
        return route, total

    # -------------------------
    # Load / Save network CSV
    # -------------------------
    def load_network_csv(self):
        file = filedialog.askopenfilename(title="Select routes CSV",
                                          filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not file:
            return
        try:
            df = pd.read_csv(file)
            # expect columns: source,destination,distance,cost (distance and cost optional)
            required = {"source", "destination"}
            if not required.issubset(set(df.columns.str.lower())):
                messagebox.showerror("Invalid CSV", "CSV must have 'source' and 'destination' columns.")
                return
            # clear current graph
            self.g.clear()
            for _, row in df.iterrows():
                u = str(row.get("source") or row.get("Source") or row.get("SOURCE"))
                v = str(row.get("destination") or row.get("Destination") or row.get("DESTINATION"))
                if pd.isna(u) or pd.isna(v):
                    continue
                u, v = u.strip(), v.strip()
                dist = None
                cost = None
                if "distance" in df.columns:
                    try:
                        dist = float(row["distance"])
                    except Exception:
                        dist = None
                if "cost" in df.columns:
                    try:
                        cost = float(row["cost"])
                    except Exception:
                        cost = None
                # add nodes and edge
                self.g.add_node(u)
                self.g.add_node(v)
                kwargs = {}
                if dist is not None: kwargs["distance"] = dist
                if cost is not None: kwargs["cost"] = cost
                self.g.add_edge(u, v, **kwargs)
            self.log_message(f"Loaded network from {os.path.basename(file)} with {len(self.g.nodes)} airports and {len(self.g.edges)} routes.")
        except Exception as e:
            messagebox.showerror("Load Error", str(e))

    def save_network_csv(self):
        if len(self.g.edges) == 0:
            messagebox.showinfo("Nothing", "No routes to save.")
            return
        file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")], title="Save routes as CSV")
        if not file:
            return
        rows = []
        for u, v, d in self.g.edges(data=True):
            rows.append({
                "source": u,
                "destination": v,
                "distance": d.get("distance", ""),
                "cost": d.get("cost", "")
            })
        df = pd.DataFrame(rows)
        df.to_csv(file, index=False)
        self.log_message(f"Saved network to {os.path.basename(file)}")

# -------------------------
# Run App
# -------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = AirlineRouteOptimizer(root)
    root.mainloop()

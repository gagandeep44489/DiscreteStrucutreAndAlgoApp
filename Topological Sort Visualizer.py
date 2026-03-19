import math
import tkinter as tk
from tkinter import messagebox


class TopologicalSortVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Topological Sort Visualizer")
        self.root.geometry("1000x650")

        self.graph = {}
        self.last_topological_order = []

        self._build_ui()

    def _build_ui(self):
        left = tk.Frame(self.root, padx=10, pady=10)
        left.pack(side=tk.LEFT, fill=tk.Y)

        right = tk.Frame(self.root, padx=10, pady=10)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(
            left,
            text=(
                "Nodes (optional, comma-separated)\n"
                "Example: A,B,C,D"
            ),
            justify="left",
        ).pack(anchor="w")
        self.nodes_entry = tk.Entry(left, width=45)
        self.nodes_entry.pack(pady=(3, 10))

        tk.Label(
            left,
            text=(
                "Directed edges (one per line)\n"
                "Format: A->B"
            ),
            justify="left",
        ).pack(anchor="w")

        self.edges_text = tk.Text(left, width=45, height=14)
        self.edges_text.pack()
        self.edges_text.insert(
            "1.0",
            "A->C\nB->C\nB->D\nC->E\nD->F\nE->F",
        )

        button_row = tk.Frame(left)
        button_row.pack(fill=tk.X, pady=10)

        tk.Button(button_row, text="Visualize", command=self.visualize, width=14).pack(
            side=tk.LEFT, padx=(0, 8)
        )
        tk.Button(button_row, text="Clear", command=self.clear_all, width=14).pack(
            side=tk.LEFT
        )

        tk.Label(left, text="Topological Order:").pack(anchor="w")
        self.order_var = tk.StringVar(value="-")
        tk.Label(
            left,
            textvariable=self.order_var,
            wraplength=320,
            justify="left",
            fg="#0B5FBA",
        ).pack(anchor="w", pady=(0, 10))

        tk.Label(left, text="Step-by-step queue processing:").pack(anchor="w")
        self.steps_listbox = tk.Listbox(left, width=50, height=11)
        self.steps_listbox.pack(fill=tk.BOTH, expand=False)

        self.canvas = tk.Canvas(right, bg="white", highlightthickness=1, highlightbackground="#ccc")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.legend = tk.Label(
            right,
            text="Green: zero in-degree at start   |   Blue border: selected in topological order",
            anchor="w",
        )
        self.legend.pack(fill=tk.X, pady=(8, 0))

    @staticmethod
    def _parse_nodes(raw_nodes):
        nodes = []
        seen = set()
        for part in raw_nodes.split(","):
            node = part.strip()
            if node and node not in seen:
                seen.add(node)
                nodes.append(node)
        return nodes

    @staticmethod
    def _parse_edges(raw_edges):
        edges = []
        for idx, line in enumerate(raw_edges.splitlines(), start=1):
            text = line.strip()
            if not text:
                continue
            if "->" not in text:
                raise ValueError(f"Invalid edge format at line {idx}: '{text}'. Use A->B")
            left, right = text.split("->", 1)
            src = left.strip()
            dst = right.strip()
            if not src or not dst:
                raise ValueError(f"Invalid edge format at line {idx}: '{text}'. Use A->B")
            edges.append((src, dst))
        return edges

    def _build_graph(self, nodes, edges):
        graph = {n: [] for n in nodes}
        for src, dst in edges:
            if src not in graph:
                graph[src] = []
            if dst not in graph:
                graph[dst] = []
            graph[src].append(dst)
        return graph

    def _kahn_topological_sort(self, graph):
        indegree = {node: 0 for node in graph}
        for src in graph:
            for dst in graph[src]:
                indegree[dst] += 1

        queue = sorted([node for node, deg in indegree.items() if deg == 0])
        initial_zero = set(queue)
        steps = [f"Start queue (in-degree 0): {queue if queue else '[]'}"]

        order = []
        while queue:
            node = queue.pop(0)
            order.append(node)
            steps.append(f"Pop '{node}' -> order: {order}")

            for neighbor in sorted(graph[node]):
                indegree[neighbor] -= 1
                if indegree[neighbor] == 0:
                    queue.append(neighbor)
                    queue.sort()
                    steps.append(
                        f"  Decrease in-degree('{neighbor}') to 0; enqueue -> queue: {queue}"
                    )
                else:
                    steps.append(
                        f"  Decrease in-degree('{neighbor}') to {indegree[neighbor]}"
                    )

        is_dag = len(order) == len(graph)
        if not is_dag:
            remaining = [n for n in graph if n not in order]
            steps.append(f"Cycle detected. Remaining nodes not processed: {remaining}")

        return order, steps, indegree, initial_zero, is_dag

    def _compute_levels(self, graph, order):
        level = {node: 0 for node in graph}
        for node in order:
            for nei in graph[node]:
                level[nei] = max(level[nei], level[node] + 1)
        grouped = {}
        for node, lv in level.items():
            grouped.setdefault(lv, []).append(node)
        for lv in grouped:
            grouped[lv].sort()
        return grouped

    def _draw_arrow(self, x1, y1, x2, y2):
        self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, width=1.6, fill="#555")

    def _draw_graph(self, graph, order, initial_zero, is_dag):
        self.canvas.delete("all")
        w = max(self.canvas.winfo_width(), 700)
        h = max(self.canvas.winfo_height(), 500)

        positions = {}

        if is_dag and order:
            levels = self._compute_levels(graph, order)
            max_level = max(levels.keys()) if levels else 0
            x_gap = (w - 140) / max(max_level, 1)

            for lv in sorted(levels.keys()):
                nodes = levels[lv]
                y_gap = h / (len(nodes) + 1)
                x = 70 + lv * x_gap
                for i, node in enumerate(nodes, start=1):
                    positions[node] = (x, i * y_gap)
        else:
            nodes = sorted(graph.keys())
            if nodes:
                cx, cy = w / 2, h / 2
                radius = min(w, h) * 0.35
                for i, node in enumerate(nodes):
                    angle = (2 * math.pi * i) / len(nodes)
                    positions[node] = (
                        cx + radius * math.cos(angle),
                        cy + radius * math.sin(angle),
                    )

        for src in graph:
            for dst in graph[src]:
                if src in positions and dst in positions:
                    x1, y1 = positions[src]
                    x2, y2 = positions[dst]
                    self._draw_arrow(x1, y1, x2, y2)

        order_index = {node: i for i, node in enumerate(order)}
        for node, (x, y) in positions.items():
            r = 24
            fill = "#D7F7D2" if node in initial_zero else "#EAF1FF"
            outline = "#1E6BE0" if node in order_index else "#8E8E8E"
            width = 3 if node in order_index else 2

            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=fill, outline=outline, width=width)
            self.canvas.create_text(x, y, text=node, font=("Arial", 11, "bold"))

            if node in order_index:
                self.canvas.create_text(x, y + 36, text=f"#{order_index[node] + 1}", fill="#0B5FBA")

    def clear_all(self):
        self.nodes_entry.delete(0, tk.END)
        self.edges_text.delete("1.0", tk.END)
        self.order_var.set("-")
        self.steps_listbox.delete(0, tk.END)
        self.canvas.delete("all")

    def visualize(self):
        raw_nodes = self.nodes_entry.get().strip()
        raw_edges = self.edges_text.get("1.0", tk.END).strip()

        try:
            nodes = self._parse_nodes(raw_nodes)
            edges = self._parse_edges(raw_edges)

            if not nodes and not edges:
                raise ValueError("Please provide nodes or edges to visualize.")

            self.graph = self._build_graph(nodes, edges)
            order, steps, _, initial_zero, is_dag = self._kahn_topological_sort(self.graph)
            self.last_topological_order = order

            if is_dag:
                self.order_var.set(" -> ".join(order) if order else "(Empty graph)")
            else:
                self.order_var.set("No valid topological order (cycle detected)")

            self.steps_listbox.delete(0, tk.END)
            for line in steps:
                self.steps_listbox.insert(tk.END, line)

            self._draw_graph(self.graph, order, initial_zero, is_dag)

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = TopologicalSortVisualizer(root)
    root.mainloop()
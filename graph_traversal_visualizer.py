import tkinter as tk
from tkinter import messagebox
import time

class GraphTraversalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Traversal Visualizer (DFS & BFS)")
        self.root.geometry("900x600")
        self.root.configure(bg="#f7f7f7")

        self.canvas = tk.Canvas(self.root, width=700, height=550, bg="white")
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)

        frame = tk.Frame(self.root, bg="#f7f7f7")
        frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        # Data
        self.nodes = []
        self.edges = {}
        self.selected_node = None

        # Buttons
        tk.Label(frame, text="Graph Controls", bg="#f7f7f7", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Button(frame, text="Add Node", command=self.add_node_mode, width=20).pack(pady=5)
        tk.Button(frame, text="Add Edge", command=self.add_edge_mode, width=20).pack(pady=5)
        tk.Button(frame, text="Run DFS", command=self.run_dfs, width=20).pack(pady=5)
        tk.Button(frame, text="Run BFS", command=self.run_bfs, width=20).pack(pady=5)
        tk.Button(frame, text="Reset", command=self.reset, width=20).pack(pady=5)

        self.mode = None
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.info_label = tk.Label(frame, text="", bg="#f7f7f7", fg="blue", font=("Arial", 10))
        self.info_label.pack(pady=20)

    def add_node_mode(self):
        self.mode = "node"
        self.info_label.config(text="Click on canvas to add a node")

    def add_edge_mode(self):
        self.mode = "edge"
        self.info_label.config(text="Click two nodes to connect an edge")

    def on_canvas_click(self, event):
        if self.mode == "node":
            node_id = len(self.nodes)
            self.nodes.append((event.x, event.y))
            self.edges[node_id] = []
            self.canvas.create_oval(event.x - 20, event.y - 20, event.x + 20, event.y + 20, fill="#a8dadc")
            self.canvas.create_text(event.x, event.y, text=str(node_id), font=("Arial", 12, "bold"))
        elif self.mode == "edge":
            clicked = self.get_clicked_node(event.x, event.y)
            if clicked is not None:
                if self.selected_node is None:
                    self.selected_node = clicked
                    self.highlight_node(clicked, "yellow")
                else:
                    n1, n2 = self.selected_node, clicked
                    if n1 != n2 and n2 not in self.edges[n1]:
                        self.edges[n1].append(n2)
                        self.edges[n2].append(n1)
                        self.draw_edge(n1, n2)
                    self.highlight_node(self.selected_node, "#a8dadc")
                    self.selected_node = None

    def draw_edge(self, n1, n2):
        x1, y1 = self.nodes[n1]
        x2, y2 = self.nodes[n2]
        self.canvas.create_line(x1, y1, x2, y2, fill="black", width=2)

    def highlight_node(self, node, color):
        x, y = self.nodes[node]
        self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill=color)
        self.canvas.create_text(x, y, text=str(node), font=("Arial", 12, "bold"))

    def get_clicked_node(self, x, y):
        for i, (nx, ny) in enumerate(self.nodes):
            if (nx - x) ** 2 + (ny - y) ** 2 <= 400:  # within radius 20
                return i
        return None

    def reset(self):
        self.canvas.delete("all")
        self.nodes.clear()
        self.edges.clear()
        self.selected_node = None
        self.mode = None
        self.info_label.config(text="Graph cleared")

    def run_dfs(self):
        if not self.nodes:
            messagebox.showwarning("Warning", "Add some nodes first!")
            return
        start = 0
        visited = set()
        self.info_label.config(text="Running DFS...")
        self.dfs_visual(start, visited)
        self.info_label.config(text="DFS Complete!")

    def dfs_visual(self, node, visited):
        visited.add(node)
        self.highlight_node(node, "#ffb703")
        self.root.update()
        time.sleep(0.5)
        for neighbor in self.edges[node]:
            if neighbor not in visited:
                self.dfs_visual(neighbor, visited)
        self.highlight_node(node, "#219ebc")
        self.root.update()

    def run_bfs(self):
        if not self.nodes:
            messagebox.showwarning("Warning", "Add some nodes first!")
            return
        start = 0
        visited = {start}
        queue = [start]
        self.info_label.config(text="Running BFS...")
        while queue:
            current = queue.pop(0)
            self.highlight_node(current, "#ffafcc")
            self.root.update()
            time.sleep(0.5)
            for neighbor in self.edges[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        self.info_label.config(text="BFS Complete!")

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphTraversalApp(root)
    root.mainloop()

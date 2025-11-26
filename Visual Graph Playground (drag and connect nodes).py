import tkinter as tk
from tkinter import messagebox, filedialog
import json
import math

class VisualGraphPlayground:

    def __init__(self, root):
        self.root = root
        self.root.title("Visual Graph Playground – Drag & Connect Nodes")

        # Canvas
        self.canvas = tk.Canvas(root, width=900, height=600, bg="white")
        self.canvas.pack(fill="both", expand=True)

        # Graph data
        self.nodes = {}          # node_id : (x, y)
        self.edges = []          # list of (node1, node2)
        self.node_radius = 22

        # Dragging variables
        self.dragging_node = None

        # UI Buttons
        frame = tk.Frame(root)
        frame.pack()

        tk.Button(frame, text="Add Node", command=self.add_node).grid(row=0, column=0)
        tk.Button(frame, text="Clear All", command=self.clear_graph).grid(row=0, column=1)
        tk.Button(frame, text="Save Graph", command=self.save_graph).grid(row=0, column=2)
        tk.Button(frame, text="Load Graph", command=self.load_graph).grid(row=0, column=3)

        # Canvas Events
        self.canvas.bind("<Button-1>", self.canvas_click)
        self.canvas.bind("<B1-Motion>", self.drag_node)
        self.canvas.bind("<ButtonRelease-1>", self.release_node)

        # Show help popup ONCE
        self.show_help_popup()

    # ---------------------------- HELP POPUP ----------------------------
    def show_help_popup(self):
        messagebox.showinfo(
            "How to Use",
            "Left Click = Select / Move Node\n"
            "Click empty area = Add Node (or use button)\n"
            "Drag Node = Move it\n"
            "Drag from one node to another = Connect Edge\n"
            "Right Click Node = Delete Node\n"
            "Right Click Edge line = Delete Edge\n"
            "Use Save / Load buttons to save or restore graphs"
        )

    # ---------------------------- NODE MANAGEMENT ----------------------------
    def add_node(self, x=None, y=None):
        if x is None or y is None:
            x = 100 + len(self.nodes) * 40
            y = 100 + len(self.nodes) * 20

        node_id = f"N{len(self.nodes)+1}"
        self.nodes[node_id] = (x, y)
        self.draw_graph()

    def delete_node(self, node_id):
        self.nodes.pop(node_id)
        self.edges = [
            (u, v) for (u, v) in self.edges if u != node_id and v != node_id
        ]
        self.draw_graph()

    # ---------------------------- EDGE MANAGEMENT ----------------------------
    def add_edge(self, n1, n2):
        if n1 != n2 and (n1, n2) not in self.edges and (n2, n1) not in self.edges:
            self.edges.append((n1, n2))
        self.draw_graph()

    def delete_edge(self, edge):
        self.edges.remove(edge)
        self.draw_graph()

    # ---------------------------- GRAPH DRAWING ----------------------------
    def draw_graph(self):
        self.canvas.delete("all")

        # Draw Edges First
        for (u, v) in self.edges:
            x1, y1 = self.nodes[u]
            x2, y2 = self.nodes[v]
            line = self.canvas.create_line(x1, y1, x2, y2, width=3, fill="gray")
            self.canvas.tag_bind(line, "<Button-3>", lambda e, edge=(u, v): self.delete_edge(edge))

        # Draw Nodes
        for node_id, (x, y) in self.nodes.items():
            oval = self.canvas.create_oval(
                x - self.node_radius, y - self.node_radius,
                x + self.node_radius, y + self.node_radius,
                fill="skyblue", outline="black", width=2
            )

            text = self.canvas.create_text(x, y, text=node_id)

            # Bind right-click to delete node
            self.canvas.tag_bind(oval, "<Button-3>", lambda e, nid=node_id: self.delete_node(nid))
            self.canvas.tag_bind(text, "<Button-3>", lambda e, nid=node_id: self.delete_node(nid))

    # ---------------------------- INTERACTION ----------------------------
    def canvas_click(self, event):
        clicked_node = self.get_node_at(event.x, event.y)

        if clicked_node:
            self.dragging_node = clicked_node
        else:
            self.add_node(event.x, event.y)

    def drag_node(self, event):
        if self.dragging_node:
            self.nodes[self.dragging_node] = (event.x, event.y)
            self.draw_graph()

    def release_node(self, event):
        if not self.dragging_node:
            return

        release_on = self.get_node_at(event.x, event.y)

        if release_on and release_on != self.dragging_node:
            self.add_edge(self.dragging_node, release_on)

        self.dragging_node = None

    # ---------------------------- NODE DETECTION ----------------------------
    def get_node_at(self, x, y):
        for node_id, (nx, ny) in self.nodes.items():
            if math.dist((x, y), (nx, ny)) <= self.node_radius:
                return node_id
        return None

    # ---------------------------- SAVE / LOAD ----------------------------
    def save_graph(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json")
        if not file_path:
            return

        data = {"nodes": self.nodes, "edges": self.edges}

        with open(file_path, "w") as f:
            json.dump(data, f)

        messagebox.showinfo("Saved", "Graph saved successfully!")

    def load_graph(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not file_path:
            return

        with open(file_path, "r") as f:
            data = json.load(f)

        self.nodes = {k: tuple(v) for k, v in data["nodes"].items()}
        self.edges = data["edges"]

        self.draw_graph()

    # ---------------------------- CLEAR GRAPH ----------------------------
    def clear_graph(self):
        self.nodes.clear()
        self.edges.clear()
        self.draw_graph()


# ---------------------------- MAIN ----------------------------
def main():
    root = tk.Tk()
    app = VisualGraphPlayground(root)
    root.mainloop()

if __name__ == "__main__":
    main()

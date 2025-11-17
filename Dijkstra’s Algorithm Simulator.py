import tkinter as tk
from tkinter import messagebox, scrolledtext
import heapq


# ------------------- Dijkstra Function -------------------
def dijkstra(graph, start):
    distances = {node: float("inf") for node in graph}
    distances[start] = 0

    pq = [(0, start)]
    steps = []

    while pq:
        current_distance, current_node = heapq.heappop(pq)

        if current_distance > distances[current_node]:
            continue

        steps.append(f"Visiting: {current_node} (distance = {current_distance})")

        for neighbor, weight in graph[current_node].items():
            steps.append(f"  Checking {neighbor} with weight {weight}")

            distance = current_distance + weight

            if distance < distances[neighbor]:
                steps.append(f"    Updated {neighbor}: {distances[neighbor]} → {distance}")
                distances[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor))
            else:
                steps.append(f"    No update needed")

    return distances, steps


# ------------------- GUI App -------------------
class DijkstraApp:
    def __init__(self, root):
        self.root = root
        root.title("Dijkstra Algorithm Simulator")
        root.geometry("700x600")

        # Input fields
        tk.Label(root, text="Enter edges (Format: A B 4)").pack()
        self.edge_entry = tk.Entry(root, width=40)
        self.edge_entry.pack()

        self.add_button = tk.Button(root, text="Add Edge", command=self.add_edge)
        self.add_button.pack()

        # Show edges
        tk.Label(root, text="Graph Edges:").pack()
        self.edge_list_box = scrolledtext.ScrolledText(root, width=50, height=7)
        self.edge_list_box.pack()

        tk.Label(root, text="Start Node:").pack()
        self.start_entry = tk.Entry(root, width=10)
        self.start_entry.pack()

        tk.Button(root, text="Run Dijkstra", command=self.run_dijkstra).pack()

        # Output areas
        tk.Label(root, text="Steps:").pack()
        self.steps_box = scrolledtext.ScrolledText(root, width=80, height=15)
        self.steps_box.pack()

        tk.Label(root, text="Shortest Distances:").pack()
        self.result_box = scrolledtext.ScrolledText(root, width=40, height=7)
        self.result_box.pack()

        self.graph = {}

    # Add edges to graph
    def add_edge(self):
        text = self.edge_entry.get().strip()

        try:
            u, v, w = text.split()
            w = int(w)

            if u not in self.graph:
                self.graph[u] = {}
            if v not in self.graph:
                self.graph[v] = {}

            self.graph[u][v] = w
            self.graph[v][u] = w  # Undirected graph

            self.edge_list_box.insert(tk.END, f"{u} -- {v} (weight {w})\n")
            self.edge_entry.delete(0, tk.END)

        except:
            messagebox.showerror("Error", "Enter edge in correct format: A B 5")

    # Run Dijkstra and display result
    def run_dijkstra(self):
        start = self.start_entry.get().strip()

        if start not in self.graph:
            messagebox.showerror("Error", "Start node not found in graph!")
            return

        distances, steps = dijkstra(self.graph, start)

        # Clear boxes
        self.steps_box.delete(1.0, tk.END)
        self.result_box.delete(1.0, tk.END)

        # Show steps
        for s in steps:
            self.steps_box.insert(tk.END, s + "\n")

        # Show final distances
        for node, dist in distances.items():
            self.result_box.insert(tk.END, f"{node}: {dist}\n")


# ------------------- Run Application -------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = DijkstraApp(root)
    root.mainloop()

import tkinter as tk
from tkinter import messagebox

class DSU:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Path Compression
        return self.parent[x]

    def union(self, x, y):
        rootX = self.find(x)
        rootY = self.find(y)

        if rootX != rootY:
            if self.rank[rootX] < self.rank[rootY]:
                self.parent[rootX] = rootY
            elif self.rank[rootX] > self.rank[rootY]:
                self.parent[rootY] = rootX
            else:
                self.parent[rootY] = rootX
                self.rank[rootX] += 1


class DSUDemoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Disjoint Set Union (DSU) Demo")
        self.root.geometry("700x500")

        self.dsu = None

        self.create_widgets()

    def create_widgets(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        tk.Label(top_frame, text="Number of Elements:").grid(row=0, column=0, padx=5)
        self.size_entry = tk.Entry(top_frame)
        self.size_entry.grid(row=0, column=1, padx=5)

        tk.Button(top_frame, text="Initialize", command=self.initialize_dsu).grid(row=0, column=2, padx=10)

        action_frame = tk.Frame(self.root)
        action_frame.pack(pady=10)

        tk.Label(action_frame, text="Element 1:").grid(row=0, column=0)
        self.elem1_entry = tk.Entry(action_frame, width=5)
        self.elem1_entry.grid(row=0, column=1)

        tk.Label(action_frame, text="Element 2:").grid(row=0, column=2)
        self.elem2_entry = tk.Entry(action_frame, width=5)
        self.elem2_entry.grid(row=0, column=3)

        tk.Button(action_frame, text="Union", command=self.perform_union).grid(row=0, column=4, padx=10)
        tk.Button(action_frame, text="Find", command=self.perform_find).grid(row=0, column=5, padx=10)

        self.output_text = tk.Text(self.root, height=15, width=80)
        self.output_text.pack(pady=10)

    def initialize_dsu(self):
        try:
            n = int(self.size_entry.get())
            if n <= 0:
                raise ValueError
            self.dsu = DSU(n)
            self.output_text.insert(tk.END, f"Initialized DSU with {n} elements\n")
            self.display_state()
        except ValueError:
            messagebox.showerror("Input Error", "Enter a valid positive integer.")

    def perform_union(self):
        if not self.dsu:
            messagebox.showwarning("Warning", "Initialize DSU first.")
            return
        try:
            x = int(self.elem1_entry.get())
            y = int(self.elem2_entry.get())
            self.dsu.union(x, y)
            self.output_text.insert(tk.END, f"Union({x}, {y}) performed\n")
            self.display_state()
        except:
            messagebox.showerror("Input Error", "Enter valid element indices.")

    def perform_find(self):
        if not self.dsu:
            messagebox.showwarning("Warning", "Initialize DSU first.")
            return
        try:
            x = int(self.elem1_entry.get())
            root = self.dsu.find(x)
            self.output_text.insert(tk.END, f"Find({x}) → Root: {root}\n")
            self.display_state()
        except:
            messagebox.showerror("Input Error", "Enter a valid element index.")

    def display_state(self):
        if self.dsu:
            self.output_text.insert(tk.END, f"Parent Array: {self.dsu.parent}\n")
            self.output_text.insert(tk.END, f"Rank Array: {self.dsu.rank}\n\n")
            self.output_text.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = DSUDemoApp(root)
    root.mainloop()
import math
import tkinter as tk
from tkinter import messagebox, ttk


class HeapConstructionSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Heap Construction Simulator")
        self.root.geometry("1000x720")
        self.root.minsize(900, 650)

        self.snapshots = []
        self.current_step = 0

        self.create_widgets()

    def create_widgets(self):
        title = tk.Label(
            self.root,
            text="Heap Construction Simulator",
            font=("Arial", 18, "bold"),
        )
        title.pack(pady=10)

        controls = tk.Frame(self.root)
        controls.pack(fill="x", padx=12)

        tk.Label(controls, text="Input Values (comma separated):").grid(row=0, column=0, sticky="w")
        self.input_entry = tk.Entry(controls, width=60)
        self.input_entry.grid(row=0, column=1, columnspan=4, padx=8, pady=4, sticky="w")

        tk.Label(controls, text="Heap Type:").grid(row=1, column=0, sticky="w")
        self.heap_type = tk.StringVar(value="Max Heap")
        ttk.Combobox(
            controls,
            textvariable=self.heap_type,
            state="readonly",
            values=["Max Heap", "Min Heap"],
            width=18,
        ).grid(row=1, column=1, sticky="w", padx=8)

        tk.Label(controls, text="Construction Method:").grid(row=1, column=2, sticky="e")
        self.method = tk.StringVar(value="Bottom-up Heapify")
        ttk.Combobox(
            controls,
            textvariable=self.method,
            state="readonly",
            values=["Bottom-up Heapify", "Insertion (Top-down)"],
            width=24,
        ).grid(row=1, column=3, sticky="w", padx=8)

        tk.Button(controls, text="Simulate", command=self.simulate, width=12).grid(row=1, column=4, padx=8)
        tk.Button(controls, text="Reset", command=self.reset, width=10).grid(row=1, column=5, padx=8)

        nav = tk.Frame(self.root)
        nav.pack(fill="x", padx=12, pady=8)

        self.prev_btn = tk.Button(nav, text="◀ Previous", command=self.previous_step, state="disabled")
        self.prev_btn.pack(side="left")

        self.step_label = tk.Label(nav, text="Step: 0/0", font=("Arial", 11, "bold"))
        self.step_label.pack(side="left", padx=14)

        self.next_btn = tk.Button(nav, text="Next ▶", command=self.next_step, state="disabled")
        self.next_btn.pack(side="left")

        self.action_label = tk.Label(nav, text="", fg="#0b4f92", font=("Arial", 11))
        self.action_label.pack(side="left", padx=16)

        self.canvas = tk.Canvas(self.root, bg="#f5f8fc", height=390)
        self.canvas.pack(fill="both", expand=True, padx=12, pady=6)

        log_frame = tk.LabelFrame(self.root, text="Operation Log", padx=8, pady=8)
        log_frame.pack(fill="both", padx=12, pady=(0, 12))

        self.log_text = tk.Text(log_frame, height=8, wrap="word")
        self.log_text.pack(fill="both", expand=True)

    def parse_input(self):
        raw = self.input_entry.get().strip()
        if not raw:
            raise ValueError("Please enter input values.")

        items = [x.strip() for x in raw.split(",") if x.strip()]
        if not items:
            raise ValueError("No valid numbers found.")

        try:
            return [int(v) for v in items]
        except ValueError as exc:
            raise ValueError("Only integer values are allowed.") from exc

    def compare(self, a, b):
        if self.heap_type.get() == "Max Heap":
            return a > b
        return a < b

    def save_snapshot(self, heap, action):
        self.snapshots.append({"heap": heap.copy(), "action": action})

    def sift_down(self, heap, n, i):
        current = i
        while True:
            left = 2 * current + 1
            right = 2 * current + 2
            best = current

            if left < n and self.compare(heap[left], heap[best]):
                best = left
            if right < n and self.compare(heap[right], heap[best]):
                best = right

            if best == current:
                break

            heap[current], heap[best] = heap[best], heap[current]
            self.save_snapshot(heap, f"Swap index {current} with child {best}.")
            current = best

    def build_heap_bottom_up(self, values):
        heap = values.copy()
        self.save_snapshot(heap, "Initial array.")
        n = len(heap)
        for i in range((n // 2) - 1, -1, -1):
            self.save_snapshot(heap, f"Heapify subtree rooted at index {i}.")
            self.sift_down(heap, n, i)
        self.save_snapshot(heap, "Heap construction complete.")

    def build_heap_insertion(self, values):
        heap = []
        self.save_snapshot(heap, "Start with an empty heap.")

        for value in values:
            heap.append(value)
            i = len(heap) - 1
            self.save_snapshot(heap, f"Insert value {value} at index {i}.")

            while i > 0:
                parent = (i - 1) // 2
                if self.compare(heap[i], heap[parent]):
                    heap[i], heap[parent] = heap[parent], heap[i]
                    self.save_snapshot(heap, f"Bubble up: swap index {i} with parent {parent}.")
                    i = parent
                else:
                    break
        self.save_snapshot(heap, "Heap construction complete.")

    def simulate(self):
        try:
            values = self.parse_input()
        except ValueError as err:
            messagebox.showerror("Input Error", str(err))
            return

        self.snapshots = []
        self.current_step = 0

        if self.method.get() == "Bottom-up Heapify":
            self.build_heap_bottom_up(values)
        else:
            self.build_heap_insertion(values)

        self.log_text.delete("1.0", tk.END)
        for idx, snap in enumerate(self.snapshots, start=1):
            self.log_text.insert(tk.END, f"Step {idx}: {snap['action']}  Heap: {snap['heap']}\n")

        self.prev_btn.config(state="normal")
        self.next_btn.config(state="normal")
        self.render_snapshot(0)

    def render_snapshot(self, step):
        if not self.snapshots:
            return

        self.current_step = step
        snapshot = self.snapshots[step]
        heap = snapshot["heap"]

        self.step_label.config(text=f"Step: {step + 1}/{len(self.snapshots)}")
        self.action_label.config(text=snapshot["action"])

        self.canvas.delete("all")
        if not heap:
            self.canvas.create_text(450, 180, text="Heap is empty", font=("Arial", 14), fill="#555")
            return

        width = max(self.canvas.winfo_width(), 850)
        levels = math.ceil(math.log2(len(heap) + 1))
        vertical_gap = min(80, max(55, 360 // max(levels, 1)))

        positions = {}
        for i, value in enumerate(heap):
            level = int(math.log2(i + 1))
            index_in_level = i - (2**level - 1)
            nodes_in_level = 2**level

            x_gap = width / (nodes_in_level + 1)
            x = (index_in_level + 1) * x_gap
            y = 50 + level * vertical_gap
            positions[i] = (x, y)

            if i > 0:
                parent = (i - 1) // 2
                px, py = positions[parent]
                self.canvas.create_line(px, py + 20, x, y - 20, fill="#7a8ca6", width=2)

            self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill="#4f81bd", outline="")
            self.canvas.create_text(x, y, text=str(value), fill="white", font=("Arial", 10, "bold"))

        self.canvas.create_text(
            12,
            12,
            anchor="nw",
            text=f"Array Representation: {heap}",
            font=("Consolas", 11),
            fill="#1f2d3d",
        )

    def next_step(self):
        if self.current_step < len(self.snapshots) - 1:
            self.render_snapshot(self.current_step + 1)

    def previous_step(self):
        if self.current_step > 0:
            self.render_snapshot(self.current_step - 1)

    def reset(self):
        self.input_entry.delete(0, tk.END)
        self.snapshots = []
        self.current_step = 0
        self.step_label.config(text="Step: 0/0")
        self.action_label.config(text="")
        self.prev_btn.config(state="disabled")
        self.next_btn.config(state="disabled")
        self.canvas.delete("all")
        self.log_text.delete("1.0", tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = HeapConstructionSimulator(root)
    root.mainloop()
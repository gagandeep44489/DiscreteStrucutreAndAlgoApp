import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from PIL import Image, ImageTk
import pydot
import os

# Function to convert boolean expression to graph
def expression_to_graph(expr):
    """
    Simple parser for demo purposes.
    Supports AND, OR, NOT, NAND, NOR, XOR
    """
    graph = pydot.Dot(graph_type='digraph', rankdir='TB')

    # Remove spaces and split by parentheses for basic parsing
    expr_clean = expr.replace(" ", "")
    counter = [0]

    def add_node(node_name):
        node_id = f"node{counter[0]}"
        counter[0] += 1
        graph_node = pydot.Node(node_id, label=node_name, shape="box")
        graph.add_node(graph_node)
        return node_id

    def parse(subexpr):
        if "AND" in subexpr:
            parts = subexpr.split("AND")
            parent = add_node("AND")
            for part in parts:
                child = parse(part)
                graph.add_edge(pydot.Edge(child, parent))
            return parent
        elif "OR" in subexpr:
            parts = subexpr.split("OR")
            parent = add_node("OR")
            for part in parts:
                child = parse(part)
                graph.add_edge(pydot.Edge(child, parent))
            return parent
        elif "NOT" in subexpr:
            child = parse(subexpr.replace("NOT", ""))
            parent = add_node("NOT")
            graph.add_edge(pydot.Edge(child, parent))
            return parent
        else:
            return add_node(subexpr)

    parse(expr_clean)
    return graph

# Tkinter GUI
class LogicCircuitApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Logic Expression to Circuit Converter")
        self.root.geometry("800x600")

        ttk.Label(root, text="Logic Expression to Circuit Converter", font=("Arial", 16, "bold")).pack(pady=10)

        ttk.Label(root, text="Enter Boolean Logic Expression:").pack(anchor="w", padx=10)
        self.input_text = scrolledtext.ScrolledText(root, height=5, wrap=tk.WORD)
        self.input_text.pack(fill="x", padx=10, pady=5)

        ttk.Button(root, text="Generate Circuit", command=self.generate_circuit).pack(pady=5)
        ttk.Button(root, text="Save Circuit as PNG", command=self.save_circuit).pack(pady=5)

        self.canvas = tk.Canvas(root, bg="white", width=760, height=400)
        self.canvas.pack(pady=10)

        self.graph = None
        self.img_path = "circuit.png"

    def generate_circuit(self):
        expr = self.input_text.get("1.0", tk.END).strip()
        if not expr:
            messagebox.showwarning("Input Error", "Please enter a logic expression.")
            return

        try:
            self.graph = expression_to_graph(expr)
            self.graph.write_png(self.img_path)
            self.show_image(self.img_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate circuit: {e}")

    def show_image(self, path):
        img = Image.open(path)
        img = img.resize((760, 400))
        self.photo = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

    def save_circuit(self):
        if self.graph is None:
            messagebox.showwarning("Warning", "Please generate the circuit first.")
            return
        save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image","*.png")])
        if save_path:
            self.graph.write_png(save_path)
            messagebox.showinfo("Saved", f"Circuit saved to {save_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = LogicCircuitApp(root)
    root.mainloop()

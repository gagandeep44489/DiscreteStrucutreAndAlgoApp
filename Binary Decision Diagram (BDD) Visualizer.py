import tkinter as tk
from tkinter import messagebox
from graphviz import Digraph
from boolean import BooleanAlgebra

# Initialize Boolean Algebra
algebra = BooleanAlgebra()

# ---------------- BDD Node ---------------- #
class BDDNode:
    def __init__(self, var, low=None, high=None):
        self.var = var
        self.low = low
        self.high = high

# ---------------- BDD Builder ---------------- #
def build_bdd(expr, variables):
    if expr == algebra.TRUE:
        return "1"
    if expr == algebra.FALSE:
        return "0"

    if not variables:
        return "0"

    var = variables[0]
    low_expr = expr.subs({var: False})
    high_expr = expr.subs({var: True})

    low = build_bdd(low_expr, variables[1:])
    high = build_bdd(high_expr, variables[1:])

    return BDDNode(var, low, high)

# ---------------- Draw BDD ---------------- #
def draw_bdd(dot, node, node_id):
    if node in ["0", "1"]:
        dot.node(node_id, node, shape="box")
        return

    dot.node(node_id, node.var)

    low_id = node_id + "0"
    high_id = node_id + "1"

    draw_bdd(dot, node.low, low_id)
    draw_bdd(dot, node.high, high_id)

    dot.edge(node_id, low_id, label="0")
    dot.edge(node_id, high_id, label="1")

# ---------------- GUI Action ---------------- #
def generate_bdd():
    try:
        expression = entry.get().strip()
        if not expression:
            raise ValueError("Expression is empty")

        expr = algebra.parse(expression)
        variables = sorted(expr.get_symbols(), key=str)

        bdd_root = build_bdd(expr, variables)

        dot = Digraph("BDD", format="png")
        draw_bdd(dot, bdd_root, "root")
        dot.render("bdd_diagram", cleanup=True)

        messagebox.showinfo(
            "Success",
            "BDD generated successfully!\nSaved as bdd_diagram.png"
        )

    except Exception as e:
        messagebox.showerror("Error", str(e))

# ---------------- GUI ---------------- #
root = tk.Tk()
root.title("Binary Decision Diagram (BDD) Visualizer")
root.geometry("420x200")

tk.Label(
    root,
    text="Enter Boolean Expression\nExample: (A & B) | C",
    font=("Arial", 11)
).pack(pady=10)

entry = tk.Entry(root, width=40, font=("Arial", 11))
entry.pack(pady=5)

tk.Button(
    root,
    text="Generate BDD",
    command=generate_bdd,
    bg="#4CAF50",
    fg="white",
    font=("Arial", 11),
    width=18
).pack(pady=15)

root.mainloop()

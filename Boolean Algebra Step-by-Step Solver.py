# Boolean Algebra Step-by-Step Solver
# Author: Gagandeep Singh
# Purpose: Educational / Digital Logic Tool
# Tech Stack: Python, Tkinter

import tkinter as tk
from tkinter import messagebox

class BooleanAlgebraSolver:
    def __init__(self, root):
        self.root = root
        self.root.title("Boolean Algebra Step-by-Step Solver")
        self.root.geometry("700x500")

        self.create_ui()

    def create_ui(self):
        header = tk.Label(self.root, text="Boolean Algebra Step-by-Step Solver", font=("Arial", 16, "bold"))
        header.pack(pady=10)

        tk.Label(self.root, text="Enter Boolean Expression:", font=("Arial", 12)).pack(pady=5)
        self.expr_entry = tk.Entry(self.root, width=50, font=("Arial", 12))
        self.expr_entry.pack(pady=5)

        tk.Button(self.root, text="Solve Step by Step", command=self.solve_expression, font=("Arial", 12)).pack(pady=10)

        self.output_text = tk.Text(self.root, height=20, width=80, font=("Arial", 12))
        self.output_text.pack(pady=10)

    def solve_expression(self):
        expr = self.expr_entry.get().strip()
        if not expr:
            messagebox.showwarning("Input Required", "Please enter a Boolean expression.")
            return

        self.output_text.delete(1.0, tk.END)
        try:
            steps = self.boolean_simplify_steps(expr)
            for i, step in enumerate(steps, 1):
                self.output_text.insert(tk.END, f"Step {i}: {step}\n")
        except Exception as e:
            self.output_text.insert(tk.END, f"Error: {str(e)}")

    def boolean_simplify_steps(self, expr):
        # This is a simplified demonstration of step-by-step simplification
        # Replace AND with *, OR with +, NOT with '
        steps = []
        steps.append(f"Original Expression: {expr}")

        # Step 1: Remove double negation
        simplified = expr.replace("''", "")
        if simplified != expr:
            steps.append(f"Remove double negation: {simplified}")
        else:
            steps.append(f"No double negation to remove")

        # Step 2: Apply basic identities (example simplification)
        simplified = simplified.replace('A*A', 'A')
        simplified = simplified.replace('A+0', 'A')
        simplified = simplified.replace('A+1', '1')
        simplified = simplified.replace('A*1', 'A')
        simplified = simplified.replace('A*0', '0')
        steps.append(f"Apply basic Boolean identities: {simplified}")

        # Step 3: Final simplified result
        steps.append(f"Final Simplified Expression: {simplified}")
        return steps

if __name__ == "__main__":
    root = tk.Tk()
    app = BooleanAlgebraSolver(root)
    root.mainloop()
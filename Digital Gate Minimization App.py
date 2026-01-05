import tkinter as tk
from tkinter import ttk, scrolledtext
from sympy import symbols, simplify_logic
from sympy.logic.boolalg import Or, And

class DigitalGateMinimizationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Digital Gate Minimization App")
        self.root.geometry("700x500")

        self.create_ui()

    def create_ui(self):
        frame = ttk.Frame(self.root, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Digital Gate Minimization Tool", font=("Arial", 14, "bold")).pack(pady=10)

        ttk.Label(frame, text="Enter Boolean Expression (SOP form, e.g., A & B | ~C):").pack(anchor="w")
        self.expr_input = scrolledtext.ScrolledText(frame, height=5)
        self.expr_input.pack(fill=tk.BOTH, expand=True, pady=5)

        ttk.Button(frame, text="Minimize Expression", command=self.minimize_expression).pack(pady=15)

        result_frame = ttk.LabelFrame(frame, text="Result", padding=10)
        result_frame.pack(fill=tk.X, pady=10)

        self.minimized_label = ttk.Label(result_frame, text="Simplified Expression: ")
        self.minimized_label.pack(anchor="w", pady=5)

    def minimize_expression(self):
        expr_text = self.expr_input.get("1.0", tk.END).strip()
        if not expr_text:
            return

        # Identify variables automatically
        var_names = sorted(set([ch for ch in expr_text if ch.isalpha()]))
        var_symbols = symbols(var_names)

        # Map variable names to symbols
        var_dict = {name: sym for name, sym in zip(var_names, var_symbols)}

        # Replace variables in expression string with symbols
        for name, sym in var_dict.items():
            expr_text = expr_text.replace(name, f"var_dict['{name}']")

        try:
            # Evaluate expression string to sympy expression
            expr = eval(expr_text)
            simplified_expr = simplify_logic(expr, form='dnf')  # or form='cnf'
            self.minimized_label.config(text=f"Simplified Expression: {simplified_expr}")
        except Exception as e:
            self.minimized_label.config(text=f"Error: Invalid expression. {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DigitalGateMinimizationApp(root)
    root.mainloop()

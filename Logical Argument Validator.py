import tkinter as tk
from tkinter import ttk, scrolledtext
from sympy import symbols
from sympy.logic.boolalg import Or, And, Not, Implies, Equivalent
from sympy.logic.inference import satisfiable

class LogicalArgumentValidator:
    def __init__(self, root):
        self.root = root
        self.root.title("Logical Argument Validator")
        self.root.geometry("750x550")

        self.create_ui()

    def create_ui(self):
        frame = ttk.Frame(self.root, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Logical Argument Validator", font=("Arial", 14, "bold")).pack(pady=10)

        ttk.Label(frame, text="Enter premises (one per line, e.g., A >> B):").pack(anchor="w")
        self.premises_input = scrolledtext.ScrolledText(frame, height=8)
        self.premises_input.pack(fill=tk.BOTH, expand=True, pady=5)

        ttk.Label(frame, text="Enter conclusion (e.g., A >> C):").pack(anchor="w")
        self.conclusion_input = tk.Entry(frame, width=50)
        self.conclusion_input.pack(fill=tk.X, pady=5)

        ttk.Button(frame, text="Validate Argument", command=self.validate_argument).pack(pady=15)

        self.result_label = ttk.Label(frame, text="Result: ", font=("Arial", 12, "bold"))
        self.result_label.pack(anchor="w", pady=5)

        self.counterexample_label = ttk.Label(frame, text="", wraplength=700)
        self.counterexample_label.pack(anchor="w", pady=5)

    def validate_argument(self):
        premises_text = self.premises_input.get("1.0", tk.END).strip()
        conclusion_text = self.conclusion_input.get().strip()

        if not premises_text or not conclusion_text:
            self.result_label.config(text="Result: Please enter premises and conclusion.")
            return

        premises_list = [line.strip() for line in premises_text.split("\n") if line.strip()]

        # Collect all variable symbols
        var_names = set()
        for expr in premises_list + [conclusion_text]:
            var_names.update([ch for ch in expr if ch.isalpha()])
        var_symbols = symbols(sorted(var_names))
        var_dict = {name: sym for name, sym in zip(sorted(var_names), var_symbols)}

        # Convert strings to sympy expressions
        try:
            premises_expr = [eval(expr.replace(">>", ">>").replace("^", "&").replace("v", "|").replace("~", "Not(")+")") for expr in premises_list]
            conclusion_expr = eval(conclusion_text.replace(">>", ">>").replace("^", "&").replace("v", "|").replace("~", "Not(")+")")
        except Exception as e:
            self.result_label.config(text=f"Result: Invalid expression. {e}")
            return

        # Check validity: if premises & not conclusion is satisfiable, then invalid
        combined_expr = And(*premises_expr, Not(conclusion_expr))
        sat = satisfiable(combined_expr)

        if sat:
            self.result_label.config(text="Result: Argument is INVALID")
            self.counterexample_label.config(text=f"Counterexample: {sat}")
        else:
            self.result_label.config(text="Result: Argument is VALID")
            self.counterexample_label.config(text="")

if __name__ == "__main__":
    root = tk.Tk()
    app = LogicalArgumentValidator(root)
    root.mainloop()

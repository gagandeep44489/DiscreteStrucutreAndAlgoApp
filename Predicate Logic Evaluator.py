import tkinter as tk
from tkinter import ttk, messagebox
import sympy as sp
from sympy.logic.boolalg import And, Or, Not, Implies, Equivalent
from sympy import symbols
from sympy.logic.inference import satisfiable

# ---------------------------------------------------
# Predicate Logic Evaluator Desktop App
# ---------------------------------------------------

class PredicateLogicApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Predicate Logic Evaluator")
        self.geometry("1100x700")

        # State
        self.domain = []
        self.constants = {}
        self.predicates = {}
        self.formula = None

        self.build_ui()

    # ---------------------------------------------------
    # UI Layout
    # ---------------------------------------------------
    def build_ui(self):
        top = ttk.Frame(self, padding=8)
        top.pack(fill='x')

        ttk.Label(top, text="Formula:").pack(side='left')
        self.formula_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.formula_var, width=60).pack(side='left', padx=8)

        ttk.Button(top, text="Parse Formula", command=self.parse_formula).pack(side='left', padx=4)
        ttk.Button(top, text="Evaluate", command=self.evaluate_formula).pack(side='left', padx=4)
        ttk.Button(top, text="Check Validity", command=self.check_validity).pack(side='left', padx=4)
        ttk.Button(top, text="Check Satisfiable", command=self.check_satisfiable).pack(side='left', padx=4)

        # domain section
        domain_frame = ttk.LabelFrame(self, text="Domain", padding=10)
        domain_frame.pack(fill='x', padx=8, pady=6)

        self.domain_var = tk.StringVar()
        ttk.Entry(domain_frame, textvariable=self.domain_var, width=40).pack(side='left', padx=4)
        ttk.Button(domain_frame, text="Set Domain", command=self.set_domain).pack(side='left', padx=4)
        ttk.Label(domain_frame, text="(comma-separated)").pack(side='left')

        # predicates section
        pred_frame = ttk.LabelFrame(self, text="Predicates", padding=10)
        pred_frame.pack(fill='x', padx=8, pady=6)

        ttk.Label(pred_frame, text="Predicate name:").grid(row=0, column=0)
        ttk.Label(pred_frame, text="Arity (1 or 2):").grid(row=0, column=1)
        ttk.Label(pred_frame, text="True tuples:").grid(row=0, column=2)

        self.pred_name_var = tk.StringVar()
        ttk.Entry(pred_frame, textvariable=self.pred_name_var, width=12).grid(row=1, column=0, padx=4)

        self.pred_arity_var = tk.IntVar(value=1)
        ttk.Spinbox(pred_frame, from_=1, to=2, width=5, textvariable=self.pred_arity_var).grid(row=1, column=1, padx=4)

        self.pred_tuple_var = tk.StringVar()
        ttk.Entry(pred_frame, textvariable=self.pred_tuple_var, width=40).grid(row=1, column=2, padx=4)

        ttk.Button(pred_frame, text="Add Predicate", command=self.add_predicate).grid(row=1, column=3, padx=4)

        # Info display
        self.output = tk.Text(self, height=20, wrap="word")
        self.output.pack(fill='both', expand=True, padx=8, pady=10)

    # ---------------------------------------------------
    # Domain management
    # ---------------------------------------------------
    def set_domain(self):
        text = self.domain_var.get().strip()
        if not text:
            return

        self.domain = [x.strip() for x in text.split(",") if x.strip()]
        self.output.insert('end', f"Domain set to: {self.domain}\n\n")

    # ---------------------------------------------------
    # Predicate setup
    # ---------------------------------------------------
    def add_predicate(self):
        name = self.pred_name_var.get().strip()
        arity = self.pred_arity_var.get()
        tuples_text = self.pred_tuple_var.get().strip()

        if not name or arity not in (1,2):
            messagebox.showerror("Error", "Invalid predicate definition.")
            return

        true_tuples = []
        if tuples_text:
            raw = [t.strip() for t in tuples_text.split(";")]
            for each in raw:
                t = tuple(x.strip() for x in each.split(","))
                if len(t) != arity:
                    messagebox.showerror("Error", "Tuple arity mismatch.")
                    return
                true_tuples.append(t)

        self.predicates[name] = (arity, true_tuples)
        self.output.insert('end', f"Predicate {name}/{arity}: {true_tuples}\n\n")

    # ---------------------------------------------------
    # Formula parsing (SymPy-like)
    # ---------------------------------------------------
    def parse_formula(self):
        text = self.formula_var.get().strip()
        if not text:
            messagebox.showerror("Error", "Formula is empty")
            return

        try:
            # Very lightweight parsing using sympy symbols
            # Users write predicates as P(x), R(x,y)
            expr = sp.sympify(text, evaluate=False)
            self.formula = expr
            self.output.insert('end', f"Parsed formula: {expr}\n\n")
        except Exception as e:
            messagebox.showerror("Error", f"Parsing failed: {e}")

    # ---------------------------------------------------
    # Evaluate formula under interpretation
    # ---------------------------------------------------
    def evaluate_formula(self):
        if self.formula is None:
            messagebox.showerror("Error", "Parse formula first.")
            return

        if not self.domain:
            messagebox.showerror("Error", "Set domain first.")
            return

        result = self.interpret_formula(self.formula)
        self.output.insert('end', f"Evaluation result: {result}\n\n")

    # ---------------------------------------------------
    # Recursive evaluation
    # ---------------------------------------------------
    def interpret_formula(self, expr):
        # Predicate call: P(x)
        if isinstance(expr, sp.Function):
            name = expr.func.__name__
            if name not in self.predicates:
                raise ValueError(f"Predicate {name} not defined")

            arity, true_tuples = self.predicates[name]

            args = []
            for a in expr.args:
                if isinstance(a, sp.Symbol):
                    # Treat symbol as a constant name referring to domain element
                    args.append(str(a))
                else:
                    raise ValueError("Only constant symbols supported.")

            t = tuple(args)
            return t in true_tuples

        # Boolean operators
        if isinstance(expr, And):
            return all(self.interpret_formula(arg) for arg in expr.args)

        if isinstance(expr, Or):
            return any(self.interpret_formula(arg) for arg in expr.args)

        if isinstance(expr, Not):
            return not self.interpret_formula(expr.args[0])

        if isinstance(expr, Implies):
            A = self.interpret_formula(expr.args[0])
            B = self.interpret_formula(expr.args[1])
            return (not A) or B

        if isinstance(expr, Equivalent):
            A = self.interpret_formula(expr.args[0])
            B = self.interpret_formula(expr.args[1])
            return A == B

        return False

    # ---------------------------------------------------
    # Logical meta-properties
    # ---------------------------------------------------
    def check_validity(self):
        if self.formula is None:
            messagebox.showerror("Error", "Parse formula first.")
            return

        try:
            r = satisfiable(Not(self.formula))
            if r is False:
                self.output.insert('end', "Formula is VALID (true in all interpretations)\n\n")
            else:
                self.output.insert('end', "Formula is NOT valid\n\n")
        except:
            self.output.insert('end', "Validity check failed\n\n")

    def check_satisfiable(self):
        if self.formula is None:
            messagebox.showerror("Error", "Parse formula first.")
            return

        try:
            r = satisfiable(self.formula)
            if r is False:
                self.output.insert('end', "Formula is UNSAT (no interpretation makes it true)\n\n")
            else:
                self.output.insert('end', "Formula is SATISFIABLE\n\n")
        except:
            self.output.insert('end', "Satisfiability check failed\n\n")


# ---------------------------------------------------
# Run App
# ---------------------------------------------------
if __name__ == "__main__":
    app = PredicateLogicApp()
    app.mainloop()

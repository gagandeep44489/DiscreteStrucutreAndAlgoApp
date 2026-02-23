import tkinter as tk
from tkinter import messagebox

class SetExpressionSimplifier:
    def __init__(self, root):
        self.root = root
        self.root.title("Set Expression Simplifier")
        self.root.geometry("650x500")

        tk.Label(root, text="Set Expression Simplifier",
                 font=("Arial", 18, "bold")).pack(pady=10)

        # Universal Set
        tk.Label(root, text="Universal Set (comma separated):").pack()
        self.universal_entry = tk.Entry(root, width=50)
        self.universal_entry.pack()

        # Set A
        tk.Label(root, text="Set A (comma separated):").pack()
        self.setA_entry = tk.Entry(root, width=50)
        self.setA_entry.pack()

        # Set B
        tk.Label(root, text="Set B (comma separated):").pack()
        self.setB_entry = tk.Entry(root, width=50)
        self.setB_entry.pack()

        # Set C
        tk.Label(root, text="Set C (comma separated):").pack()
        self.setC_entry = tk.Entry(root, width=50)
        self.setC_entry.pack()

        # Expression Input
        tk.Label(root, text="Enter Set Expression:").pack(pady=5)
        self.expression_entry = tk.Entry(root, width=50)
        self.expression_entry.pack()

        tk.Button(root, text="Simplify Expression",
                  command=self.simplify_expression).pack(pady=10)

        self.result_label = tk.Label(root, text="", font=("Arial", 12))
        self.result_label.pack(pady=20)

    def parse_set(self, entry):
        values = entry.get().strip()
        if values == "":
            return set()
        return set(values.split(","))

    def simplify_expression(self):
        try:
            U = self.parse_set(self.universal_entry)
            A = self.parse_set(self.setA_entry)
            B = self.parse_set(self.setB_entry)
            C = self.parse_set(self.setC_entry)

            expr = self.expression_entry.get()

            # Handle complement using '
            expr = expr.replace("A'", "U - A")
            expr = expr.replace("B'", "U - B")
            expr = expr.replace("C'", "U - C")

            result = eval(expr)

            self.result_label.config(
                text=f"Simplified Result:\n{result}"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Invalid Expression\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SetExpressionSimplifier(root)
    root.mainloop()
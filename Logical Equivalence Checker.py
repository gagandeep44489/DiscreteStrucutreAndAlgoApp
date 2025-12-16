import tkinter as tk
from tkinter import messagebox
from itertools import product

class LogicalEquivalenceChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("Logical Equivalence Checker")
        self.root.geometry("700x500")

        # Input frame
        input_frame = tk.Frame(root)
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Expression 1 (use variables a,b,c,... and operators & | ~)").pack()
        self.expr1_entry = tk.Entry(input_frame, width=60)
        self.expr1_entry.pack(pady=5)

        tk.Label(input_frame, text="Expression 2 (use variables a,b,c,... and operators & | ~)").pack()
        self.expr2_entry = tk.Entry(input_frame, width=60)
        self.expr2_entry.pack(pady=5)

        check_btn = tk.Button(input_frame, text="Check Equivalence", command=self.check_equivalence)
        check_btn.pack(pady=10)

        # Output frame
        self.output_text = tk.Text(root, wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def check_equivalence(self):
        expr1 = self.expr1_entry.get().strip()
        expr2 = self.expr2_entry.get().strip()

        if not expr1 or not expr2:
            messagebox.showwarning("Input Error", "Please enter both expressions")
            return

        try:
            # Find all unique variables
            vars_set = set([ch for ch in expr1+expr2 if ch.isalpha()])
            vars_list = sorted(list(vars_set))

            equivalent = True
            self.output_text.delete('1.0', tk.END)
            self.output_text.insert(tk.END, f"Checking equivalence for variables: {vars_list}\n\n")

            # Generate all combinations of True/False
            for values in product([False, True], repeat=len(vars_list)):
                env = dict(zip(vars_list, values))
                val1 = eval(expr1, {}, env)
                val2 = eval(expr2, {}, env)
                self.output_text.insert(tk.END, f"{env}: Expr1={val1}, Expr2={val2}\n")
                if val1 != val2:
                    equivalent = False

            if equivalent:
                self.output_text.insert(tk.END, "\nExpressions are LOGICALLY EQUIVALENT")
            else:
                self.output_text.insert(tk.END, "\nExpressions are NOT EQUIVALENT")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to evaluate expressions:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LogicalEquivalenceChecker(root)
    root.mainloop()
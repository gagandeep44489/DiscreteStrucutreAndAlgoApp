import tkinter as tk
from tkinter import messagebox
from sympy import symbols
from sympy.logic.boolalg import to_cnf, to_dnf
from sympy.parsing.sympy_parser import parse_expr

class CNFDNFConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("CNF / DNF Converter")
        self.root.geometry("700x400")

        tk.Label(
            root,
            text="Enter Logical Expression (use &, |, ~)",
            font=("Arial", 12)
        ).pack(pady=10)

        self.input_expr = tk.Entry(root, width=70)
        self.input_expr.pack(pady=5)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Convert to CNF", command=self.convert_cnf).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="Convert to DNF", command=self.convert_dnf).grid(row=0, column=1, padx=10)

        tk.Label(root, text="Result").pack(pady=5)

        self.output = tk.Text(root, height=8, width=80)
        self.output.pack(pady=5)

    def convert_cnf(self):
        self.convert(mode="cnf")

    def convert_dnf(self):
        self.convert(mode="dnf")

    def convert(self, mode):
        expr_text = self.input_expr.get()
        if not expr_text:
            messagebox.showerror("Error", "Please enter a logical expression")
            return

        try:
            expr = parse_expr(expr_text, evaluate=False)
            if mode == "cnf":
                result = to_cnf(expr, simplify=True)
            else:
                result = to_dnf(expr, simplify=True)

            self.output.delete("1.0", tk.END)
            self.output.insert(tk.END, str(result))

        except Exception as e:
            messagebox.showerror("Error", f"Invalid Expression\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CNFDNFConverter(root)
    root.mainloop()

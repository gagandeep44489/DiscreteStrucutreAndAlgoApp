import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt

class FunctionAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Function Graph Analyzer (One-One / Onto)")

        tk.Label(root, text="Enter function in terms of x (e.g., x**2 + 1):").pack()
        self.function_entry = tk.Entry(root, width=50)
        self.function_entry.pack()

        tk.Label(root, text="Domain start:").pack()
        self.domain_start = tk.Entry(root)
        self.domain_start.pack()

        tk.Label(root, text="Domain end:").pack()
        self.domain_end = tk.Entry(root)
        self.domain_end.pack()

        tk.Label(root, text="Codomain start:").pack()
        self.codomain_start = tk.Entry(root)
        self.codomain_start.pack()

        tk.Label(root, text="Codomain end:").pack()
        self.codomain_end = tk.Entry(root)
        self.codomain_end.pack()

        tk.Button(root, text="Analyze Function", command=self.analyze).pack(pady=10)

    def analyze(self):
        try:
            func_str = self.function_entry.get()
            x_start = float(self.domain_start.get())
            x_end = float(self.domain_end.get())
            y_start = float(self.codomain_start.get())
            y_end = float(self.codomain_end.get())

            x = np.linspace(x_start, x_end, 400)
            y = eval(func_str)

            # Plot graph
            plt.figure()
            plt.plot(x, y)
            plt.title("Function Graph")
            plt.xlabel("x")
            plt.ylabel("f(x)")
            plt.grid(True)
            plt.show()

            # Check Injective (One-One)
            injective = len(set(np.round(y, 5))) == len(y)

            # Check Surjective (Onto)
            surjective = (min(y) <= y_start) and (max(y) >= y_end)

            result = ""
            if injective:
                result += "Function is One-One (Injective)\n"
            else:
                result += "Function is NOT One-One\n"

            if surjective:
                result += "Function is Onto (Surjective)"
            else:
                result += "Function is NOT Onto"

            if injective and surjective:
                result += "\nFunction is Bijective"

            messagebox.showinfo("Analysis Result", result)

        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = FunctionAnalyzer(root)
    root.mainloop()
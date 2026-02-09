import tkinter as tk
from tkinter import messagebox, scrolledtext
from itertools import product


class CartesianProductApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cartesian Product Calculator")
        self.root.geometry("650x500")
        self.root.resizable(False, False)

        title = tk.Label(
            root,
            text="Cartesian Product Calculator",
            font=("Arial", 16, "bold")
        )
        title.pack(pady=10)

        instruction = tk.Label(
            root,
            text="Enter sets (comma-separated). One set per line.",
            font=("Arial", 10)
        )
        instruction.pack()

        self.input_box = scrolledtext.ScrolledText(
            root,
            width=70,
            height=8,
            font=("Arial", 10)
        )
        self.input_box.pack(pady=10)

        calculate_btn = tk.Button(
            root,
            text="Calculate Cartesian Product",
            font=("Arial", 11, "bold"),
            command=self.calculate_product
        )
        calculate_btn.pack(pady=5)

        self.output_box = scrolledtext.ScrolledText(
            root,
            width=70,
            height=15,
            font=("Arial", 10)
        )
        self.output_box.pack(pady=10)

    def calculate_product(self):
        self.output_box.delete("1.0", tk.END)

        raw_input = self.input_box.get("1.0", tk.END).strip()
        if not raw_input:
            messagebox.showerror("Input Error", "Please enter at least two sets.")
            return

        lines = raw_input.splitlines()
        sets = []

        for line in lines:
            items = [item.strip() for item in line.split(",") if item.strip()]
            if not items:
                messagebox.showerror(
                    "Input Error",
                    "Each line must contain at least one element."
                )
                return
            sets.append(items)

        if len(sets) < 2:
            messagebox.showerror(
                "Input Error",
                "Please enter at least two sets."
            )
            return

        result = list(product(*sets))

        self.output_box.insert(tk.END, f"Total combinations: {len(result)}\n\n")
        for item in result:
            self.output_box.insert(tk.END, f"{item}\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = CartesianProductApp(root)
    root.mainloop()

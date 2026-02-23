import tkinter as tk
from tkinter import messagebox
import itertools

class UniversalSetBuilder:
    def __init__(self, root):
        self.root = root
        self.root.title("Universal Set Builder")
        self.root.geometry("700x600")

        tk.Label(root, text="Universal Set Builder",
                 font=("Arial", 18, "bold")).pack(pady=10)

        # Universal Set Input
        tk.Label(root, text="Enter Universal Set (comma separated):").pack()
        self.universal_entry = tk.Entry(root, width=60)
        self.universal_entry.pack()

        tk.Label(root, text="OR Generate Range (start,end):").pack()
        self.range_entry = tk.Entry(root, width=40)
        self.range_entry.pack()

        tk.Button(root, text="Build Universal Set",
                  command=self.build_universal_set).pack(pady=5)

        # Subset Input
        tk.Label(root, text="Enter Subset (comma separated):").pack(pady=5)
        self.subset_entry = tk.Entry(root, width=60)
        self.subset_entry.pack()

        tk.Button(root, text="Validate Subset",
                  command=self.validate_subset).pack(pady=5)

        tk.Button(root, text="Generate Power Set",
                  command=self.generate_powerset).pack(pady=5)

        tk.Button(root, text="Clear All",
                  command=self.clear_all).pack(pady=5)

        self.result_label = tk.Label(root, text="", font=("Arial", 12))
        self.result_label.pack(pady=20)

        self.U = set()

    def build_universal_set(self):
        try:
            manual_input = self.universal_entry.get().strip()
            range_input = self.range_entry.get().strip()

            if manual_input:
                self.U = set(manual_input.split(","))
            elif range_input:
                start, end = map(int, range_input.split(","))
                self.U = set(range(start, end + 1))
            else:
                messagebox.showerror("Error", "Enter manual set or range")
                return

            self.result_label.config(text=f"Universal Set Built:\n{self.U}")

        except Exception as e:
            messagebox.showerror("Error", f"Invalid Input\n{e}")

    def validate_subset(self):
        if not self.U:
            messagebox.showerror("Error", "Build Universal Set first")
            return

        subset_values = self.subset_entry.get().strip()
        if subset_values == "":
            messagebox.showerror("Error", "Enter subset values")
            return

        subset = set(subset_values.split(","))

        if subset.issubset(self.U):
            self.result_label.config(text="Valid Subset ✅")
        else:
            self.result_label.config(text="Invalid Subset ❌")

    def generate_powerset(self):
        if not self.U:
            messagebox.showerror("Error", "Build Universal Set first")
            return

        elements = list(self.U)
        powerset = []
        for r in range(len(elements) + 1):
            powerset.extend(itertools.combinations(elements, r))

        self.result_label.config(
            text=f"Power Set Size: {len(powerset)}\nPower Set:\n{powerset}"
        )

    def clear_all(self):
        self.universal_entry.delete(0, tk.END)
        self.range_entry.delete(0, tk.END)
        self.subset_entry.delete(0, tk.END)
        self.result_label.config(text="")
        self.U = set()

if __name__ == "__main__":
    root = tk.Tk()
    app = UniversalSetBuilder(root)
    root.mainloop()
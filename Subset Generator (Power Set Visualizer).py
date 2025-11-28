import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import csv

class PowerSetVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Subset Generator (Power Set Visualizer)")
        self.root.geometry("700x600")

        # Input Frame
        input_frame = ttk.LabelFrame(root, text="Input Set")
        input_frame.pack(fill="x", padx=10, pady=10)

        self.entry_items = ttk.Entry(input_frame, width=60)
        self.entry_items.pack(side="left", padx=5, pady=5)

        btn_generate_random = ttk.Button(input_frame, text="Random Set", command=self.generate_random_set)
        btn_generate_random.pack(side="left", padx=5)

        btn_generate = ttk.Button(input_frame, text="Generate Subsets", command=self.generate_subsets)
        btn_generate.pack(side="left", padx=5)

        # Filter Frame
        filter_frame = ttk.LabelFrame(root, text="Filters")
        filter_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(filter_frame, text="Subset size (optional):").pack(side="left", padx=5)
        self.entry_filter = ttk.Entry(filter_frame, width=10)
        self.entry_filter.pack(side="left", padx=5)

        btn_apply_filter = ttk.Button(filter_frame, text="Apply Filter", command=self.apply_filter)
        btn_apply_filter.pack(side="left", padx=5)

        # Output Frame
        output_frame = ttk.LabelFrame(root, text="Generated Subsets")
        output_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.text_output = tk.Text(output_frame, wrap="word")
        self.text_output.pack(fill="both", expand=True)

        # Buttons Frame
        btn_frame = ttk.Frame(root)
        btn_frame.pack(fill="x", padx=10, pady=10)

        btn_export_txt = ttk.Button(btn_frame, text="Export TXT", command=self.export_txt)
        btn_export_txt.pack(side="left", padx=5)

        btn_export_csv = ttk.Button(btn_frame, text="Export CSV", command=self.export_csv)
        btn_export_csv.pack(side="left", padx=5)

        btn_clear = ttk.Button(btn_frame, text="Clear", command=self.clear_output)
        btn_clear.pack(side="right", padx=5)

        self.subsets = []

    # Generate random items
    def generate_random_set(self):
        size = random.randint(3, 7)
        items = [chr(65 + i) for i in range(size)]
        self.entry_items.delete(0, tk.END)
        self.entry_items.insert(0, ", ".join(items))

    # Generate power set
    def generate_subsets(self):
        raw = self.entry_items.get().strip()

        if not raw:
            messagebox.showerror("Error", "Please enter at least one item.")
            return

        items = [x.strip() for x in raw.split(",") if x.strip()]

        if len(items) == 0:
            messagebox.showerror("Error", "Invalid input format.")
            return

        self.subsets = self.compute_power_set(items)
        self.display_subsets(self.subsets)

    # Compute power set (binary method)
    def compute_power_set(self, items):
        n = len(items)
        power_set = []

        for mask in range(1 << n):
            subset = []
            for i in range(n):
                if mask & (1 << i):
                    subset.append(items[i])
            power_set.append(subset)

        return power_set

    # Display subsets
    def display_subsets(self, subsets):
        self.text_output.delete("1.0", tk.END)

        for s in subsets:
            self.text_output.insert(tk.END, "{ " + ", ".join(s) + " }\n")

        self.text_output.insert(tk.END, f"\nTotal subsets: {len(subsets)}")

    # Apply subset size filter
    def apply_filter(self):
        if not self.subsets:
            messagebox.showinfo("Info", "Please generate subsets first.")
            return

        val = self.entry_filter.get().strip()
        if not val.isdigit():
            messagebox.showerror("Error", "Filter must be a number.")
            return

        k = int(val)
        filtered = [s for s in self.subsets if len(s) == k]
        self.display_subsets(filtered)

    # Export to TXT
    def export_txt(self):
        if not self.subsets:
            messagebox.showinfo("Info", "No subsets to export.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text Files", "*.txt")])

        if not file_path:
            return

        with open(file_path, "w") as f:
            for s in self.subsets:
                f.write("{ " + ", ".join(s) + " }\n")

        messagebox.showinfo("Success", "Exported to TXT successfully!")

    # Export to CSV
    def export_csv(self):
        if not self.subsets:
            messagebox.showinfo("Info", "No subsets to export.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV Files", "*.csv")])

        if not file_path:
            return

        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            for s in self.subsets:
                writer.writerow(s)

        messagebox.showinfo("Success", "Exported to CSV successfully!")

    # Clear output screen
    def clear_output(self):
        self.text_output.delete("1.0", tk.END)


# Run the Application
if __name__ == "__main__":
    root = tk.Tk()
    app = PowerSetVisualizer(root)
    root.mainloop()

#!/usr/bin/env python3
"""
Inclusion-Exclusion Principle Demo Desktop App
Demonstrates |A ∪ B ∪ C| for 3 sets with Venn diagram visualization.

Requirements:
- Python 3.8+
- matplotlib, matplotlib_venn, numpy
Install dependencies:
pip install matplotlib matplotlib-venn numpy
"""

import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib_venn import venn3

class InclusionExclusionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Inclusion-Exclusion Principle Demo")
        self.geometry("800x600")
        self._create_widgets()

    def _create_widgets(self):
        frame = ttk.Frame(self, padding=10)
        frame.pack(side=tk.TOP, fill=tk.X)

        # Labels and entries for set sizes
        labels = ["|A|", "|B|", "|C|", "|A∩B|", "|A∩C|", "|B∩C|", "|A∩B∩C|"]
        self.entries = {}
        for i, label in enumerate(labels):
            ttk.Label(frame, text=label).grid(row=i//4, column=(i%4)*2, sticky="w", padx=2, pady=2)
            entry = ttk.Entry(frame, width=8)
            entry.grid(row=i//4, column=(i%4)*2+1, sticky="w", padx=2, pady=2)
            entry.insert(0, "0")
            self.entries[label] = entry

        # Calculate button
        self.calc_btn = ttk.Button(frame, text="Calculate |A ∪ B ∪ C|", command=self.calculate_union)
        self.calc_btn.grid(row=2, column=0, columnspan=4, pady=6)

        # Result display
        self.result_var = tk.StringVar(value="Result will appear here")
        ttk.Label(frame, textvariable=self.result_var, font=("TkDefaultFont", 12, "bold")).grid(row=3, column=0, columnspan=4, pady=6)

        # Matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(5,5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def calculate_union(self):
        try:
            # Get all entries
            A = int(self.entries["|A|"].get())
            B = int(self.entries["|B|"].get())
            C = int(self.entries["|C|"].get())
            AB = int(self.entries["|A∩B|"].get())
            AC = int(self.entries["|A∩C|"].get())
            BC = int(self.entries["|B∩C|"].get())
            ABC = int(self.entries["|A∩B∩C|"].get())

            # Validate intersections do not exceed set sizes
            if AB > min(A,B) or AC > min(A,C) or BC > min(B,C) or ABC > min(AB, AC, BC):
                messagebox.showerror("Invalid Input", "Intersections cannot exceed set sizes.")
                return

            # Inclusion-Exclusion formula
            union_size = A + B + C - AB - AC - BC + ABC
            self.result_var.set(f"|A ∪ B ∪ C| = {union_size}")

            # Draw Venn diagram
            self.ax.clear()
            venn3(subsets=(A-AB-AC+ABC, B-AB-BC+ABC, AB-ABC, C-AC-BC+ABC, AC-ABC, BC-ABC, ABC),
                  set_labels=("A", "B", "C"), ax=self.ax)
            self.ax.set_title("|A ∪ B ∪ C| Visualization")
            self.canvas.draw()

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid integer values.")

if __name__ == "__main__":
    app = InclusionExclusionApp()
    app.mainloop()

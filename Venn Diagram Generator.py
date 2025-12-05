"""
Venn Diagram Generator - Desktop app (Tkinter + matplotlib + matplotlib_venn)

Features:
- Create 2-set or 3-set Venn diagrams
- Enter set labels, sizes, and pairwise/three-way overlaps
- Choose colors, diagram title
- Render and save as PNG

Requirements:
- Python 3.8+
- matplotlib
- matplotlib-venn

Install dependencies:
    pip install matplotlib matplotlib-venn

Run:
    python venn_diagram_generator.py

Note: For accurate region sizes, the venn library attempts to scale areas but exact proportional drawings may not always be perfect due to geometry constraints.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn3


class VennApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Venn Diagram Generator")
        self.geometry("900x650")
        self._create_widgets()

    def _create_widgets(self):
        # Left control frame
        ctrl = ttk.Frame(self, padding=10)
        ctrl.pack(side=tk.LEFT, fill=tk.Y)

        # Diagram type
        ttk.Label(ctrl, text="Diagram type:").pack(anchor=tk.W, pady=(0, 4))
        self.diagram_type = tk.StringVar(value="2-set")
        for t in ("2-set", "3-set"):
            ttk.Radiobutton(ctrl, text=t, value=t, variable=self.diagram_type, command=self._on_type_change).pack(anchor=tk.W)

        ttk.Separator(ctrl, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)

        # Inputs for sets
        label_frame = ttk.Frame(ctrl)
        label_frame.pack(fill=tk.X)
        ttk.Label(label_frame, text="Set labels:").grid(row=0, column=0, columnspan=3, sticky=tk.W)

        self.label_vars = [tk.StringVar(value="A"), tk.StringVar(value="B"), tk.StringVar(value="C")]
        for i, v in enumerate(self.label_vars[:3]):
            ttk.Label(label_frame, text=f"Set {i+1}:").grid(row=i+1, column=0, sticky=tk.W)
            ttk.Entry(label_frame, textvariable=v, width=6).grid(row=i+1, column=1, sticky=tk.W)

        ttk.Separator(ctrl, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)

        # Numeric inputs
        nums = ttk.Frame(ctrl)
        nums.pack(fill=tk.X)
        ttk.Label(nums, text="Sizes / Overlaps (integers):").grid(row=0, column=0, columnspan=3, sticky=tk.W)

        # Single set sizes
        self.size_vars = [tk.StringVar(value="50"), tk.StringVar(value="30"), tk.StringVar(value="20")]
        for i, v in enumerate(self.size_vars[:3]):
            ttk.Label(nums, text=f"|{chr(65+i)}|:").grid(row=i+1, column=0, sticky=tk.W)
            ttk.Entry(nums, textvariable=v, width=8).grid(row=i+1, column=1, sticky=tk.W)

        # Pairwise overlaps
        self.ov_vars = [tk.StringVar(value="10"), tk.StringVar(value="5"), tk.StringVar(value="3")]  # AB, AC, BC
        ttk.Label(nums, text="Pairwise overlaps:").grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(6,0))
        ttk.Label(nums, text="A∩B:").grid(row=5, column=0, sticky=tk.W)
        ttk.Entry(nums, textvariable=self.ov_vars[0], width=8).grid(row=5, column=1, sticky=tk.W)
        ttk.Label(nums, text="A∩C:").grid(row=6, column=0, sticky=tk.W)
        ttk.Entry(nums, textvariable=self.ov_vars[1], width=8).grid(row=6, column=1, sticky=tk.W)
        ttk.Label(nums, text="B∩C:").grid(row=7, column=0, sticky=tk.W)
        ttk.Entry(nums, textvariable=self.ov_vars[2], width=8).grid(row=7, column=1, sticky=tk.W)

        # Triple overlap
        self.triple_var = tk.StringVar(value="2")
        ttk.Label(nums, text="A∩B∩C:").grid(row=8, column=0, sticky=tk.W, pady=(6,0))
        ttk.Entry(nums, textvariable=self.triple_var, width=8).grid(row=8, column=1, sticky=tk.W)

        ttk.Separator(ctrl, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)

        # Colors and title
        misc = ttk.Frame(ctrl)
        misc.pack(fill=tk.X)
        ttk.Label(misc, text="Colors (matplotlib names or hex):").pack(anchor=tk.W)
        self.color_vars = [tk.StringVar(value="#ff9999"), tk.StringVar(value="#99ccff"), tk.StringVar(value="#99ff99")]
        for i, v in enumerate(self.color_vars[:3]):
            ttk.Entry(misc, textvariable=v, width=10).pack(anchor=tk.W, pady=2)

        ttk.Label(misc, text="Diagram title:").pack(anchor=tk.W, pady=(8,0))
        self.title_var = tk.StringVar(value="Venn Diagram")
        ttk.Entry(misc, textvariable=self.title_var).pack(fill=tk.X)

        ttk.Button(ctrl, text="Render", command=self.render_venn).pack(fill=tk.X, pady=(12,4))
        ttk.Button(ctrl, text="Save as PNG", command=self.save_png).pack(fill=tk.X)

        # Right frame for preview
        preview = ttk.Frame(self, padding=10)
        preview.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        self.fig, self.ax = plt.subplots(figsize=(6,6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=preview)
        self.canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

        # Initial render
        self._on_type_change()
        self.render_venn()

    def _on_type_change(self):
        t = self.diagram_type.get()
        # Show/hide C inputs
        if t == "2-set":
            # hide set C widgets
            self.label_vars[2].set("C")
            self.size_vars[2].set("0")
            self.ov_vars[1].set("0")
            self.ov_vars[2].set("0")
            self.triple_var.set("0")
        else:
            # set some defaults for 3-set
            if self.size_vars[2].get() == "0":
                self.size_vars[2].set("20")
            if self.triple_var.get() == "0":
                self.triple_var.set("2")

    def _parse_int(self, var, name="value"):
        try:
            return int(var.get())
        except Exception:
            raise ValueError(f"Invalid integer for {name}: '{var.get()}'")

    def render_venn(self):
        self.ax.clear()
        t = self.diagram_type.get()
        try:
            sizes = [self._parse_int(self.size_vars[i], f"|{chr(65+i)}|") for i in range(3)]
            ov_ab = self._parse_int(self.ov_vars[0], "A∩B")
            ov_ac = self._parse_int(self.ov_vars[1], "A∩C")
            ov_bc = self._parse_int(self.ov_vars[2], "B∩C")
            tri = self._parse_int(self.triple_var, "A∩B∩C")
        except ValueError as e:
            messagebox.showerror("Input error", str(e))
            return

        labels = [v.get() for v in self.label_vars[:3]]
        colors = [v.get() for v in self.color_vars[:3]]
        title = self.title_var.get()

        if t == "2-set":
            # For venn2 we use subsets=(Aonly, Bonly, AB)
            # Given |A|, |B|, |A∩B| => Aonly = |A| - |A∩B|, Bonly = |B| - |A∩B|
            a, b = sizes[0], sizes[1]
            ab = ov_ab
            a_only = max(a - ab, 0)
            b_only = max(b - ab, 0)
            subsets = (a_only, b_only, ab)
            v = venn2(subsets=subsets, set_labels=(labels[0], labels[1]), ax=self.ax)
            # style
            for idx, patch in enumerate((v.get_patch_by_id('10'), v.get_patch_by_id('01'))):
                if patch is not None:
                    patch.set_alpha(0.6)
                    patch.set_edgecolor('black')
                    patch.set_facecolor(colors[idx])
            if v.get_patch_by_id('11') is not None:
                v.get_patch_by_id('11').set_facecolor(colors[2])
                v.get_patch_by_id('11').set_alpha(0.6)

        else:  # 3-set
            a, b, c = sizes
            ab = ov_ab
            ac = ov_ac
            bc = ov_bc
            abc = tri
            # venn3 expects a 7-tuple: (100*a_only, 010*b_only, 110#ab, 001*c_only, 101#ac, 011#bc, 111#abc)
            # We'll compute region counts approximately from inputs.
            a_only = max(a - ab - ac + abc, 0)
            b_only = max(b - ab - bc + abc, 0)
            c_only = max(c - ac - bc + abc, 0)
            ab_only = max(ab - abc, 0)
            ac_only = max(ac - abc, 0)
            bc_only = max(bc - abc, 0)

            subsets = (a_only, b_only, ab_only, c_only, ac_only, bc_only, abc)
            v = venn3(subsets=subsets, set_labels=(labels[0], labels[1], labels[2]), ax=self.ax)
            # style patches
            ids = ['100','010','110','001','101','011','111']
            for i, id_ in enumerate(ids):
                patch = v.get_patch_by_id(id_)
                if patch is not None:
                    patch.set_alpha(0.6)
                    # pick color from colors list cycling
                    patch.set_facecolor(colors[i % 3])
                    patch.set_edgecolor('black')

        self.ax.set_title(title)
        self.ax.axis('off')
        self.canvas.draw()

    def save_png(self):
        file = filedialog.asksaveasfilename(defaultextension='.png', filetypes=[('PNG image','*.png')])
        if not file:
            return
        try:
            self.fig.savefig(file, dpi=300, bbox_inches='tight')
            messagebox.showinfo('Saved', f'Saved diagram to {file}')
        except Exception as e:
            messagebox.showerror('Save failed', str(e))


if __name__ == '__main__':
    app = VennApp()
    app.mainloop()

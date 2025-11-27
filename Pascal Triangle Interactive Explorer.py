"""
Pascal's Triangle Interactive Explorer (Tkinter)

Save as: pascal_explorer.py
Run: python pascal_explorer.py

Dependencies: only standard library (Tkinter).
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import sys
import time
import threading

# Layout / drawing constants
CANVAS_BG = "white"
CELL_RADIUS = 26
CELL_PADDING_X = 10
ROW_GAP = 10
COL_SPACING = CELL_RADIUS * 2 + CELL_PADDING_X
TOP_MARGIN = 60
LEFT_MARGIN = 30
MAX_ROWS = 50  # keep reasonable for visualization

def nCk(n, k):
    # robust integer combination using math.comb when available
    try:
        return math.comb(n, k)
    except AttributeError:
        # fallback for older Python
        return math.factorial(n) // (math.factorial(k) * math.factorial(n - k))

def generate_pascals_triangle(n_rows):
    triangle = []
    for n in range(n_rows + 1):
        row = [1] * (n + 1)
        for k in range(1, n):
            row[k] = triangle[n - 1][k - 1] + triangle[n - 1][k]
        triangle.append(row)
    return triangle

class PascalExplorerApp:
    def __init__(self, root):
        self.root = root
        root.title("Pascal's Triangle — Interactive Explorer")
        root.geometry("1100x700")

        self.n_rows = tk.IntVar(value=12)
        self.highlight_row = tk.IntVar(value=-1)
        self.highlight_n = tk.IntVar(value=-1)
        self.highlight_k = tk.IntVar(value=-1)
        self.animate = tk.BooleanVar(value=False)

        self.triangle = generate_pascals_triangle(self.n_rows.get())

        self.build_ui()
        self.draw_triangle()

    def build_ui(self):
        # Left control panel
        control = ttk.Frame(self.root, padding=8)
        control.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(control, text="Pascal's Triangle Explorer", font=("Arial", 14, "bold")).pack(pady=(4,10))

        # Rows control
        rows_frame = ttk.Frame(control)
        rows_frame.pack(fill=tk.X, pady=4)
        ttk.Label(rows_frame, text="Rows (0..{})".format(MAX_ROWS)).pack(anchor=tk.W)
        self.rows_slider = ttk.Scale(rows_frame, from_=0, to=MAX_ROWS, orient=tk.HORIZONTAL,
                                     command=self.on_slider_change, length=200)
        self.rows_slider.set(self.n_rows.get())
        self.rows_slider.pack(side=tk.TOP, padx=2, pady=2)
        rows_entry_frame = ttk.Frame(rows_frame)
        rows_entry_frame.pack(fill=tk.X)
        self.rows_entry = ttk.Entry(rows_entry_frame, width=6, textvariable=self.n_rows)
        self.rows_entry.pack(side=tk.LEFT, padx=(0,6))
        ttk.Button(rows_entry_frame, text="Set", command=self.on_set_rows).pack(side=tk.LEFT)

        # Highlight whole row
        ttk.Separator(control).pack(fill=tk.X, pady=8)
        ttk.Label(control, text="Highlight Row / Cell", font=("Arial", 11, "bold")).pack(anchor=tk.W)
        hr_frame = ttk.Frame(control)
        hr_frame.pack(fill=tk.X, pady=4)
        ttk.Label(hr_frame, text="Row n:").grid(row=0, column=0, sticky=tk.W)
        self.hr_entry = ttk.Entry(hr_frame, width=6, textvariable=self.highlight_row)
        self.hr_entry.grid(row=0, column=1, padx=6)
        ttk.Button(hr_frame, text="Highlight Row", command=self.on_highlight_row).grid(row=0, column=2)

        # Highlight specific nCk
        nk_frame = ttk.Frame(control)
        nk_frame.pack(fill=tk.X, pady=6)
        ttk.Label(nk_frame, text="n:").grid(row=0, column=0)
        self.n_entry = ttk.Entry(nk_frame, width=6, textvariable=self.highlight_n)
        self.n_entry.grid(row=0, column=1, padx=4)
        ttk.Label(nk_frame, text="k:").grid(row=0, column=2)
        self.k_entry = ttk.Entry(nk_frame, width=6, textvariable=self.highlight_k)
        self.k_entry.grid(row=0, column=3, padx=4)
        ttk.Button(nk_frame, text="Find nCk", command=self.on_find_nk).grid(row=0, column=4, padx=6)

        # Search / formula display
        ttk.Separator(control).pack(fill=tk.X, pady=8)
        ttk.Label(control, text="Selected Cell", font=("Arial", 11, "bold")).pack(anchor=tk.W)
        self.selected_label = ttk.Label(control, text="nCk: —", wraplength=220, justify=tk.LEFT)
        self.selected_label.pack(anchor=tk.W, pady=4)
        self.formula_label = ttk.Label(control, text="", wraplength=220, justify=tk.LEFT)
        self.formula_label.pack(anchor=tk.W)

        # Buttons: regenerate, animate, export, clear highlights
        btn_frame = ttk.Frame(control)
        btn_frame.pack(fill=tk.X, pady=10)
        ttk.Button(btn_frame, text="Regenerate", command=self.on_set_rows).grid(row=0, column=0, padx=4, pady=2)
        ttk.Button(btn_frame, text="Clear Highlights", command=self.clear_highlights).grid(row=0, column=1, padx=4)
        ttk.Checkbutton(btn_frame, text="Animate Reveal", variable=self.animate).grid(row=1, column=0, columnspan=2, pady=4)
        ttk.Button(btn_frame, text="Export Canvas", command=self.on_export).grid(row=2, column=0, columnspan=2, sticky="ew", pady=(6,0))

        # Info / tips
        ttk.Separator(control).pack(fill=tk.X, pady=8)
        tips = ("Tips:\n"
                "- Click a number in the canvas to copy nCk to clipboard.\n"
                "- Use the slider or type rows and press Set.\n"
                "- Max rows limited to {} for readability.").format(MAX_ROWS)
        ttk.Label(control, text=tips, wraplength=240, justify=tk.LEFT).pack(anchor=tk.W, pady=6)

        # Canvas area
        canvas_frame = ttk.Frame(self.root)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(canvas_frame, bg=CANVAS_BG)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # keep track of drawn cell positions for click mapping
        self.cell_positions = {}  # key: (n,k) -> (x,y,r,id_text,id_circle)

    # --- UI actions ---
    def on_slider_change(self, val):
        # slider returns float string — update entry as integer preview but don't redraw continuously
        try:
            v = int(float(val))
        except:
            return
        self.n_rows.set(v)

    def on_set_rows(self):
        try:
            v = int(self.n_rows.get())
        except ValueError:
            messagebox.showerror("Invalid", "Rows must be an integer.")
            return
        if v < 0 or v > MAX_ROWS:
            messagebox.showerror("Invalid", f"Rows must be between 0 and {MAX_ROWS}.")
            return
        # update slider & regenerate triangle
        self.rows_slider.set(v)
        self.triangle = generate_pascals_triangle(v)
        if self.animate.get():
            self.draw_triangle(animated=True)
        else:
            self.draw_triangle()

    def on_highlight_row(self):
        try:
            n = int(self.highlight_row.get())
        except:
            messagebox.showerror("Invalid", "Row must be integer.")
            return
        if n < 0 or n >= len(self.triangle):
            messagebox.showerror("Out of range", "Row outside generated triangle. Increase rows first.")
            return
        self.highlight_n.set(-1)
        self.highlight_k.set(-1)
        self.draw_triangle(highlight_row=n)

    def on_find_nk(self):
        try:
            n = int(self.highlight_n.get())
            k = int(self.highlight_k.get())
        except:
            messagebox.showerror("Invalid", "n and k must be integers.")
            return
        if n < 0 or n >= len(self.triangle) or k < 0 or k > n:
            messagebox.showerror("Out of range", "Requested n,k outside current triangle.")
            return
        self.draw_triangle(highlight_nk=(n, k))
        self.show_selected_cell(n, k)

    def clear_highlights(self):
        self.highlight_row.set(-1)
        self.highlight_n.set(-1)
        self.highlight_k.set(-1)
        self.draw_triangle()
        self.selected_label.config(text="nCk: —")
        self.formula_label.config(text="")

    def on_export(self):
        file = filedialog.asksaveasfilename(defaultextension=".ps", filetypes=[("PostScript", "*.ps")])
        if not file:
            return
        try:
            self.canvas.postscript(file=file, colormode="color")
            messagebox.showinfo("Exported", f"Canvas exported to {file} (PostScript). Convert to PNG with ImageMagick or similar.)")
        except Exception as e:
            messagebox.showerror("Export error", str(e))

    def on_canvas_resize(self, event):
        # redraw on resize
        self.canvas_width = event.width
        self.canvas_height = event.height
        self.draw_triangle()

    # --- Drawing logic ---
    def draw_triangle(self, animated=False, highlight_row=None, highlight_nk=None):
        # highlight_row or highlight_nk may be provided
        self.canvas.delete("all")
        self.cell_positions.clear()

        rows = len(self.triangle) - 1
        if rows < 0:
            return
        # calculate horizontal center positions per row so triangle is centered
        width = getattr(self, "canvas_width", 800)
        center_x = width / 2

        # vertical spacing
        row_height = CELL_RADIUS * 2 + ROW_GAP
        total_height = (rows + 1) * row_height + TOP_MARGIN
        # adjust if canvas height small
        height = getattr(self, "canvas_height", 600)
        # we won't scale fonts automatically; keep a readable size; optionally adapt
        font_size = 10
        font = ("Arial", font_size, "bold")

        # iterate rows
        reveal_sleep = 0.07 if animated else 0.0
        for n in range(rows + 1):
            k_count = n + 1
            row_width = k_count * COL_SPACING
            start_x = center_x - (row_width / 2) + COL_SPACING / 2
            y = TOP_MARGIN + n * row_height

            for k in range(k_count):
                x = start_x + k * COL_SPACING
                val = self.triangle[n][k]
                # visual choices
                bg = "#f8f9fb"
                outline = "#1f4f82"
                text_color = "black"

                # highlight logic
                if highlight_row is None and self.highlight_row.get() >= 0:
                    highlight_row = self.highlight_row.get()
                if highlight_nk is None and (self.highlight_n.get() >= 0 and self.highlight_k.get() >= 0):
                    highlight_nk = (self.highlight_n.get(), self.highlight_k.get())

                if highlight_row is not None and n == highlight_row:
                    bg = "#fff4b1"
                    outline = "#b8860b"
                    text_color = "black"
                if highlight_nk is not None and (n, k) == highlight_nk:
                    bg = "#b6ffd6"
                    outline = "#0b8a3a"
                    text_color = "black"

                # draw circle and text
                r = CELL_RADIUS
                circle_id = self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=bg, outline=outline, width=2)
                text_id = self.canvas.create_text(x, y, text=str(val), font=font, fill=text_color)
                # store mapping for click detection
                self.cell_positions[(n, k)] = (x, y, r, text_id, circle_id)
                # optional small subtitle with (n,k)
                # self.canvas.create_text(x, y + r + 8, text=f"({n},{k})", font=("Arial", 8))

            if reveal_sleep:
                self.canvas.update()
                time.sleep(reveal_sleep)

        # add title and stats
        self.canvas.create_text(width / 2, 20, text=f"Pascal's Triangle — Rows 0..{rows}", font=("Arial", 14, "bold"))
        self.canvas.create_text(120, 20, text="Click a cell to copy value and view nCk", font=("Arial", 10), anchor=tk.W)

    # --- Interaction ---
    def on_canvas_click(self, event):
        # find nearest cell by distance
        x, y = event.x, event.y
        clicked = None
        for (n, k), (cx, cy, r, tid, cid) in self.cell_positions.items():
            dx = x - cx
            dy = y - cy
            if dx * dx + dy * dy <= r * r:
                clicked = (n, k)
                break
        if clicked:
            n, k = clicked
            val = self.triangle[n][k]
            # copy to clipboard
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(str(val))
            except Exception:
                pass
            # highlight the cell
            self.highlight_row.set(-1)
            self.highlight_n.set(n)
            self.highlight_k.set(k)
            self.draw_triangle(highlight_nk=(n, k))
            self.show_selected_cell(n, k)

    def show_selected_cell(self, n, k):
        val = self.triangle[n][k]
        self.selected_label.config(text=f"n = {n}, k = {k}\nnCk = {val}")
        # show formula and explanation
        formula = f"Combination: C({n},{k}) = n! / (k! (n-k)!) = {nCk(n,k)}"
        factorials = f"{n}! / ({k}! * {n-k}!) = {math.factorial(n)} / ({math.factorial(k)} * {math.factorial(n-k)})"
        self.formula_label.config(text=formula + "\n" + factorials)

# --- Run app ---
def main():
    root = tk.Tk()
    app = PascalExplorerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

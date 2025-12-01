"""
Handshake Problem Visualizer (desktop app)

Save as: handshake_visualizer.py
Run with: python handshake_visualizer.py

Features:
- Visualize n people arranged on a circle.
- Draw all handshake edges (complete graph K_n).
- Show number of handshakes using formula n*(n-1)//2 and combinatorial explanation (C(n,2)).
- Animate edges being "counted" one-by-one with highlight and a running counter.
- Controls: n (1..20), Generate, Play/Pause, Step, Reset, Speed control.
- Optional PNG export of canvas (requires Pillow).
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import itertools
import time
import random

try:
    from PIL import ImageGrab, Image  # for PNG export via ImageGrab
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

# -----------------------
# Utility: circle positions
# -----------------------
def circle_positions(cx, cy, radius, n):
    """Return list of (x,y) coordinates equally spaced on circle (top-start)."""
    if n == 0:
        return []
    positions = []
    for i in range(n):
        angle = -math.pi / 2 + 2 * math.pi * i / n  # start at top and go clockwise
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        positions.append((x, y))
    return positions

# -----------------------
# App
# -----------------------
class HandshakeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Handshake Problem Visualizer")
        self.geometry("920x640")
        self.minsize(760, 520)

        # state
        self.n = 6
        self.nodes = []          # labels
        self.positions = []      # coords
        self.edges = []          # list of (i,j)
        self.current_edge_index = 0
        self.playing = False
        self.play_delay_ms = 650

        self._build_ui()
        self.generate_graph()  # initial

    # -----------------------
    def _build_ui(self):
        # Top controls
        top = ttk.Frame(self, padding=8)
        top.pack(side='top', fill='x')

        ttk.Label(top, text="Number of people (n):").pack(side='left')
        self.n_var = tk.IntVar(value=self.n)
        n_spin = ttk.Spinbox(top, from_=1, to=20, width=5, textvariable=self.n_var, command=self._n_changed)
        n_spin.pack(side='left', padx=(6,12))

        ttk.Label(top, text="Labels (optional, comma separated):").pack(side='left')
        self.labels_var = tk.StringVar(value="")
        labels_entry = ttk.Entry(top, textvariable=self.labels_var, width=36)
        labels_entry.pack(side='left', padx=(6,12))

        generate_btn = ttk.Button(top, text="Generate", command=self.generate_graph)
        generate_btn.pack(side='left')

        # Canvas + right panel
        middle = ttk.Frame(self)
        middle.pack(fill='both', expand=True, padx=8, pady=6)

        # Canvas
        canvas_frame = ttk.Frame(middle)
        canvas_frame.pack(side='left', fill='both', expand=True)
        self.canvas = tk.Canvas(canvas_frame, bg='white')
        self.canvas.pack(fill='both', expand=True, padx=6, pady=6)
        self.canvas.bind("<Configure>", lambda e: self.redraw())

        # Right controls
        side = ttk.Frame(middle, width=300)
        side.pack(side='right', fill='y', padx=(6,0))

        ttk.Label(side, text="Handshake Controls", font=("Segoe UI", 11, "bold")).pack(pady=(4,6))

        # Count display
        count_frame = ttk.Frame(side, padding=(6,4))
        count_frame.pack(fill='x')
        self.count_var = tk.StringVar(value="0")
        ttk.Label(count_frame, text="Handshakes counted:", font=('Segoe UI', 10)).grid(row=0, column=0, sticky='w')
        ttk.Label(count_frame, textvariable=self.count_var, font=('Segoe UI', 14, 'bold')).grid(row=1, column=0, sticky='w')

        # Formula & explanation
        formula_frame = ttk.LabelFrame(side, text="Formula & Explanation", padding=6)
        formula_frame.pack(fill='x', padx=6, pady=8)
        self.formula_label = tk.Label(formula_frame, text="", justify='left', anchor='w', font=('Segoe UI', 10))
        self.formula_label.pack(fill='x')

        # Buttons: play/step/reset
        btn_frame = ttk.Frame(side, padding=6)
        btn_frame.pack(fill='x')
        prev_btn = ttk.Button(btn_frame, text="◀ Step", command=self.step_back)
        prev_btn.pack(side='left', padx=4, expand=True, fill='x')
        self.play_btn = ttk.Button(btn_frame, text="Play ▶", command=self.toggle_play)
        self.play_btn.pack(side='left', padx=4, expand=True, fill='x')
        step_btn = ttk.Button(btn_frame, text="Step ▶", command=self.step_forward)
        step_btn.pack(side='left', padx=4, expand=True, fill='x')

        # Speed control
        speed_frame = ttk.Frame(side, padding=(6,4))
        speed_frame.pack(fill='x', pady=(6,2))
        ttk.Label(speed_frame, text="Speed (ms per step):").pack(anchor='w')
        self.speed_var = tk.IntVar(value=self.play_delay_ms)
        speed_scale = ttk.Scale(speed_frame, from_=100, to=2000, orient='horizontal', variable=self.speed_var, command=self._speed_changed)
        speed_scale.pack(fill='x', pady=(4,0))

        # Randomize labels / shuffle
        rand_frame = ttk.Frame(side, padding=6)
        rand_frame.pack(fill='x')
        shuffle_btn = ttk.Button(rand_frame, text="Shuffle Labels", command=self.shuffle_labels)
        shuffle_btn.pack(fill='x')

        # Export + reset
        export_frame = ttk.Frame(side, padding=(6,10))
        export_frame.pack(fill='x')
        export_ps = ttk.Button(export_frame, text="Export as PostScript", command=self.export_postscript)
        export_ps.pack(fill='x', pady=(0,6))
        export_png = ttk.Button(export_frame, text="Export as PNG (Pillow)", command=self.export_png)
        export_png.pack(fill='x')

        reset_btn = ttk.Button(side, text="Reset Count", command=self.reset_count)
        reset_btn.pack(fill='x', padx=6, pady=(8,0))

        # Status bar
        status = ttk.Frame(self, padding=4)
        status.pack(side='bottom', fill='x')
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status, textvariable=self.status_var).pack(side='left')

    # -----------------------
    def _n_changed(self):
        try:
            v = int(self.n_var.get())
            if v < 1:
                self.n_var.set(1)
        except Exception:
            self.n_var.set(6)

    def _speed_changed(self, _):
        self.play_delay_ms = int(self.speed_var.get())

    # -----------------------
    def generate_graph(self):
        """Generate nodes, positions and edges for current n and labels."""
        try:
            n = int(self.n_var.get())
        except Exception:
            messagebox.showerror("Invalid n", "Enter an integer for n.")
            return

        if n < 1:
            messagebox.showerror("Invalid n", "n must be >= 1.")
            return
        if n > 20:
            cont = messagebox.askyesno("Large n", "n > 20 may be slow to draw. Continue?")
            if not cont:
                return

        self.n = n
        labels_input = self.labels_var.get().strip()
        if labels_input:
            raw = [s.strip() for s in labels_input.split(",") if s.strip() != ""]
        else:
            raw = []

        # Build labels list length n
        labels = []
        for i in range(n):
            if i < len(raw):
                labels.append(raw[i])
            else:
                labels.append(str(i + 1))
        self.nodes = labels

        # Compute positions
        w = self.canvas.winfo_width() or 700
        h = self.canvas.winfo_height() or 520
        cx, cy = w / 2, h / 2
        r = min(w, h) / 2 - 70
        r = max(r, 80)
        self.positions = circle_positions(cx, cy, r, n)

        # Edges: all pairs (i,j) with i<j
        self.edges = list(itertools.combinations(range(n), 2))
        self.total_handshakes = len(self.edges)
        self._update_formula_display()

        # reset counting state
        self.current_edge_index = 0
        self.count_var.set(str(0))
        self.playing = False
        self.play_btn.config(text="Play ▶")
        self.status_var.set(f"Generated complete graph K_{n} with {self.total_handshakes} handshakes")
        self.redraw()

    # -----------------------
    def _update_formula_display(self):
        n = self.n
        formula_text = f"Formula: C(n,2) = n(n-1)/2\nFor n = {n}: {n} × {n-1} ÷ 2 = {self.total_handshakes}\n\nInterpretation: choose 2 people out of n to make a handshake."
        self.formula_label.config(text=formula_text)

    # -----------------------
    def redraw(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if not self.nodes:
            # placeholder text
            self.canvas.create_text(w/2, h/2, text="Click Generate to create nodes", font=('Segoe UI', 14), fill='#333')
            return

        # draw circle outline
        cx, cy = w/2, h/2
        r = min(w, h)/2 - 40
        if r < 10: r = 10
        self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline='#888')

        # draw all edges faintly
        node_radius = max(10, int(min(w, h) / 60))
        for (i, j) in self.edges:
            x1, y1 = self.positions[i]
            x2, y2 = self.positions[j]
            # Determine if edge is "counted" yet
            idx = self.edges.index((i,j))
            if idx < self.current_edge_index:
                width = 3
                color = '#ff6b35'  # highlighted (counted)
            elif idx == self.current_edge_index:
                width = 3
                color = '#f4c542'  # currently counting
            else:
                width = 1
                color = '#bdbdbd'  # not counted
            # draw edge
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width)

        # draw nodes on top
        for i, label in enumerate(self.nodes):
            x, y = self.positions[i]
            # draw node circle (first node slightly different color)
            self.canvas.create_oval(x-node_radius, y-node_radius, x+node_radius, y+node_radius, fill='#ffffff', outline='#333', width=2)
            # label
            self.canvas.create_text(x, y, text=str(label), font=('Segoe UI', max(8, int(node_radius/1.2), 9), 'bold'))

        # show caption at bottom
        caption = f"K_{self.n} — total handshakes: {self.total_handshakes}    Counted: {self.current_edge_index}"
        self.canvas.create_rectangle(6, h-36, w-6, h-6, fill='#ffffff', outline='#eee')
        self.canvas.create_text(12, h-22, anchor='w', text=caption, font=('Segoe UI', 9))

    # -----------------------
    def step_forward(self):
        if not self.edges:
            return
        if self.current_edge_index < self.total_handshakes:
            self.current_edge_index += 1
            self.count_var.set(str(self.current_edge_index))
        else:
            # already at end
            self.playing = False
            self.play_btn.config(text="Play ▶")
        self.status_var.set(f"Counted {self.current_edge_index} / {self.total_handshakes}")
        self.redraw()

    def step_back(self):
        if not self.edges:
            return
        if self.current_edge_index > 0:
            self.current_edge_index -= 1
            self.count_var.set(str(self.current_edge_index))
        self.status_var.set(f"Counted {self.current_edge_index} / {self.total_handshakes}")
        self.redraw()

    def reset_count(self):
        self.current_edge_index = 0
        self.count_var.set("0")
        self.playing = False
        self.play_btn.config(text="Play ▶")
        self.status_var.set("Reset count")
        self.redraw()

    # -----------------------
    def toggle_play(self):
        if not self.edges:
            return
        self.playing = not self.playing
        if self.playing:
            self.play_btn.config(text="Pause ❚❚")
            self._play_step()
        else:
            self.play_btn.config(text="Play ▶")

    def _play_step(self):
        if not self.playing:
            return
        # increment and redraw, but stop when finished
        if self.current_edge_index < self.total_handshakes:
            self.current_edge_index += 1
            self.count_var.set(str(self.current_edge_index))
            self.status_var.set(f"Counting {self.current_edge_index} / {self.total_handshakes}")
            self.redraw()
            self.after(self.play_delay_ms, self._play_step)
        else:
            self.playing = False
            self.play_btn.config(text="Play ▶")
            self.status_var.set("Finished counting all handshakes")

    # -----------------------
    def shuffle_labels(self):
        if not self.nodes:
            return
        random.shuffle(self.nodes)
        self.labels_var.set(", ".join(self.nodes))
        # regenerate positions and edges (labels changed order doesn't change edges but positions matter)
        # Recompute positions to reflect labels order (keep same n)
        w = self.canvas.winfo_width() or 700
        h = self.canvas.winfo_height() or 520
        cx, cy = w / 2, h / 2
        r = min(w, h) / 2 - 70
        r = max(r, 80)
        self.positions = circle_positions(cx, cy, r, self.n)
        self.reset_count()

    # -----------------------
    def export_postscript(self):
        if not self.nodes:
            messagebox.showinfo("Nothing to export", "Generate a graph first.")
            return
        fname = filedialog.asksaveasfilename(defaultextension=".ps", filetypes=[("PostScript", "*.ps"), ("All files", "*.*")])
        if not fname:
            return
        try:
            self.canvas.update()
            self.canvas.postscript(file=fname, colormode='color')
            messagebox.showinfo("Exported", f"Saved PostScript to:\n{fname}")
        except Exception as e:
            messagebox.showerror("Export failed", f"Could not export PostScript:\n{e}")

    def export_png(self):
        if not PIL_AVAILABLE:
            messagebox.showerror("Pillow required", "PNG export requires Pillow. Install with:\n\npip install pillow")
            return
        if not self.nodes:
            messagebox.showinfo("Nothing to export", "Generate a graph first.")
            return
        fname = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG image", "*.png"), ("All files", "*.*")])
        if not fname:
            return
        try:
            # Coordinates of canvas relative to screen
            self.canvas.update()
            x = self.canvas.winfo_rootx()
            y = self.canvas.winfo_rooty()
            x2 = x + self.canvas.winfo_width()
            y2 = y + self.canvas.winfo_height()
            img = ImageGrab.grab(bbox=(x, y, x2, y2))
            img.save(fname)
            messagebox.showinfo("Exported", f"Saved PNG to:\n{fname}")
        except Exception as e:
            messagebox.showerror("Export failed", f"Could not export PNG:\n{e}\nNote: ImageGrab may need an X server on some platforms.")

# -----------------------
def main():
    app = HandshakeApp()
    app.mainloop()

if __name__ == "__main__":
    main()

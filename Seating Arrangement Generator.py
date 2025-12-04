"""
Seating Arrangement Generator
Single-file Python desktop application using Tkinter.

Features:
- Add/remove names manually
- Import names from a CSV file (one name per line or a single column)
- Specify rows x columns for seating layout
- Set fixed seat assignments (Name -> seat index)
- Add avoid-pair constraints (two names who should not sit adjacent)
- Generate random arrangements that respect constraints (tries multiple times)
- Save/export arrangements to CSV
- Preview seating as grid

Usage:
- Save this file as seating_generator.py and run: python seating_generator.py
- Requires: Python 3.x. Tkinter is included with standard Python on most platforms.
- For CSV import/export the builtin csv module is used; pandas is *not* required.

Limitations & notes:
- Adjacency is considered orthogonal (up/down/left/right) in the grid.
- The algorithm attempts to find a valid seating by random shuffles and checking constraints; for difficult constraints or large lists it may fail after max_tries.

"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import random
import csv
import os

MAX_TRIES = 2000

class SeatingGeneratorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Seating Arrangement Generator")
        self.geometry("980x640")
        self.resizable(True, True)

        # Data
        self.names = []  # list of strings
        self.fixed = {}  # seat_index -> name
        self.avoid_pairs = set()  # set of frozenset({a,b})

        # UI
        self.create_widgets()

    def create_widgets(self):
        main = ttk.Frame(self, padding=8)
        main.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(main)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0,8))

        # Name management
        nm_frame = ttk.LabelFrame(left, text="Names")
        nm_frame.pack(fill=tk.Y, expand=False)

        self.name_entry = ttk.Entry(nm_frame, width=25)
        self.name_entry.grid(row=0, column=0, padx=4, pady=4)
        add_btn = ttk.Button(nm_frame, text="Add", command=self.add_name)
        add_btn.grid(row=0, column=1, padx=4, pady=4)

        import_btn = ttk.Button(nm_frame, text="Import CSV", command=self.import_csv)
        import_btn.grid(row=1, column=0, columnspan=2, sticky=tk.EW, padx=4)

        self.names_listbox = tk.Listbox(nm_frame, width=30, height=12, selectmode=tk.SINGLE)
        self.names_listbox.grid(row=2, column=0, columnspan=2, padx=4, pady=6)

        rm_btn = ttk.Button(nm_frame, text="Remove Selected", command=self.remove_selected)
        rm_btn.grid(row=3, column=0, columnspan=2, sticky=tk.EW, padx=4)

        clear_btn = ttk.Button(nm_frame, text="Clear All", command=self.clear_all)
        clear_btn.grid(row=4, column=0, columnspan=2, sticky=tk.EW, padx=4, pady=(4,8))

        # Layout settings
        layout_frame = ttk.LabelFrame(left, text="Layout & Constraints")
        layout_frame.pack(fill=tk.X, expand=False, pady=(8,0))

        ttk.Label(layout_frame, text="Rows:").grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        self.rows_var = tk.IntVar(value=3)
        rows_spin = ttk.Spinbox(layout_frame, from_=1, to=50, textvariable=self.rows_var, width=6)
        rows_spin.grid(row=0, column=1, padx=4)

        ttk.Label(layout_frame, text="Cols:").grid(row=0, column=2, sticky=tk.W, padx=4)
        self.cols_var = tk.IntVar(value=4)
        cols_spin = ttk.Spinbox(layout_frame, from_=1, to=50, textvariable=self.cols_var, width=6)
        cols_spin.grid(row=0, column=3, padx=4)

        ttk.Separator(layout_frame, orient=tk.HORIZONTAL).grid(row=1, column=0, columnspan=4, sticky=tk.EW, pady=6)

        # Fixed seat assignment
        ttk.Label(layout_frame, text="Fixed seat (name -> seat idx):").grid(row=2, column=0, columnspan=4, sticky=tk.W, padx=4)
        self.fixed_name_var = tk.StringVar()
        self.fixed_seat_var = tk.IntVar(value=0)
        ttk.Entry(layout_frame, textvariable=self.fixed_name_var, width=14).grid(row=3, column=0, padx=4, pady=4)
        ttk.Entry(layout_frame, textvariable=self.fixed_seat_var, width=6).grid(row=3, column=1, padx=4)
        ttk.Button(layout_frame, text="Set Fixed", command=self.set_fixed).grid(row=3, column=2, padx=4)
        ttk.Button(layout_frame, text="Clear Fixed", command=self.clear_fixed).grid(row=3, column=3, padx=4)

        # Avoid pair
        ttk.Label(layout_frame, text="Avoid pair (name1,name2):").grid(row=4, column=0, columnspan=4, sticky=tk.W, padx=4)
        self.avoid_a_var = tk.StringVar()
        self.avoid_b_var = tk.StringVar()
        ttk.Entry(layout_frame, textvariable=self.avoid_a_var, width=12).grid(row=5, column=0, padx=4, pady=4)
        ttk.Entry(layout_frame, textvariable=self.avoid_b_var, width=12).grid(row=5, column=1, padx=4)
        ttk.Button(layout_frame, text="Add Avoid", command=self.add_avoid).grid(row=5, column=2, padx=4)
        ttk.Button(layout_frame, text="Clear Avoids", command=self.clear_avoids).grid(row=5, column=3, padx=4)

        # Avoids list
        self.avoids_listbox = tk.Listbox(layout_frame, width=30, height=4)
        self.avoids_listbox.grid(row=6, column=0, columnspan=4, padx=4, pady=6)

        # Generate controls
        gen_frame = ttk.LabelFrame(left, text="Generate & Export")
        gen_frame.pack(fill=tk.X, expand=False, pady=8)

        self.max_tries_var = tk.IntVar(value=MAX_TRIES)
        ttk.Label(gen_frame, text="Max tries:").grid(row=0, column=0, padx=4, pady=6)
        ttk.Entry(gen_frame, textvariable=self.max_tries_var, width=8).grid(row=0, column=1, padx=4)

        ttk.Button(gen_frame, text="Generate Arrangement", command=self.generate_arrangement).grid(row=1, column=0, columnspan=2, sticky=tk.EW, padx=4, pady=6)
        ttk.Button(gen_frame, text="Save to CSV", command=self.save_csv).grid(row=2, column=0, columnspan=2, sticky=tk.EW, padx=4)

        # Right side: preview / grid
        right = ttk.Frame(main)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        preview_frame = ttk.LabelFrame(right, text="Seating Preview")
        preview_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas for grid
        self.grid_canvas = tk.Canvas(preview_frame, bg="#f8f8f8")
        self.grid_canvas.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.grid_canvas.bind("<Configure>", self.redraw_grid)

        # textual output
        out_frame = ttk.Frame(right)
        out_frame.pack(fill=tk.X)
        ttk.Label(out_frame, text="Last arrangement (seat_index: name)").pack(anchor=tk.W, padx=6)
        self.output_text = tk.Text(out_frame, height=6)
        self.output_text.pack(fill=tk.X, padx=6, pady=4)

        # status bar
        self.status_var = tk.StringVar(value="Ready")
        status = ttk.Label(self, textvariable=self.status_var, anchor=tk.W)
        status.pack(side=tk.BOTTOM, fill=tk.X)

        # current arrangement
        self.current_arrangement = []

    # ---- Name management ----
    def add_name(self):
        name = self.name_entry.get().strip()
        if not name:
            return
        if name in self.names:
            messagebox.showinfo("Info", f"{name} already in list")
            return
        self.names.append(name)
        self.names_listbox.insert(tk.END, name)
        self.name_entry.delete(0, tk.END)

    def import_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*")])
        if not path:
            return
        try:
            with open(path, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                added = 0
                for row in reader:
                    if not row:
                        continue
                    name = str(row[0]).strip()
                    if name and name not in self.names:
                        self.names.append(name)
                        self.names_listbox.insert(tk.END, name)
                        added += 1
            self.set_status(f"Imported {added} names from {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import CSV: {e}")

    def remove_selected(self):
        sel = self.names_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        name = self.names_listbox.get(idx)
        self.names_listbox.delete(idx)
        self.names.remove(name)
        self.set_status(f"Removed {name}")

    def clear_all(self):
        if messagebox.askyesno("Confirm", "Clear all names and constraints?"):
            self.names_listbox.delete(0, tk.END)
            self.names.clear()
            self.fixed.clear()
            self.avoid_pairs.clear()
            self.avoids_listbox.delete(0, tk.END)
            self.set_status("Cleared all data")

    # ---- Fixed & avoids ----
    def set_fixed(self):
        name = self.fixed_name_var.get().strip()
        if not name:
            messagebox.showinfo("Info", "Enter a name")
            return
        if name not in self.names:
            messagebox.showerror("Error", f"{name} not in names list")
            return
        seat = int(self.fixed_seat_var.get())
        total = self.rows_var.get() * self.cols_var.get()
        if seat < 0 or seat >= total:
            messagebox.showerror("Error", f"Seat index must be between 0 and {total-1}")
            return
        # ensure no other name fixed to same seat
        for s, n in list(self.fixed.items()):
            if s == seat and n != name:
                messagebox.showerror("Error", f"Seat {seat} already fixed to {n}")
                return
        # remove prior fixed if exists for that name
        for s, n in list(self.fixed.items()):
            if n == name and s != seat:
                del self.fixed[s]
        self.fixed[seat] = name
        self.set_status(f"Fixed {name} -> seat {seat}")

    def clear_fixed(self):
        self.fixed.clear()
        self.set_status("Cleared fixed seats")

    def add_avoid(self):
        a = self.avoid_a_var.get().strip()
        b = self.avoid_b_var.get().strip()
        if not a or not b:
            return
        if a == b:
            messagebox.showinfo("Info", "Choose two different names")
            return
        if a not in self.names or b not in self.names:
            messagebox.showerror("Error", "Both names must be in the names list")
            return
        pair = frozenset((a, b))
        if pair in self.avoid_pairs:
            messagebox.showinfo("Info", "Pair already exists")
            return
        self.avoid_pairs.add(pair)
        self.avoids_listbox.insert(tk.END, f"{a}  -  {b}")
        self.set_status(f"Added avoid: {a} vs {b}")

    def clear_avoids(self):
        self.avoid_pairs.clear()
        self.avoids_listbox.delete(0, tk.END)
        self.set_status("Cleared avoid pairs")

    # ---- Generation logic ----
    def generate_arrangement(self):
        total_seats = self.rows_var.get() * self.cols_var.get()
        names = list(self.names)
        n_names = len(names)
        if n_names == 0:
            messagebox.showerror("Error", "No names to seat")
            return
        if n_names > total_seats:
            messagebox.showerror("Error", f"Not enough seats: {total_seats} seats for {n_names} names")
            return

        # Starting arrangement with empty seats
        seats = [None] * total_seats
        # place fixed
        for seat_idx, name in self.fixed.items():
            if seat_idx < 0 or seat_idx >= total_seats:
                messagebox.showerror("Error", f"Fixed seat {seat_idx} out of range")
                return
            seats[seat_idx] = name
            if name in names:
                names.remove(name)

        max_tries = max(1, self.max_tries_var.get())
        found = False
        arrangement = None
        for attempt in range(max_tries):
            random.shuffle(names)
            temp = seats.copy()
            i = 0
            # fill empty seats
            for idx in range(total_seats):
                if temp[idx] is None and i < len(names):
                    temp[idx] = names[i]
                    i += 1
            # check avoids
            if self.check_avoids(temp):
                arrangement = temp
                found = True
                break
        if not found:
            messagebox.showwarning("Warning", f"Could not find arrangement after {max_tries} tries")
            self.set_status("No valid arrangement found")
            return
        self.current_arrangement = arrangement
        self.display_arrangement(arrangement)
        self.set_status(f"Arrangement generated (attempt {attempt+1})")

    def check_avoids(self, arrangement):
        # compute adjacency map
        rows = self.rows_var.get()
        cols = self.cols_var.get()
        total = rows * cols
        for r in range(rows):
            for c in range(cols):
                idx = r * cols + c
                name = arrangement[idx]
                if not name:
                    continue
                # neighbors
                neighbors = []
                for dr, dc in ((-1,0),(1,0),(0,-1),(0,1)):
                    rr, cc = r+dr, c+dc
                    if 0 <= rr < rows and 0 <= cc < cols:
                        nidx = rr*cols + cc
                        neighbor = arrangement[nidx]
                        if neighbor:
                            neighbors.append(neighbor)
                for nb in neighbors:
                    if frozenset((name, nb)) in self.avoid_pairs:
                        return False
        return True

    # ---- Display ----
    def display_arrangement(self, arr):
        # textual
        self.output_text.delete(1.0, tk.END)
        for i, name in enumerate(arr):
            self.output_text.insert(tk.END, f"{i}: {name or ''}\n")
        # redraw grid
        self.redraw_grid()

    def redraw_grid(self, event=None):
        self.grid_canvas.delete("all")
        rows = self.rows_var.get()
        cols = self.cols_var.get()
        if rows <=0 or cols <=0:
            return
        w = self.grid_canvas.winfo_width()
        h = self.grid_canvas.winfo_height()
        cell_w = w / cols
        cell_h = h / rows
        arr = self.current_arrangement if self.current_arrangement else [None]*(rows*cols)
        for r in range(rows):
            for c in range(cols):
                idx = r*cols + c
                x0 = c*cell_w
                y0 = r*cell_h
                x1 = x0 + cell_w
                y1 = y0 + cell_h
                self.grid_canvas.create_rectangle(x0, y0, x1, y1, width=1)
                name = arr[idx] if idx < len(arr) else None
                display = name if name else ""
                self.grid_canvas.create_text((x0+x1)/2, (y0+y1)/2, text=display, anchor=tk.CENTER)
                # mark fixed seats with small dot
                if idx in self.fixed:
                    self.grid_canvas.create_oval(x1-12, y0+4, x1-4, y0+12, fill="black")

    # ---- Save/Load ----
    def save_csv(self):
        if not self.current_arrangement:
            messagebox.showinfo("Info", "No arrangement to save")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if not path:
            return
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["seat_index","name"])
                for i, name in enumerate(self.current_arrangement):
                    writer.writerow([i, name or ""])
            self.set_status(f"Saved arrangement to {os.path.basename(path)}")
            messagebox.showinfo("Saved", f"Arrangement saved to {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save CSV: {e}")

    # ---- Utilities ----
    def set_status(self, msg):
        self.status_var.set(msg)


if __name__ == '__main__':
    app = SeatingGeneratorApp()
    app.mainloop()

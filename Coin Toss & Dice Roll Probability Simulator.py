"""
Coin Toss & Dice Roll Probability Simulator
Single-file tkinter desktop application.

Features:
- Simulate biased/unbiased coin tosses and n-sided dice rolls
- Choose number of trials, coin bias (probability of Heads), number of dice and sides
- Run simulation and view counts, empirical probabilities, and simple bar charts drawn on a Tkinter Canvas
- Live progress for long simulations with a progress bar
- Export results to CSV

Run: save this file as coin_dice_simulator.py and run `python coin_dice_simulator.py`.
Requires: standard Python 3 (no external packages required)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import csv
import threading
import time

class SimulatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Coin Toss & Dice Roll Probability Simulator")
        self.geometry("900x620")
        self.minsize(760, 520)

        self._build_ui()

        # Simulation state
        self.results = {}
        self._stop_sim = False

    def _build_ui(self):
        # Top: controls
        ctrl_frame = ttk.LabelFrame(self, text="Simulation Controls", padding=10)
        ctrl_frame.pack(fill="x", padx=10, pady=8)

        # Simulation type
        ttk.Label(ctrl_frame, text="Simulate:").grid(row=0, column=0, sticky="w")
        self.sim_type = tk.StringVar(value="coin")
        ttk.Radiobutton(ctrl_frame, text="Coin Toss", variable=self.sim_type, value="coin", command=self._toggle_options).grid(row=0, column=1, sticky="w")
        ttk.Radiobutton(ctrl_frame, text="Dice Roll", variable=self.sim_type, value="dice", command=self._toggle_options).grid(row=0, column=2, sticky="w")
        ttk.Radiobutton(ctrl_frame, text="Both", variable=self.sim_type, value="both", command=self._toggle_options).grid(row=0, column=3, sticky="w")

        # Number of trials
        ttk.Label(ctrl_frame, text="Trials:").grid(row=1, column=0, sticky="w", pady=(8,0))
        self.trials_var = tk.IntVar(value=1000)
        self.trials_spin = ttk.Spinbox(ctrl_frame, from_=1, to=10000000, textvariable=self.trials_var, width=12)
        self.trials_spin.grid(row=1, column=1, sticky="w", pady=(8,0))

        # Coin options
        self.coin_frame = ttk.Frame(ctrl_frame)
        self.coin_frame.grid(row=2, column=0, columnspan=4, sticky="w", pady=(8,0))
        ttk.Label(self.coin_frame, text="Coin bias (P(Heads)):").grid(row=0, column=0, sticky="w")
        self.coin_bias = tk.DoubleVar(value=0.5)
        self.coin_spin = ttk.Spinbox(self.coin_frame, from_=0.0, to=1.0, increment=0.01, textvariable=self.coin_bias, width=8)
        self.coin_spin.grid(row=0, column=1, sticky="w", padx=(6,10))

        # Dice options
        self.dice_frame = ttk.Frame(ctrl_frame)
        self.dice_frame.grid(row=3, column=0, columnspan=4, sticky="w", pady=(8,0))
        ttk.Label(self.dice_frame, text="Dice sides:").grid(row=0, column=0, sticky="w")
        self.dice_sides = tk.IntVar(value=6)
        ttk.Spinbox(self.dice_frame, from_=2, to=100, textvariable=self.dice_sides, width=6).grid(row=0, column=1, sticky="w", padx=(6,10))
        ttk.Label(self.dice_frame, text="Number of dice per roll:").grid(row=0, column=2, sticky="w")
        self.dice_count = tk.IntVar(value=1)
        ttk.Spinbox(self.dice_frame, from_=1, to=10, textvariable=self.dice_count, width=6).grid(row=0, column=3, sticky="w", padx=(6,0))

        # Buttons
        btn_frame = ttk.Frame(ctrl_frame)
        btn_frame.grid(row=4, column=0, columnspan=4, pady=(10,0), sticky="e")
        self.run_btn = ttk.Button(btn_frame, text="Run Simulation", command=self.run_simulation)
        self.run_btn.pack(side="left", padx=(0,6))
        self.stop_btn = ttk.Button(btn_frame, text="Stop", command=self._stop, state="disabled")
        self.stop_btn.pack(side="left", padx=(0,6))
        self.export_btn = ttk.Button(btn_frame, text="Export CSV", command=self.export_csv, state="disabled")
        self.export_btn.pack(side="left")

        # Progress bar
        self.progress = ttk.Progressbar(self, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(padx=14, pady=(2,8), anchor="e")

        # Middle: results and charts
        mid_frame = ttk.Frame(self)
        mid_frame.pack(fill="both", expand=True, padx=10, pady=6)
        mid_frame.columnconfigure(0, weight=1)
        mid_frame.columnconfigure(1, weight=1)
        mid_frame.rowconfigure(0, weight=1)

        # Left: Text results
        results_frame = ttk.LabelFrame(mid_frame, text="Results", padding=8)
        results_frame.grid(row=0, column=0, sticky="nsew", padx=(0,6))
        results_frame.rowconfigure(0, weight=1)
        results_frame.columnconfigure(0, weight=1)

        self.results_text = tk.Text(results_frame, state="disabled", wrap="word")
        self.results_text.grid(row=0, column=0, sticky="nsew")
        results_scroll = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_text.yview)
        results_scroll.grid(row=0, column=1, sticky="ns")
        self.results_text.configure(yscrollcommand=results_scroll.set)

        # Right: Canvas charts
        chart_frame = ttk.LabelFrame(mid_frame, text="Charts", padding=8)
        chart_frame.grid(row=0, column=1, sticky="nsew", padx=(6,0))
        chart_frame.rowconfigure(0, weight=1)
        chart_frame.columnconfigure(0, weight=1)

        self.chart_canvas = tk.Canvas(chart_frame, background="#ffffff")
        self.chart_canvas.grid(row=0, column=0, sticky="nsew")

        # Bottom: quick help
        help_frame = ttk.LabelFrame(self, text="How to use", padding=8)
        help_frame.pack(fill="x", padx=10, pady=(0,10))
        help_label = ttk.Label(help_frame, text=("Choose simulation type, set trials and options, then click Run Simulation. "
                                                "Results will show counts and simple bar charts. Export to CSV if needed."))
        help_label.pack()

        self._toggle_options()

    def _toggle_options(self):
        t = self.sim_type.get()
        if t == "coin":
            self.coin_frame.grid()
            self.dice_frame.grid_remove()
        elif t == "dice":
            self.coin_frame.grid_remove()
            self.dice_frame.grid()
        else:
            self.coin_frame.grid()
            self.dice_frame.grid()

    def run_simulation(self):
        try:
            trials = int(self.trials_var.get())
            if trials <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Invalid trials", "Please enter a positive integer for trials.")
            return

        # Prepare
        self.run_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.export_btn.config(state="disabled")
        self.results_text.config(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.config(state="disabled")
        self.chart_canvas.delete("all")
        self.progress['value'] = 0
        self.results = {}
        self._stop_sim = False

        # Run in background thread to keep UI responsive
        thread = threading.Thread(target=self._simulate_thread, args=(trials,))
        thread.daemon = True
        thread.start()

    def _stop(self):
        self._stop_sim = True
        self.stop_btn.config(state="disabled")

    def _simulate_thread(self, trials):
        sim_type = self.sim_type.get()
        coin_p = float(self.coin_bias.get()) if sim_type in ("coin", "both") else None
        sides = int(self.dice_sides.get()) if sim_type in ("dice", "both") else None
        dice_count = int(self.dice_count.get()) if sim_type in ("dice", "both") else None

        # Initialize counters
        coin_counts = {"Heads": 0, "Tails": 0}
        dice_counts = {}  # key: sum or face

        for i in range(trials):
            if self._stop_sim:
                break

            if sim_type in ("coin", "both"):
                # single toss per trial for coin simulation
                r = random.random()
                if r < coin_p:
                    coin_counts["Heads"] += 1
                else:
                    coin_counts["Tails"] += 1

            if sim_type in ("dice", "both"):
                # roll dice_count dice and sum results
                total = 0
                for _ in range(dice_count):
                    total += random.randint(1, sides)
                dice_counts[total] = dice_counts.get(total, 0) + 1

            # update progress every so often
            if (i + 1) % max(1, trials // 100) == 0 or i == trials - 1:
                progress_val = int((i + 1) / trials * 100)
                self._safe_update_progress(progress_val)

        # store and show results
        self.results['coin'] = coin_counts
        self.results['dice'] = dice_counts
        self._safe_finish()

    def _safe_update_progress(self, val):
        try:
            self.progress['value'] = val
            self.update_idletasks()
        except Exception:
            pass

    def _safe_finish(self):
        # run on main thread
        self.after(0, self._finish_simulation)

    def _finish_simulation(self):
        self.run_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.export_btn.config(state="normal")
        self.progress['value'] = 100
        self._render_results()

    def _render_results(self):
        self.results_text.config(state="normal")
        self.results_text.delete("1.0", "end")

        sim_type = self.sim_type.get()

        if sim_type in ("coin", "both"):
            coin_counts = self.results.get('coin', {"Heads":0, "Tails":0})
            total = coin_counts.get('Heads',0) + coin_counts.get('Tails',0)
            self.results_text.insert("end", f"Coin tosses (total = {total})\n")
            if total > 0:
                ph = coin_counts.get('Heads',0)/total
                pt = coin_counts.get('Tails',0)/total
                self.results_text.insert("end", f"  Heads: {coin_counts.get('Heads',0)} ({ph:.4f})\n")
                self.results_text.insert("end", f"  Tails: {coin_counts.get('Tails',0)} ({pt:.4f})\n")
            else:
                self.results_text.insert("end", "  No coin data.\n")
            self.results_text.insert("end", "\n")

        if sim_type in ("dice", "both"):
            dice_counts = self.results.get('dice', {})
            total = sum(dice_counts.values())
            self.results_text.insert("end", f"Dice rolls (trials = {total})\n")
            if total > 0:
                # show sorted distribution
                for k in sorted(dice_counts.keys()):
                    self.results_text.insert("end", f"  {k}: {dice_counts[k]} ({dice_counts[k]/total:.4f})\n")
            else:
                self.results_text.insert("end", "  No dice data.\n")
            self.results_text.insert("end", "\n")

        self.results_text.config(state="disabled")

        # draw charts
        self.chart_canvas.delete("all")
        w = self.chart_canvas.winfo_width()
        h = self.chart_canvas.winfo_height()
        if w < 100 or h < 80:
            # schedule redraw when widget has size
            self.after(150, self._render_results)
            return

        pad = 20
        chart_w = max(200, w - pad*2)
        chart_h = max(120, h - pad*2)

        # If both, draw two small charts vertically
        charts = []
        if sim_type in ("coin", "both"):
            charts.append(('coin', self.results.get('coin', {})))
        if sim_type in ("dice", "both"):
            charts.append(('dice', self.results.get('dice', {})))

        n = len(charts)
        if n == 0:
            return

        section_h = chart_h // n
        for idx, (kind, data) in enumerate(charts):
            top = pad + idx * section_h
            left = pad
            bottom = top + section_h - 10
            right = left + chart_w
            # draw border
            self.chart_canvas.create_rectangle(left-2, top-2, right+2, bottom+2, outline="#ccc")

            if not data:
                self.chart_canvas.create_text((left+right)//2, (top+bottom)//2, text="No data to display")
                continue

            # normalize and draw bars
            items = sorted(data.items(), key=lambda x: x[0])
            keys = [str(k) for k, _ in items]
            vals = [v for _, v in items]
            total = sum(vals) if sum(vals) > 0 else 1
            maxv = max(vals)
            bar_gap = 8
            bar_w = max(12, (chart_w - (len(vals)+1)*bar_gap) / max(1, len(vals)))
            # baseline
            baseline = bottom - 30
            # labels area
            for i, (k, v) in enumerate(items):
                bx = left + bar_gap + i * (bar_w + bar_gap)
                by = baseline
                # height proportional
                bh = int((v / maxv) * (baseline - top - 20)) if maxv > 0 else 0
                self.chart_canvas.create_rectangle(bx, by-bh, bx+bar_w, by, fill="#4a90e2", outline="black")
                # value text
                self.chart_canvas.create_text(bx + bar_w/2, by-bh-10, text=str(v), anchor="s")
                # key label
                self.chart_canvas.create_text(bx + bar_w/2, bottom - 10, text=str(k), anchor="n")

            # chart title
            title = "Coin toss distribution" if kind == 'coin' else "Dice roll distribution (sum)"
            self.chart_canvas.create_text(left+6, top+8, anchor="nw", text=title, font=(None, 10, 'bold'))

    def export_csv(self):
        if not self.results:
            messagebox.showwarning("No data", "Run a simulation first before exporting.")
            return
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files','*.csv'), ('All files','*.*')])
        if not path:
            return
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Type', 'Key', 'Count'])
                coin = self.results.get('coin', {})
                for k, v in coin.items():
                    writer.writerow(['coin', k, v])
                dice = self.results.get('dice', {})
                for k, v in sorted(dice.items()):
                    writer.writerow(['dice', k, v])
            messagebox.showinfo("Saved", f"Results exported to {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save CSV: {e}")

if __name__ == '__main__':
    app = SimulatorApp()
    app.mainloop()

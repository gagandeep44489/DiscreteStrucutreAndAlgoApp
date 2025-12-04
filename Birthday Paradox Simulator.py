"""
Birthday Paradox Simulator
Single-file Python desktop application using Tkinter and matplotlib.

Features:
- Run Monte Carlo simulations of the birthday paradox
- Choose number of people per group and number of trials
- Run batched simulations and show estimated probability that at least two people share a birthday
- Compare Monte Carlo estimate to theoretical probability
- Show histogram of counts of shared birthdays per trial
- Export results to CSV

Requirements:
- Python 3.x
- tkinter (included in standard Python)
- matplotlib (for embedding histogram) -> pip install matplotlib

Save as birthday_simulator.py and run: python birthday_simulator.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import random
import math
import csv
import threading
import time

# Optional widget embedding
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except Exception:
    MATPLOTLIB_AVAILABLE = False

DEFAULT_DAYS = 365

class BirthdaySimulatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Birthday Paradox Simulator")
        self.geometry("900x620")
        self.resizable(True, True)

        # Simulation data
        self.num_people = tk.IntVar(value=23)
        self.trials = tk.IntVar(value=5000)
        self.days_in_year = tk.IntVar(value=DEFAULT_DAYS)
        self.random_seed = tk.StringVar(value="")

        self.running = False
        self.results = []  # list of number of collisions per trial

        self.create_widgets()

    def create_widgets(self):
        main = ttk.Frame(self, padding=8)
        main.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(main)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0,8))

        controls = ttk.LabelFrame(left, text="Simulation Controls")
        controls.pack(fill=tk.X, pady=(0,8))

        ttk.Label(controls, text="People per group:").grid(row=0, column=0, sticky=tk.W, padx=4, pady=6)
        ttk.Spinbox(controls, from_=2, to=365, textvariable=self.num_people, width=6).grid(row=0, column=1, padx=4)

        ttk.Label(controls, text="Days in year:").grid(row=1, column=0, sticky=tk.W, padx=4, pady=6)
        ttk.Spinbox(controls, from_=1, to=1000, textvariable=self.days_in_year, width=6).grid(row=1, column=1, padx=4)

        ttk.Label(controls, text="Trials:").grid(row=2, column=0, sticky=tk.W, padx=4, pady=6)
        ttk.Entry(controls, textvariable=self.trials, width=10).grid(row=2, column=1, padx=4)

        ttk.Label(controls, text="Random seed (optional):").grid(row=3, column=0, sticky=tk.W, padx=4, pady=6)
        ttk.Entry(controls, textvariable=self.random_seed, width=12).grid(row=3, column=1, padx=4)

        self.run_btn = ttk.Button(controls, text="Run Simulation", command=self.run_simulation_thread)
        self.run_btn.grid(row=4, column=0, columnspan=2, sticky=tk.EW, padx=4, pady=(8,4))

        self.stop_btn = ttk.Button(controls, text="Stop", command=self.stop_simulation, state=tk.DISABLED)
        self.stop_btn.grid(row=5, column=0, columnspan=2, sticky=tk.EW, padx=4)

        ttk.Separator(left, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)

        actions = ttk.LabelFrame(left, text="Actions")
        actions.pack(fill=tk.X)
        ttk.Button(actions, text="Export CSV", command=self.export_csv).pack(fill=tk.X, padx=6, pady=4)
        ttk.Button(actions, text="Clear Results", command=self.clear_results).pack(fill=tk.X, padx=6, pady=4)

        # Right area: results and plot
        right = ttk.Frame(main)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        top_stats = ttk.Frame(right)
        top_stats.pack(fill=tk.X)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(top_stats, textvariable=self.status_var).pack(anchor=tk.W)

        stats_frame = ttk.LabelFrame(right, text="Results")
        stats_frame.pack(fill=tk.X, pady=6)

        ttk.Label(stats_frame, text="Estimated probability (>= 1 shared birthday):").grid(row=0, column=0, sticky=tk.W, padx=6, pady=4)
        self.estimate_var = tk.StringVar(value="-")
        ttk.Label(stats_frame, textvariable=self.estimate_var, width=12).grid(row=0, column=1, sticky=tk.W)

        ttk.Label(stats_frame, text="Theoretical probability:").grid(row=1, column=0, sticky=tk.W, padx=6, pady=4)
        self.theory_var = tk.StringVar(value="-")
        ttk.Label(stats_frame, textvariable=self.theory_var, width=12).grid(row=1, column=1, sticky=tk.W)

        ttk.Label(stats_frame, text="Average collisions per trial:").grid(row=2, column=0, sticky=tk.W, padx=6, pady=4)
        self.avg_collisions_var = tk.StringVar(value="-")
        ttk.Label(stats_frame, textvariable=self.avg_collisions_var, width=12).grid(row=2, column=1, sticky=tk.W)

        # histogram area
        hist_frame = ttk.LabelFrame(right, text="Histogram of number of shared birthdays per trial")
        hist_frame.pack(fill=tk.BOTH, expand=True, pady=(6,0))

        if MATPLOTLIB_AVAILABLE:
            self.fig = Figure(figsize=(5,3.5), dpi=100)
            self.ax = self.fig.add_subplot(111)
            self.ax.set_xlabel('Number of shared birthdays in a trial')
            self.ax.set_ylabel('Frequency')
            self.canvas = FigureCanvasTkAgg(self.fig, master=hist_frame)
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            lbl = ttk.Label(hist_frame, text="matplotlib not available — install matplotlib to see histogram")
            lbl.pack(padx=6, pady=6)

        # output log
        out_frame = ttk.LabelFrame(right, text="Log")
        out_frame.pack(fill=tk.X)
        self.log_text = tk.Text(out_frame, height=6)
        self.log_text.pack(fill=tk.X, padx=6, pady=6)

    # ---- Simulation logic ----
    def run_simulation_thread(self):
        if self.running:
            return
        try:
            trials = int(self.trials.get())
            if trials <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "Enter a positive integer for trials")
            return
        people = int(self.num_people.get())
        days = int(self.days_in_year.get())
        if people <=1 or days <=0:
            messagebox.showerror("Error", "People must be >=2 and days must be >0")
            return
        seed = self.random_seed.get().strip()
        if seed != "":
            try:
                s = int(seed)
                random.seed(s)
            except Exception:
                random.seed(seed)

        # disable controls
        self.running = True
        self.run_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_var.set("Running simulation...")
        self.log_text.delete(1.0, tk.END)
        self.results = []

        # run in background thread to keep UI responsive
        t = threading.Thread(target=self._run_simulation, args=(people, days, trials), daemon=True)
        t.start()

    def _run_simulation(self, people, days, trials):
        start = time.time()
        collisions_counts = []
        for i in range(trials):
            if not self.running:
                break
            # generate birthdays
            birthdays = [random.randrange(days) for _ in range(people)]
            # count duplicates
            counts = len(birthdays) - len(set(birthdays))  # number of duplicate entries
            # for number of shared birthday pairs, there are more advanced counts, but this gives collisions count
            collisions_counts.append(counts)
            if (i+1) % max(1, trials//10) == 0:
                self._append_log(f"Progress: {i+1}/{trials} trials")
        self.running = False
        duration = time.time() - start
        self.results = collisions_counts
        # compute stats on main thread
        self.after(10, lambda: self._finalize_simulation(people, days, trials, duration))

    def _finalize_simulation(self, people, days, trials, duration):
        succeeded_trials = len(self.results)
        if succeeded_trials == 0:
            self.status_var.set("Stopped")
            self.run_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            return
        # probability estimate: fraction of trials with at least one collision
        with_collision = sum(1 for x in self.results if x > 0)
        prob_est = with_collision / succeeded_trials
        avg_collisions = sum(self.results) / succeeded_trials

        prob_theory = self.theoretical_probability(people, days)

        self.estimate_var.set(f"{prob_est:.4f}")
        self.theory_var.set(f"{prob_theory:.4f}")
        self.avg_collisions_var.set(f"{avg_collisions:.3f}")
        self.status_var.set(f"Completed {succeeded_trials}/{trials} trials in {duration:.2f}s")
        self._append_log(f"Completed: estimated probability {prob_est:.4f}, theoretical {prob_theory:.4f}")

        # draw histogram
        if MATPLOTLIB_AVAILABLE:
            self.ax.clear()
            self.ax.hist(self.results, bins=range(min(self.results or [0]), max(self.results or [0])+2))
            self.ax.set_xlabel('Number of shared birthdays in a trial')
            self.ax.set_ylabel('Frequency')
            self.canvas.draw()

        self.run_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def stop_simulation(self):
        if not self.running:
            return
        self.running = False
        self.status_var.set("Stopping...")
        self._append_log("Requested stop — simulation will halt shortly")

    def theoretical_probability(self, people, days):
        # P(no shared birthdays) = product_{k=0 to n-1} (days - k)/days
        if people > days:
            return 1.0
        prob_no_match = 1.0
        for k in range(people):
            prob_no_match *= (days - k) / days
        return 1.0 - prob_no_match

    # ---- Utilities ----
    def _append_log(self, text):
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)

    def export_csv(self):
        if not self.results:
            messagebox.showinfo("Info", "No results to export")
            return
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files','*.csv')])
        if not path:
            return
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['trial_index','num_collisions'])
                for i, val in enumerate(self.results):
                    writer.writerow([i+1, val])
            messagebox.showinfo('Saved', f'Saved results to {path}')
            self._append_log(f'Saved results to {path}')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to save CSV: {e}')

    def clear_results(self):
        if messagebox.askyesno('Confirm', 'Clear simulation results?'):
            self.results = []
            self.estimate_var.set('-')
            self.theory_var.set('-')
            self.avg_collisions_var.set('-')
            if MATPLOTLIB_AVAILABLE:
                self.ax.clear()
                self.canvas.draw()
            self.log_text.delete(1.0, tk.END)
            self.status_var.set('Ready')


if __name__ == '__main__':
    app = BirthdaySimulatorApp()
    app.mainloop()

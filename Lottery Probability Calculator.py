"""
Lottery Probability Calculator
Single-file Tkinter desktop application.

Features:
- Calculate exact combinatorial probabilities for lottery games ("choose k of n")
- Compute odds of matching exactly m numbers, at least m numbers, or jackpot (all k)
- Allow user to input total pool size (n), numbers picked (k), and number of drawn numbers (d)
- Provide hypergeometric probability formula and display as fraction and decimal
- Optional Monte Carlo simulator for empirical verification
- Export results to CSV

Run: save this file as lottery_probability_calculator.py and run `python lottery_probability_calculator.py`.
Requires: Python 3 (standard library only)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from math import comb
import random
import csv
import threading


def hypergeom_prob(total_pool, draw_count, picks, match_count):
    """Probability of matching exactly match_count numbers when user picks 'picks' numbers
    from total_pool, and the lottery draws 'draw_count' winning numbers.
    Formula: C(picks, match_count) * C(total_pool - picks, draw_count - match_count) / C(total_pool, draw_count)
    """
    if match_count < 0 or match_count > picks or match_count > draw_count:
        return 0.0
    if draw_count - match_count > total_pool - picks:
        return 0.0
    numerator = comb(picks, match_count) * comb(total_pool - picks, draw_count - match_count)
    denom = comb(total_pool, draw_count)
    return numerator / denom


class LotteryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Lottery Probability Calculator")
        self.geometry("820x560")
        self.minsize(760, 480)
        self._build_ui()
        self.sim_thread = None
        self._stop_sim = False

    def _build_ui(self):
        main = ttk.Frame(self, padding=10)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=1)

        top = ttk.LabelFrame(main, text="Lottery Parameters", padding=8)
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(1, weight=1)

        ttk.Label(top, text="Total pool (n):").grid(row=0, column=0, sticky="w")
        self.total_var = tk.IntVar(value=49)
        ttk.Spinbox(top, from_=1, to=1000, textvariable=self.total_var, width=8).grid(row=0, column=1, sticky="w")

        ttk.Label(top, text="Numbers you pick (k):").grid(row=1, column=0, sticky="w")
        self.pick_var = tk.IntVar(value=6)
        ttk.Spinbox(top, from_=1, to=50, textvariable=self.pick_var, width=8).grid(row=1, column=1, sticky="w")

        ttk.Label(top, text="Numbers drawn by lottery (d):").grid(row=2, column=0, sticky="w")
        self.draw_var = tk.IntVar(value=6)
        ttk.Spinbox(top, from_=1, to=50, textvariable=self.draw_var, width=8).grid(row=2, column=1, sticky="w")

        ttk.Label(top, text="Match at least (m):").grid(row=3, column=0, sticky="w")
        self.match_atleast_var = tk.IntVar(value=3)
        ttk.Spinbox(top, from_=0, to=50, textvariable=self.match_atleast_var, width=8).grid(row=3, column=1, sticky="w")

        calc_btn = ttk.Button(top, text="Calculate Probabilities", command=self.calculate)
        calc_btn.grid(row=0, column=2, rowspan=2, padx=8)

        sim_btn = ttk.Button(top, text="Run Monte Carlo Simulation", command=self._start_simulation)
        sim_btn.grid(row=2, column=2, rowspan=2, padx=8)

        export_btn = ttk.Button(top, text="Export Results (CSV)", command=self.export_csv)
        export_btn.grid(row=0, column=3, rowspan=2, padx=8)

        # Results area
        res_frame = ttk.LabelFrame(main, text="Results", padding=8)
        res_frame.grid(row=1, column=0, sticky="nsew", pady=8)
        res_frame.columnconfigure(0, weight=1)
        res_frame.rowconfigure(0, weight=1)

        self.results_text = tk.Text(res_frame, state="disabled", wrap="word")
        self.results_text.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(res_frame, orient="vertical", command=self.results_text.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.results_text.configure(yscrollcommand=scroll.set)

        # Simulation controls
        sim_frame = ttk.LabelFrame(main, text="Simulation Options", padding=8)
        sim_frame.grid(row=2, column=0, sticky="ew")
        sim_frame.columnconfigure(1, weight=1)

        ttk.Label(sim_frame, text="Trials:").grid(row=0, column=0, sticky="w")
        self.trials_var = tk.IntVar(value=10000)
        ttk.Spinbox(sim_frame, from_=1, to=10_000_000, textvariable=self.trials_var, width=12).grid(row=0, column=1, sticky="w")

        self.sim_progress = ttk.Progressbar(sim_frame, orient="horizontal", length=300, mode="determinate")
        self.sim_progress.grid(row=0, column=2, padx=8)

        self.stop_sim_btn = ttk.Button(sim_frame, text="Stop", command=self._stop_simulation, state="disabled")
        self.stop_sim_btn.grid(row=0, column=3, padx=4)

        # Help / formulas
        help_frame = ttk.LabelFrame(main, text="Formula & Info", padding=8)
        help_frame.grid(row=3, column=0, sticky="ew", pady=8)
        help_label = ttk.Label(help_frame, text=("Exact probability formula (hypergeometric):\n" 
                                                 "P(X = m) = C(k, m) * C(n - k, d - m) / C(n, d)\n" 
                                                 "Where: n = total pool, k = your picks, d = drawn numbers, m = matches"))
        help_label.pack()

    def _append_result(self, text):
        self.results_text.config(state="normal")
        self.results_text.insert("end", text + "\n")
        self.results_text.see("end")
        self.results_text.config(state="disabled")

    def calculate(self):
        n = int(self.total_var.get())
        k = int(self.pick_var.get())
        d = int(self.draw_var.get())
        m_min = int(self.match_atleast_var.get())

        if not (1 <= k <= n and 1 <= d <= n):
            messagebox.showerror("Invalid parameters", "Please ensure 1 <= k <= n and 1 <= d <= n")
            return

        self.results_text.config(state="normal")
        self.results_text.delete("1.0", "end")

        # exact probabilities for 0..min(k,d)
        max_m = min(k, d)
        self.probs_exact = []
        for m in range(0, max_m + 1):
            p = hypergeom_prob(n, d, k, m)
            self.probs_exact.append((m, p))
            frac = f"{p:.12f}" if p > 0 else "0"
            odds = f"1 in {1/p:.0f}" if p > 0 else "Inf"
            self._append_result(f"P(exactly {m} matches) = {frac}  (odds {odds})")

        # cumulative probabilities >= m_min
        cum = sum(p for m, p in self.probs_exact if m >= m_min)
        self._append_result("")
        self._append_result(f"P(at least {m_min} matches) = {cum:.12f}  (1 in {1/cum:.0f} if >0)" if cum>0 else f"P(at least {m_min} matches) = 0")

        # jackpot probability (match all your picks if k==d, else matching k if d>=k)
        jackpot_m = k if k <= d else None
        if jackpot_m is not None:
            jackp = dict(self.probs_exact).get(jackpot_m, 0.0)
            self._append_result(f"\nJackpot (match all {jackpot_m}) probability = {jackp:.12f}  (1 in {1/jackp:.0f})" if jackp>0 else "\nJackpot probability = 0")

        self.results_text.config(state="disabled")

    def _start_simulation(self):
        if self.sim_thread and self.sim_thread.is_alive():
            messagebox.showinfo("Simulation", "Simulation already running")
            return
        try:
            trials = int(self.trials_var.get())
            if trials <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Invalid trials", "Enter a positive integer for trials")
            return

        # ensure parameters valid
        n = int(self.total_var.get())
        k = int(self.pick_var.get())
        d = int(self.draw_var.get())
        if not (1 <= k <= n and 1 <= d <= n):
            messagebox.showerror("Invalid parameters", "Please ensure 1 <= k <= n and 1 <= d <= n")
            return

        # prepare
        self._stop_sim = False
        self.sim_progress['value'] = 0
        self.stop_sim_btn.config(state="normal")
        self.sim_thread = threading.Thread(target=self._simulate, args=(trials, n, k, d), daemon=True)
        self.sim_thread.start()

    def _simulate(self, trials, n, k, d):
        # counts for exact matches
        counts = {m: 0 for m in range(0, min(k, d) + 1)}
        for i in range(trials):
            if self._stop_sim:
                break
            # draw winning numbers
            winning = set(random.sample(range(1, n+1), d))
            # player picks k numbers (random)
            picks = set(random.sample(range(1, n+1), k))
            m = len(winning & picks)
            counts[m] += 1
            if (i+1) % max(1, trials//200) == 0 or i == trials-1:
                self.after(0, self.sim_progress.step, 100/trials * (max(1, trials//200)))
        # finish
        # normalize progress
        self.after(0, lambda: self.sim_progress.configure(value=100))
        # show results
        self.after(0, self._show_sim_results, counts, trials)
        self.after(0, lambda: self.stop_sim_btn.config(state="disabled"))

    def _show_sim_results(self, counts, trials):
        self.results_text.config(state="normal")
        self.results_text.insert("end", "\n--- Simulation Results ---\n")
        for m in sorted(counts.keys()):
            cnt = counts[m]
            p = cnt / trials
            self.results_text.insert("end", f"Match exactly {m}: {cnt} / {trials}  -> {p:.6f} (1 in {1/p:.0f} if p>0)\n")
        self.results_text.see("end")
        self.results_text.config(state="disabled")

    def _stop_simulation(self):
        self._stop_sim = True
        self.stop_sim_btn.config(state="disabled")

    def export_csv(self):
        # Export last calculated exact probabilities if available
        try:
            probs = getattr(self, 'probs_exact', None)
            if not probs:
                messagebox.showwarning("No data", "Run calculations first before exporting")
                return
            path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV','*.csv')])
            if not path:
                return
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['match_count','probability_decimal','odds_1_in'])
                for m, p in probs:
                    o = f"{1/p:.0f}" if p>0 else 'Inf'
                    writer.writerow([m, f"{p:.12f}", o])
            messagebox.showinfo("Saved", f"Saved results to {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV: {e}")


if __name__ == '__main__':
    app = LotteryApp()
    app.mainloop()

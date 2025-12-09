#!/usr/bin/env python3
"""
monte_carlo_tool.py
A single-file Tkinter desktop app for running Monte Carlo simulations:
- Estimate pi
- Estimate a definite integral
- Price a European option (Monte Carlo)
Requirements: Python 3.8+, numpy, matplotlib
Install dependencies:
    pip install numpy matplotlib
Run:
    python monte_carlo_tool.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
import io
import math

# -------------------------
# Monte Carlo implementations
# -------------------------

def mc_estimate_pi(n):
    """Estimate pi by sampling n points in the unit square and counting those inside the quarter circle."""
    # vectorized sampling
    x = np.random.random(n)
    y = np.random.random(n)
    inside = (x*x + y*y) <= 1.0
    count = inside.sum()
    estimate = 4.0 * count / n
    # standard error approx: se = 4 * sqrt(p(1-p)/n) where p = count/n
    p = count / n
    se = 4.0 * math.sqrt(p * (1 - p) / n) if n > 0 else float('nan')
    samples = (x, y, inside)
    return estimate, se, samples

def mc_integral_estimate(func, a, b, n):
    """Estimate integral of func over [a, b] using Monte Carlo sampling."""
    x = np.random.random(n) * (b - a) + a
    fx = func(x)
    estimate = (b - a) * fx.mean()
    se = (b - a) * fx.std(ddof=1) / math.sqrt(n) if n > 1 else float('nan')
    samples = (x, fx)
    return estimate, se, samples

def mc_european_option_price(S0, K, r, sigma, T, n, option_type="call"):
    """
    Price a European option using plain Monte Carlo of terminal stock price
    under Geometric Brownian Motion:
      S_T = S0 * exp((r - 0.5*sigma^2)*T + sigma*sqrt(T)*Z)
    """
    Z = np.random.normal(size=n)
    ST = S0 * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * Z)
    if option_type == "call":
        payoffs = np.maximum(ST - K, 0.0)
    else:
        payoffs = np.maximum(K - ST, 0.0)
    discounted = np.exp(-r * T) * payoffs
    estimate = discounted.mean()
    se = discounted.std(ddof=1) / math.sqrt(n) if n > 1 else float('nan')
    samples = (ST, discounted)
    return estimate, se, samples

# Predefined functions for integral estimation
def f_x2(x): return x**2
def f_sin(x): return np.sin(x)
def f_exp(x): return np.exp(x)

FUNC_MAP = {
    "x^2": f_x2,
    "sin(x)": f_sin,
    "exp(x)": f_exp
}

# -------------------------
# GUI App
# -------------------------

class MonteCarloApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Monte Carlo Simulation Tool")
        self.geometry("950x650")
        self.resizable(True, True)
        self._create_widgets()
        self.last_samples = None  # store for export / plot

    def _create_widgets(self):
        # Top controls frame
        frm_top = ttk.Frame(self, padding=8)
        frm_top.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(frm_top, text="Simulation:").grid(row=0, column=0, sticky="w")
        self.sim_choice = ttk.Combobox(frm_top, values=["Estimate π", "Integral", "European Option"], state="readonly", width=18)
        self.sim_choice.current(0)
        self.sim_choice.grid(row=0, column=1, padx=6, sticky="w")
        self.sim_choice.bind("<<ComboboxSelected>>", self._on_sim_select)

        ttk.Label(frm_top, text="Samples (n):").grid(row=0, column=2, sticky="w")
        self.n_entry = ttk.Entry(frm_top, width=12)
        self.n_entry.insert(0, "100000")
        self.n_entry.grid(row=0, column=3, padx=6, sticky="w")

        self.btn_run = ttk.Button(frm_top, text="Run", command=self._on_run)
        self.btn_run.grid(row=0, column=4, padx=6)

        self.progress = ttk.Progressbar(frm_top, orient="horizontal", mode="determinate", length=200)
        self.progress.grid(row=0, column=5, padx=8)

        # Parameter frame (changes depending on sim)
        self.param_frame = ttk.LabelFrame(self, text="Parameters", padding=8)
        self.param_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=8)
        self._build_param_widgets()

        # Middle: plot and results
        middle = ttk.Frame(self)
        middle.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Matplotlib figure
        self.fig = Figure(figsize=(6.5,4.5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Simulation Output")
        self.canvas = FigureCanvasTkAgg(self.fig, master=middle)
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Right column: results and export
        right = ttk.Frame(middle, width=280)
        right.pack(side=tk.RIGHT, fill=tk.Y)
        ttk.Label(right, text="Results:", font=("TkDefaultFont", 11, "bold")).pack(anchor="nw", pady=(4,2))
        self.results_text = tk.Text(right, width=36, height=12, wrap="word")
        self.results_text.pack(fill=tk.Y, pady=(0,8))
        self.results_text.insert("end", "Run a simulation and results will appear here.\n")
        self.results_text.config(state=tk.DISABLED)

        btns = ttk.Frame(right)
        btns.pack(fill=tk.X, pady=6)
        ttk.Button(btns, text="Save Plot PNG", command=self._save_plot).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text="Export Samples CSV", command=self._export_csv).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text="Clear", command=self._clear).pack(side=tk.LEFT, padx=6)

        # Status bar
        self.status = ttk.Label(self, text="Ready", anchor="w")
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def _build_param_widgets(self):
        # Remove any children
        for child in self.param_frame.winfo_children():
            child.destroy()

        sim = self.sim_choice.get()
        if sim == "Estimate π":
            ttk.Label(self.param_frame, text="No extra parameters for π estimator.").grid(row=0, column=0, sticky="w")
        elif sim == "Integral":
            ttk.Label(self.param_frame, text="Function:").grid(row=0, column=0, sticky="w")
            self.func_choice = ttk.Combobox(self.param_frame, values=list(FUNC_MAP.keys()), state="readonly", width=12)
            self.func_choice.current(0)
            self.func_choice.grid(row=0, column=1, padx=6)

            ttk.Label(self.param_frame, text="a:").grid(row=0, column=2, sticky="w")
            self.a_entry = ttk.Entry(self.param_frame, width=8)
            self.a_entry.insert(0, "0.0")
            self.a_entry.grid(row=0, column=3, padx=4)

            ttk.Label(self.param_frame, text="b:").grid(row=0, column=4, sticky="w")
            self.b_entry = ttk.Entry(self.param_frame, width=8)
            self.b_entry.insert(0, "1.0")
            self.b_entry.grid(row=0, column=5, padx=4)

        elif sim == "European Option":
            # S0, K, r, sigma, T, type
            ttk.Label(self.param_frame, text="S0:").grid(row=0, column=0, sticky="w")
            self.s0_entry = ttk.Entry(self.param_frame, width=8); self.s0_entry.insert(0, "100")
            self.s0_entry.grid(row=0, column=1, padx=4)

            ttk.Label(self.param_frame, text="K:").grid(row=0, column=2, sticky="w")
            self.k_entry = ttk.Entry(self.param_frame, width=8); self.k_entry.insert(0, "100")
            self.k_entry.grid(row=0, column=3, padx=4)

            ttk.Label(self.param_frame, text="r:").grid(row=0, column=4, sticky="w")
            self.r_entry = ttk.Entry(self.param_frame, width=6); self.r_entry.insert(0, "0.05")
            self.r_entry.grid(row=0, column=5, padx=4)

            ttk.Label(self.param_frame, text="sigma:").grid(row=1, column=0, sticky="w")
            self.sigma_entry = ttk.Entry(self.param_frame, width=8); self.sigma_entry.insert(0, "0.2")
            self.sigma_entry.grid(row=1, column=1, padx=4)

            ttk.Label(self.param_frame, text="T (yrs):").grid(row=1, column=2, sticky="w")
            self.T_entry = ttk.Entry(self.param_frame, width=8); self.T_entry.insert(0, "1.0")
            self.T_entry.grid(row=1, column=3, padx=4)

            ttk.Label(self.param_frame, text="Type:").grid(row=1, column=4, sticky="w")
            self.opt_type = ttk.Combobox(self.param_frame, values=["call", "put"], state="readonly", width=8)
            self.opt_type.current(0)
            self.opt_type.grid(row=1, column=5, padx=4)

    def _on_sim_select(self, event=None):
        self._build_param_widgets()

    def _set_status(self, text):
        self.status.config(text=text)
        self.update_idletasks()

    def _on_run(self):
        # Read n and validate
        try:
            n = int(self.n_entry.get())
            if n <= 0:
                raise ValueError("n must be positive")
        except Exception as e:
            messagebox.showerror("Invalid samples", f"Samples (n) must be a positive integer.\n{e}")
            return

        sim = self.sim_choice.get()
        params = {"sim": sim, "n": n}
        if sim == "Integral":
            func_name = self.func_choice.get()
            a = float(self.a_entry.get())
            b = float(self.b_entry.get())
            params.update({"func": func_name, "a": a, "b": b})
        elif sim == "European Option":
            try:
                S0 = float(self.s0_entry.get()); K = float(self.k_entry.get())
                r = float(self.r_entry.get()); sigma = float(self.sigma_entry.get())
                T = float(self.T_entry.get()); opt_type = self.opt_type.get()
                params.update({"S0": S0, "K": K, "r": r, "sigma": sigma, "T": T, "type": opt_type})
            except Exception as e:
                messagebox.showerror("Invalid parameters", f"Please check option parameters.\n{e}")
                return

        # Disable run button and run in thread to keep UI responsive
        self.btn_run.config(state=tk.DISABLED)
        self.progress.config(value=0, maximum=100)
        self._set_status("Running simulation...")
        thread = threading.Thread(target=self._run_simulation, args=(params,), daemon=True)
        thread.start()

    def _run_simulation(self, params):
        sim = params["sim"]
        n = params["n"]

        # We'll run in chunks and update progressbar so UI doesn't freeze for very large n
        CHUNK = min(200000, max(10000, n // 50))  # adapt chunk size
        n_done = 0

        # For simulations that can be vectorized fully we just run once — but we still fake progress.
        try:
            if sim == "Estimate π":
                estimate, se, samples = mc_estimate_pi(n)
                n_done = n
                self.last_samples = ("pi", samples)
            elif sim == "Integral":
                func = FUNC_MAP.get(params["func"], f_x2)
                estimate, se, samples = mc_integral_estimate(func, params["a"], params["b"], n)
                n_done = n
                self.last_samples = ("integral", samples, params["func"], params["a"], params["b"])
            else:  # European Option
                estimate, se, samples = mc_european_option_price(
                    params["S0"], params["K"], params["r"], params["sigma"], params["T"], n, params["type"]
                )
                n_done = n
                self.last_samples = ("option", samples, params)

            # Simulate progress filling
            for p in range(0, 101, 10):
                time.sleep(0.02)
                self.progress.step(10)
                self.update_idletasks()

            # Update plot and results (back in main thread)
            self.after(0, lambda: self._display_results(estimate, se, params))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Sim Error", f"An error occurred during the simulation:\n{e}"))
        finally:
            self.after(0, lambda: self.btn_run.config(state=tk.NORMAL))
            self.after(0, lambda: self.progress.config(value=0))
            self.after(0, lambda: self._set_status("Ready"))

    def _display_results(self, estimate, se, params):
        # Update results text
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        sim = params["sim"]
        self.results_text.insert(tk.END, f"Simulation: {sim}\n")
        self.results_text.insert(tk.END, f"Samples (n): {params['n']}\n")
        self.results_text.insert(tk.END, f"Estimate: {estimate}\n")
        self.results_text.insert(tk.END, f"Std. error (approx): {se}\n")
        self.results_text.insert(tk.END, "\n")
        if sim == "Integral":
            self.results_text.insert(tk.END, f"Function: {params['func']} over [{params['a']}, {params['b']}]\n")
        elif sim == "European Option":
            self.results_text.insert(tk.END, f"Option params: S0={params['S0']}, K={params['K']}, r={params['r']}, sigma={params['sigma']}, T={params['T']}, type={params['type']}\n")
        self.results_text.config(state=tk.DISABLED)

        # Plot histogram or scatter for pi
        self.ax.clear()
        if sim == "Estimate π":
            kind = "pi"
            tag, samples = self.last_samples[0], self.last_samples[1]
            x, y, inside = samples
            # show scatter of a sample subset to avoid overplot
            display_n = min(5000, len(x))
            idx = np.random.choice(len(x), display_n, replace=False)
            self.ax.scatter(x[idx], y[idx], s=6, alpha=0.6)
            self.ax.set_aspect('equal', 'box')
            self.ax.set_title("Random points (subset) used for π estimation")
            # draw quarter circle
            theta = np.linspace(0, np.pi/2, 200)
            self.ax.plot(np.cos(theta), np.sin(theta), linewidth=2)
        elif sim == "Integral":
            tag, samples, func_name, a, b = self.last_samples
            x, fx = samples
            # histogram of fx
            self.ax.hist(fx, bins=60)
            self.ax.set_title(f"Histogram of f(x) samples for {func_name} on [{a},{b}]")
            self.ax.set_xlabel("f(x)")
            self.ax.set_ylabel("Frequency")
        else:  # option
            tag, samples, params_saved = self.last_samples
            ST, discounted = samples
            self.ax.hist(discounted, bins=60)
            self.ax.set_title("Histogram of discounted payoffs (samples)")
            self.ax.set_xlabel("Discounted Payoff")
            self.ax.set_ylabel("Frequency")

        self.canvas.draw()

    def _save_plot(self):
        ftypes = [("PNG image","*.png")]
        filename = filedialog.asksaveasfilename(defaultextension=".png", filetypes=ftypes)
        if not filename:
            return
        try:
            self.fig.savefig(filename, dpi=150)
            messagebox.showinfo("Saved", f"Plot saved to {filename}")
        except Exception as e:
            messagebox.showerror("Save error", str(e))

    def _export_csv(self):
        if not self.last_samples:
            messagebox.showwarning("No samples", "No simulation samples available to export. Run a simulation first.")
            return
        ftypes = [("CSV file","*.csv")]
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=ftypes)
        if not filename:
            return
        try:
            tag = self.last_samples[0]
            if tag == "pi":
                _, (x, y, inside) = self.last_samples
                data = [("x","y","inside")]
                for xi, yi, in_flag in zip(x, y, inside):
                    data.append((xi, yi, int(in_flag)))
            elif tag == "integral":
                _, (x, fx), func_name, a, b = self.last_samples
                data = [("x","f(x)")]
                for xi, fxi in zip(x, fx):
                    data.append((xi, fxi))
            else:
                _, (ST, discounted), params = self.last_samples
                data = [("ST","discounted_payoff")]
                for s, d in zip(ST, discounted):
                    data.append((s, d))
            with open(filename, "w", newline="") as f:
                writer = csv.writer(f)
                for row in data:
                    writer.writerow(row)
            messagebox.showinfo("Exported", f"Samples exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export error", str(e))

    def _clear(self):
        self.ax.clear()
        self.ax.set_title("Simulation Output")
        self.canvas.draw()
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert(tk.END, "Cleared.\n")
        self.results_text.config(state=tk.DISABLED)
        self.last_samples = None
        self._set_status("Ready")

if __name__ == "__main__":
    app = MonteCarloApp()
    app.mainloop()

"""
Probability Distribution Plotter
Single-file Python desktop application using Tkinter and matplotlib.

Features:
- Select common probability distributions (Normal, Uniform, Binomial, Poisson, Exponential, Beta)
- Set distribution-specific parameters
- Generate random samples or plot theoretical PDF/PMF
- Overlay histogram of samples with theoretical curve
- Save plot as PNG and export sample data to CSV
- Show sample statistics (mean, variance)

Requirements:
- Python 3.x
- tkinter (included)
- numpy
- matplotlib
- scipy (optional but recommended for accurate PMF/PDF functions)

Save as probability_plotter.py and run: python probability_plotter.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
import math

# Try to use scipy.stats if available for precise pdf/pmf; otherwise fall back to numpy implementations
try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except Exception:
    SCIPY_AVAILABLE = False

class ProbPlotterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Probability Distribution Plotter')
        self.geometry('1000x680')
        self.resizable(True, True)

        # UI variables
        self.dist_var = tk.StringVar(value='normal')
        self.sample_size = tk.IntVar(value=1000)
        self.bins = tk.IntVar(value=40)
        # distribution params (store as dict of StringVars)
        self.params = {
            'normal_mu': tk.DoubleVar(value=0.0),
            'normal_sigma': tk.DoubleVar(value=1.0),
            'uniform_a': tk.DoubleVar(value=0.0),
            'uniform_b': tk.DoubleVar(value=1.0),
            'binomial_n': tk.IntVar(value=20),
            'binomial_p': tk.DoubleVar(value=0.5),
            'poisson_mu': tk.DoubleVar(value=3.0),
            'exponential_scale': tk.DoubleVar(value=1.0),
            'beta_a': tk.DoubleVar(value=2.0),
            'beta_b': tk.DoubleVar(value=5.0),
        }

        self.samples = None

        self.create_widgets()

    def create_widgets(self):
        main = ttk.Frame(self, padding=8)
        main.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(main)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0,8))

        # Distribution selector
        dist_frame = ttk.LabelFrame(left, text='Distribution')
        dist_frame.pack(fill=tk.X, pady=(0,8))

        dists = ['normal', 'uniform', 'binomial', 'poisson', 'exponential', 'beta']
        for i, d in enumerate(dists):
            ttk.Radiobutton(dist_frame, text=d.capitalize(), variable=self.dist_var, value=d, command=self.update_param_widgets).grid(row=i, column=0, sticky=tk.W, padx=4, pady=2)

        # Parameters frame
        self.param_frame = ttk.LabelFrame(left, text='Parameters')
        self.param_frame.pack(fill=tk.X, pady=(0,8))
        self.update_param_widgets()

        # Sampling & actions
        sample_frame = ttk.LabelFrame(left, text='Sampling & Actions')
        sample_frame.pack(fill=tk.X)

        ttk.Label(sample_frame, text='Sample size:').grid(row=0, column=0, sticky=tk.W, padx=4, pady=6)
        ttk.Entry(sample_frame, textvariable=self.sample_size, width=10).grid(row=0, column=1, padx=4)

        ttk.Label(sample_frame, text='Bins:').grid(row=1, column=0, sticky=tk.W, padx=4, pady=6)
        ttk.Entry(sample_frame, textvariable=self.bins, width=10).grid(row=1, column=1, padx=4)

        ttk.Button(sample_frame, text='Generate Samples & Plot', command=self.generate_and_plot).grid(row=2, column=0, columnspan=2, sticky=tk.EW, padx=4, pady=(8,4))
        ttk.Button(sample_frame, text='Plot Theoretical Only', command=self.plot_theoretical_only).grid(row=3, column=0, columnspan=2, sticky=tk.EW, padx=4, pady=4)
        ttk.Button(sample_frame, text='Save Plot as PNG', command=self.save_plot).grid(row=4, column=0, columnspan=2, sticky=tk.EW, padx=4, pady=4)
        ttk.Button(sample_frame, text='Export Samples to CSV', command=self.export_csv).grid(row=5, column=0, columnspan=2, sticky=tk.EW, padx=4, pady=4)

        # Right side: plot and stats
        right = ttk.Frame(main)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        plot_frame = ttk.LabelFrame(right, text='Plot')
        plot_frame.pack(fill=tk.BOTH, expand=True)

        self.fig = Figure(figsize=(6,4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('Density / Probability')

        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        stats_frame = ttk.LabelFrame(right, text='Sample Statistics')
        stats_frame.pack(fill=tk.X, pady=(6,0))
        self.mean_var = tk.StringVar(value='-')
        self.var_var = tk.StringVar(value='-')
        ttk.Label(stats_frame, text='Mean:').grid(row=0, column=0, sticky=tk.W, padx=6, pady=4)
        ttk.Label(stats_frame, textvariable=self.mean_var).grid(row=0, column=1, sticky=tk.W)
        ttk.Label(stats_frame, text='Variance:').grid(row=1, column=0, sticky=tk.W, padx=6, pady=4)
        ttk.Label(stats_frame, textvariable=self.var_var).grid(row=1, column=1, sticky=tk.W)

    def clear_plot(self):
        self.ax.clear()
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('Density / Probability')

    def update_param_widgets(self):
        # clear existing widgets
        for w in self.param_frame.winfo_children():
            w.destroy()
        d = self.dist_var.get()
        row = 0
        if d == 'normal':
            ttk.Label(self.param_frame, text='Mean (mu):').grid(row=row, column=0, sticky=tk.W, padx=4, pady=2)
            ttk.Entry(self.param_frame, textvariable=self.params['normal_mu'], width=12).grid(row=row, column=1)
            row +=1
            ttk.Label(self.param_frame, text='Std Dev (sigma):').grid(row=row, column=0, sticky=tk.W, padx=4, pady=2)
            ttk.Entry(self.param_frame, textvariable=self.params['normal_sigma'], width=12).grid(row=row, column=1)
        elif d == 'uniform':
            ttk.Label(self.param_frame, text='Lower (a):').grid(row=row, column=0, sticky=tk.W, padx=4, pady=2)
            ttk.Entry(self.param_frame, textvariable=self.params['uniform_a'], width=12).grid(row=row, column=1)
            row+=1
            ttk.Label(self.param_frame, text='Upper (b):').grid(row=row, column=0, sticky=tk.W, padx=4, pady=2)
            ttk.Entry(self.param_frame, textvariable=self.params['uniform_b'], width=12).grid(row=row, column=1)
        elif d == 'binomial':
            ttk.Label(self.param_frame, text='Number of trials (n):').grid(row=row, column=0, sticky=tk.W, padx=4, pady=2)
            ttk.Entry(self.param_frame, textvariable=self.params['binomial_n'], width=12).grid(row=row, column=1)
            row+=1
            ttk.Label(self.param_frame, text='Success prob (p):').grid(row=row, column=0, sticky=tk.W, padx=4, pady=2)
            ttk.Entry(self.param_frame, textvariable=self.params['binomial_p'], width=12).grid(row=row, column=1)
        elif d == 'poisson':
            ttk.Label(self.param_frame, text='Mean (lambda):').grid(row=row, column=0, sticky=tk.W, padx=4, pady=2)
            ttk.Entry(self.param_frame, textvariable=self.params['poisson_mu'], width=12).grid(row=row, column=1)
        elif d == 'exponential':
            ttk.Label(self.param_frame, text='Scale (1/lambda):').grid(row=row, column=0, sticky=tk.W, padx=4, pady=2)
            ttk.Entry(self.param_frame, textvariable=self.params['exponential_scale'], width=12).grid(row=row, column=1)
        elif d == 'beta':
            ttk.Label(self.param_frame, text='Alpha (a):').grid(row=row, column=0, sticky=tk.W, padx=4, pady=2)
            ttk.Entry(self.param_frame, textvariable=self.params['beta_a'], width=12).grid(row=row, column=1)
            row+=1
            ttk.Label(self.param_frame, text='Beta (b):').grid(row=row, column=0, sticky=tk.W, padx=4, pady=2)
            ttk.Entry(self.param_frame, textvariable=self.params['beta_b'], width=12).grid(row=row, column=1)

    def generate_and_plot(self):
        d = self.dist_var.get()
        n = max(1, int(self.sample_size.get()))
        bins = max(1, int(self.bins.get()))
        try:
            if d == 'normal':
                mu = float(self.params['normal_mu'].get())
                sigma = float(self.params['normal_sigma'].get())
                samples = np.random.normal(mu, sigma, size=n)
            elif d == 'uniform':
                a = float(self.params['uniform_a'].get())
                b = float(self.params['uniform_b'].get())
                samples = np.random.uniform(a, b, size=n)
            elif d == 'binomial':
                trials = int(self.params['binomial_n'].get())
                p = float(self.params['binomial_p'].get())
                samples = np.random.binomial(trials, p, size=n)
            elif d == 'poisson':
                mu = float(self.params['poisson_mu'].get())
                samples = np.random.poisson(mu, size=n)
            elif d == 'exponential':
                scale = float(self.params['exponential_scale'].get())
                samples = np.random.exponential(scale, size=n)
            elif d == 'beta':
                a = float(self.params['beta_a'].get())
                b = float(self.params['beta_b'].get())
                samples = np.random.beta(a, b, size=n)
            else:
                messagebox.showerror('Error', 'Unknown distribution')
                return
        except Exception as e:
            messagebox.showerror('Error', f'Invalid parameters: {e}')
            return

        self.samples = samples
        self.mean_var.set(f'{np.mean(samples):.4f}')
        self.var_var.set(f'{np.var(samples, ddof=0):.4f}')

        # plot
        self.clear_plot()
        ax = self.ax
        # distinguish discrete distributions for PMF plotting
        if d in ('binomial', 'poisson'):
            # histogram as bar for discrete
            values, counts = np.unique(samples, return_counts=True)
            ax.bar(values, counts / counts.sum(), align='center', alpha=0.6, label='Sample PMF')
            # theoretical pmf
            xs = np.arange(values.min(), values.max()+1)
            pmf = self.theoretical_pmf(xs, d)
            if pmf is not None:
                ax.plot(xs, pmf, marker='o', linestyle='-', label='Theoretical PMF')
            ax.set_xlabel('k')
            ax.set_ylabel('Probability')
        else:
            ax.hist(samples, bins=bins, density=True, alpha=0.6, label='Sample histogram')
            xs = np.linspace(np.min(samples), np.max(samples), 400)
            pdf = self.theoretical_pdf(xs, d)
            if pdf is not None:
                ax.plot(xs, pdf, lw=2, label='Theoretical PDF')

        ax.legend()
        ax.set_title(f'{d.capitalize()} distribution (n={n})')
        self.canvas.draw()

    def plot_theoretical_only(self):
        d = self.dist_var.get()
        self.clear_plot()
        ax = self.ax
        # choose reasonable x-range per distribution
        if d == 'normal':
            mu = float(self.params['normal_mu'].get())
            sigma = float(self.params['normal_sigma'].get())
            xs = np.linspace(mu - 4*sigma, mu + 4*sigma, 400)
            pdf = self.theoretical_pdf(xs, d)
            ax.plot(xs, pdf, lw=2, label='Normal PDF')
        elif d == 'uniform':
            a = float(self.params['uniform_a'].get())
            b = float(self.params['uniform_b'].get())
            xs = np.linspace(a - (b-a)*0.1, b + (b-a)*0.1, 200)
            pdf = self.theoretical_pdf(xs, d)
            ax.plot(xs, pdf, lw=2, label='Uniform PDF')
        elif d == 'binomial':
            trials = int(self.params['binomial_n'].get())
            xs = np.arange(0, trials+1)
            pmf = self.theoretical_pmf(xs, d)
            if pmf is not None:
                ax.stem(xs, pmf, basefmt=' ', use_line_collection=True)
        elif d == 'poisson':
            mu = float(self.params['poisson_mu'].get())
            xs = np.arange(0, max(20, int(mu*4)+5))
            pmf = self.theoretical_pmf(xs, d)
            if pmf is not None:
                ax.stem(xs, pmf, basefmt=' ', use_line_collection=True)
        elif d == 'exponential':
            scale = float(self.params['exponential_scale'].get())
            xs = np.linspace(0, scale*8, 400)
            pdf = self.theoretical_pdf(xs, d)
            ax.plot(xs, pdf, lw=2, label='Exponential PDF')
        elif d == 'beta':
            a = float(self.params['beta_a'].get())
            b = float(self.params['beta_b'].get())
            xs = np.linspace(0,1,400)
            pdf = self.theoretical_pdf(xs, d)
            ax.plot(xs, pdf, lw=2, label='Beta PDF')
        ax.set_title(f'Theoretical {d.capitalize()}')
        ax.legend()
        self.canvas.draw()

    def theoretical_pdf(self, xs, dist):
        if SCIPY_AVAILABLE:
            if dist == 'normal':
                mu = float(self.params['normal_mu'].get()); sigma = float(self.params['normal_sigma'].get())
                return stats.norm.pdf(xs, loc=mu, scale=sigma)
            if dist == 'uniform':
                a = float(self.params['uniform_a'].get()); b = float(self.params['uniform_b'].get())
                return stats.uniform.pdf(xs, loc=a, scale=(b-a))
            if dist == 'exponential':
                scale = float(self.params['exponential_scale'].get())
                return stats.expon.pdf(xs, scale=scale)
            if dist == 'beta':
                a = float(self.params['beta_a'].get()); b = float(self.params['beta_b'].get())
                return stats.beta.pdf(xs, a, b)
        else:
            # fallback implementations
            if dist == 'normal':
                mu = float(self.params['normal_mu'].get()); sigma = float(self.params['normal_sigma'].get())
                coeff = 1.0 / (sigma * math.sqrt(2*math.pi))
                return coeff * np.exp(-0.5 * ((xs - mu)/sigma)**2)
            if dist == 'uniform':
                a = float(self.params['uniform_a'].get()); b = float(self.params['uniform_b'].get())
                pdf = np.zeros_like(xs)
                mask = (xs >= a) & (xs <= b)
                pdf[mask] = 1.0 / (b-a) if b > a else 0
                return pdf
            if dist == 'exponential':
                scale = float(self.params['exponential_scale'].get())
                lam = 1.0/scale if scale>0 else 0
                pdf = np.zeros_like(xs)
                mask = xs >= 0
                pdf[mask] = lam * np.exp(-lam * xs[mask])
                return pdf
            if dist == 'beta':
                a = float(self.params['beta_a'].get()); b = float(self.params['beta_b'].get())
                # use scipy if available; otherwise approximate via gamma function from math
                def beta_fn(a,b):
                    return math.exp(math.lgamma(a) + math.lgamma(b) - math.lgamma(a+b))
                B = beta_fn(a,b)
                pdf = np.zeros_like(xs)
                mask = (xs >= 0) & (xs <= 1)
                pdf[mask] = (xs[mask]**(a-1)) * ((1 - xs[mask])**(b-1)) / B
                return pdf
        return None

    def theoretical_pmf(self, ks, dist):
        if SCIPY_AVAILABLE:
            if dist == 'binomial':
                n = int(self.params['binomial_n'].get()); p = float(self.params['binomial_p'].get())
                return stats.binom.pmf(ks, n, p)
            if dist == 'poisson':
                mu = float(self.params['poisson_mu'].get())
                return stats.poisson.pmf(ks, mu)
        else:
            if dist == 'binomial':
                n = int(self.params['binomial_n'].get()); p = float(self.params['binomial_p'].get())
                pmf = np.array([math.comb(n, k) * (p**k) * ((1-p)**(n-k)) if 0<=k<=n else 0 for k in ks])
                return pmf
            if dist == 'poisson':
                mu = float(self.params['poisson_mu'].get())
                pmf = np.array([math.exp(-mu) * (mu**k) / math.factorial(int(k)) if k>=0 else 0 for k in ks])
                return pmf
        return None

    def save_plot(self):
        path = filedialog.asksaveasfilename(defaultextension='.png', filetypes=[('PNG image','*.png')])
        if not path:
            return
        try:
            self.fig.savefig(path)
            messagebox.showinfo('Saved', f'Plot saved to {path}')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to save plot: {e}')

    def export_csv(self):
        if self.samples is None:
            messagebox.showinfo('Info', 'No samples to export')
            return
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files','*.csv')])
        if not path:
            return
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['index','value'])
                for i, v in enumerate(self.samples):
                    writer.writerow([i+1, v])
            messagebox.showinfo('Saved', f'Samples exported to {path}')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to export CSV: {e}')

if __name__ == '__main__':
    app = ProbPlotterApp()
    app.mainloop()

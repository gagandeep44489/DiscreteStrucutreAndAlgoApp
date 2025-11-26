"""
Permutation & Combination Calculator - Desktop app using Tkinter
Save this file as Permutation_and_Combination_Calculator.py and run with Python 3.8+

Features:
- Compute factorial, nPr, nCr
- Supports permutations/combinations with repetition
- Input validation with helpful error messages
- Copy result to clipboard, save history to a text file
- Keyboard shortcuts: Enter to calculate, Ctrl+C to copy result, Ctrl+S to save history
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import datetime

APP_TITLE = "Permutation & Combination Calculator"


def safe_int(s):
    try:
        return int(s)
    except Exception:
        return None


def factorial(n):
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    return math.factorial(n)


def permutations(n, r, repetition=False):
    if repetition:
        # n^r
        return pow(n, r)
    if r > n:
        return 0
    return math.factorial(n) // math.factorial(n - r)


def combinations(n, r, repetition=False):
    if repetition:
        # C(n+r-1, r) for combinations with repetition
        return math.comb(n + r - 1, r)
    if r > n:
        return 0
    return math.comb(n, r)


class App:
    def __init__(self, root):
        self.root = root
        root.title(APP_TITLE)
        root.geometry("520x380")
        root.resizable(False, False)

        main = ttk.Frame(root, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        # Inputs
        inputs = ttk.LabelFrame(main, text="Inputs", padding=10)
        inputs.grid(row=0, column=0, sticky="ew", padx=6, pady=6)

        ttk.Label(inputs, text="n (total items):").grid(row=0, column=0, sticky="w")
        self.n_var = tk.StringVar()
        self.n_entry = ttk.Entry(inputs, textvariable=self.n_var, width=12)
        self.n_entry.grid(row=0, column=1, sticky="w", padx=6)

        ttk.Label(inputs, text="r (selected items):").grid(row=1, column=0, sticky="w")
        self.r_var = tk.StringVar()
        self.r_entry = ttk.Entry(inputs, textvariable=self.r_var, width=12)
        self.r_entry.grid(row=1, column=1, sticky="w", padx=6)

        self.repetition_var = tk.BooleanVar(value=False)
        self.repetition_check = ttk.Checkbutton(inputs, text="Allow repetition", variable=self.repetition_var)
        self.repetition_check.grid(row=2, column=0, columnspan=2, sticky="w", pady=(6,0))

        # Mode: factorial / permutation / combination
        mode = ttk.LabelFrame(main, text="Operation", padding=10)
        mode.grid(row=1, column=0, sticky="ew", padx=6, pady=6)

        self.mode_var = tk.StringVar(value="nPr")
        ttk.Radiobutton(mode, text="nPr (Permutation)", variable=self.mode_var, value="nPr").grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(mode, text="nCr (Combination)", variable=self.mode_var, value="nCr").grid(row=0, column=1, sticky="w")
        ttk.Radiobutton(mode, text="n! (Factorial of n)", variable=self.mode_var, value="fact").grid(row=0, column=2, sticky="w")

        # Buttons
        controls = ttk.Frame(main)
        controls.grid(row=2, column=0, sticky="ew", padx=6, pady=6)

        self.calc_btn = ttk.Button(controls, text="Calculate", command=self.calculate)
        self.calc_btn.grid(row=0, column=0, padx=(0,8))

        self.copy_btn = ttk.Button(controls, text="Copy Result", command=self.copy_result)
        self.copy_btn.grid(row=0, column=1, padx=(0,8))

        self.clear_btn = ttk.Button(controls, text="Clear", command=self.clear_all)
        self.clear_btn.grid(row=0, column=2, padx=(0,8))

        self.save_btn = ttk.Button(controls, text="Save History", command=self.save_history)
        self.save_btn.grid(row=0, column=3)

        # Result / History
        output = ttk.LabelFrame(main, text="Output", padding=10)
        output.grid(row=3, column=0, sticky="nsew", padx=6, pady=6)

        ttk.Label(output, text="Result:").grid(row=0, column=0, sticky="w")
        self.result_var = tk.StringVar()
        self.result_entry = ttk.Entry(output, textvariable=self.result_var, state="readonly", width=40)
        self.result_entry.grid(row=0, column=1, sticky="w", padx=6)

        ttk.Label(output, text="History (recent):").grid(row=1, column=0, sticky="nw", pady=(6,0))
        self.history_txt = tk.Text(output, height=8, width=60, wrap=tk.WORD, state=tk.DISABLED)
        self.history_txt.grid(row=1, column=1, pady=(6,0))

        # Bindings
        root.bind('<Return>', lambda e: self.calculate())
        root.bind('<Control-c>', lambda e: self.copy_result())
        root.bind('<Control-C>', lambda e: self.copy_result())
        root.bind('<Control-s>', lambda e: self.save_history())
        root.bind('<Control-S>', lambda e: self.save_history())

        # internal history list
        self.history = []

    def add_history(self, text):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        entry = f"[{timestamp}] {text}\n"
        self.history.insert(0, entry)
        # keep recent 50 entries
        self.history = self.history[:50]
        self.history_txt.configure(state=tk.NORMAL)
        self.history_txt.delete('1.0', tk.END)
        self.history_txt.insert(tk.END, ''.join(self.history))
        self.history_txt.configure(state=tk.DISABLED)

    def calculate(self):
        mode = self.mode_var.get()
        n_s = self.n_var.get().strip()
        r_s = self.r_var.get().strip()
        rep = self.repetition_var.get()

        # factorial mode only needs n
        n = safe_int(n_s)
        r = safe_int(r_s) if r_s != '' else None

        try:
            if mode == 'fact':
                if n is None:
                    raise ValueError('Please enter a valid integer for n')
                val = factorial(n)
                self.result_var.set(str(val))
                self.add_history(f"{n}! = {val}")
                return

            # for permutations/combinations both n and r required
            if n is None or r is None:
                raise ValueError('Please enter valid integers for n and r')
            if n < 0 or r < 0:
                raise ValueError('n and r must be non-negative integers')

            if mode == 'nPr':
                val = permutations(n, r, repetition=rep)
                self.result_var.set(str(val))
                self.add_history(f"P({n},{r}){' with repetition' if rep else ''} = {val}")
            elif mode == 'nCr':
                val = combinations(n, r, repetition=rep)
                self.result_var.set(str(val))
                self.add_history(f"C({n},{r}){' with repetition' if rep else ''} = {val}")
            else:
                raise ValueError('Unknown operation')

        except Exception as e:
            messagebox.showerror('Error', str(e))

    def copy_result(self):
        val = self.result_var.get()
        if not val:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(val)
        messagebox.showinfo('Copied', 'Result copied to clipboard')

    def clear_all(self):
        self.n_var.set('')
        self.r_var.set('')
        self.result_var.set('')
        self.repetition_var.set(False)

    def save_history(self):
        if not self.history:
            messagebox.showinfo('No history', 'There is no history to save')
            return
        file_path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text files','*.txt')], title='Save history')
        if not file_path:
            return
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(self.history[::-1])
            messagebox.showinfo('Saved', f'History saved to {file_path}')
        except Exception as e:
            messagebox.showerror('Save error', str(e))


if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()

"""
Karnaugh Map Solver — Python (tkinter)

Single-file desktop application to build and solve Karnaugh maps (K-maps) for 2 to 4 variables.

Features:
- Support for 2, 3, or 4 variables (standard K-map sizes)
- Interactive grid where each cell can be toggled: 0 -> 1 -> X (don't care)
- Compute simplified Boolean expression (Sum of Products) using SymPy's SOPform
- Show simplified expression in human-readable form and as a Python-like expression
- Export truth table / minterms to CSV

Requirements:
- Python 3.8+
- sympy (install with `pip install sympy`)

Run:
python "Karnaugh Map Solver — Python (tkinter).py"

"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import itertools
import csv

try:
    from sympy.logic.boolalg import SOPform, POSform
    from sympy import symbols
except Exception as e:
    SOPform = None
    POSform = None


GRAY = lambda n: n ^ (n >> 1)


def gray_code(n):
    return [GRAY(i) for i in range(1 << n)]


class KarnaughApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Karnaugh Map Solver')
        self.geometry('880x560')

        # State
        self.var_count = tk.IntVar(value=4)
        self.cell_states = []  # list of state per cell: 0,1,2 -> 0,1,don't care
        self.cell_buttons = []

        self._build_ui()

    def _build_ui(self):
        top = ttk.Frame(self, padding=8)
        top.pack(fill=tk.X)

        ttk.Label(top, text='Variables:').pack(side=tk.LEFT)
        self.var_combo = ttk.Combobox(top, values=[2,3,4], width=3, state='readonly', textvariable=self.var_count)
        self.var_combo.pack(side=tk.LEFT, padx=6)
        self.var_combo.bind('<<ComboboxSelected>>', lambda e: self.build_kmap())

        ttk.Button(top, text='Build K-map', command=self.build_kmap).pack(side=tk.LEFT, padx=6)
        ttk.Button(top, text='Clear', command=self.clear_map).pack(side=tk.LEFT, padx=6)
        ttk.Button(top, text='Evaluate (Simplify)', command=self.evaluate).pack(side=tk.LEFT, padx=6)
        ttk.Button(top, text='Export CSV', command=self.export_csv).pack(side=tk.LEFT, padx=6)

        mid = ttk.Frame(self, padding=8)
        mid.pack(fill=tk.BOTH, expand=True)

        # Left: K-map canvas
        self.kmap_frame = ttk.Frame(mid)
        self.kmap_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Right: results
        right = ttk.Frame(mid, width=320)
        right.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Label(right, text='Simplified Expression:', font=('Segoe UI', 10, 'bold')).pack(anchor='nw', pady=(2,4))
        self.result_text = tk.Text(right, width=40, height=8, wrap=tk.WORD)
        self.result_text.pack(padx=6, pady=4)
        self.result_text.config(state=tk.DISABLED)

        ttk.Label(right, text='Python-style expression:', font=('Segoe UI', 10, 'bold')).pack(anchor='nw', pady=(8,4))
        self.py_text = tk.Text(right, width=40, height=4, wrap=tk.WORD)
        self.py_text.pack(padx=6, pady=4)
        self.py_text.config(state=tk.DISABLED)

        ttk.Label(right, text='Notes / Help', font=('Segoe UI', 10, 'bold')).pack(anchor='nw', pady=(8,4))
        help_lbl = tk.Label(right, justify=tk.LEFT, wraplength=300, text=(
            'Click a cell to toggle its state: 0 -> 1 -> X (don\'t care) -> 0.\n\n'
            'After setting minterms (1) and don\'t-cares (X), click Evaluate to get the simplified SOP form.\n\n'
            'Requires sympy. Install with: pip install sympy'
        ))
        help_lbl.pack(padx=6)

        # Build initial map
        self.build_kmap()

    def build_kmap(self):
        # clear
        for child in self.kmap_frame.winfo_children():
            child.destroy()
        self.cell_buttons.clear()
        self.cell_states.clear()

        n = self.var_count.get()
        if n not in (2,3,4):
            messagebox.showwarning('Unsupported', 'Only 2, 3, or 4 variables are supported.')
            return

        # variable names A, B, C, D
        var_names = ['A','B','C','D'][:n]
        self.vars = var_names

        # layout: for 2 vars -> 2x2, 3 vars -> 2x4 (rows A, cols BC), 4 vars -> 4x4 (rows AB, cols CD)
        if n == 2:
            rows, cols = 2, 2
            row_vars = ['A']
            col_vars = ['B']
        elif n == 3:
            rows, cols = 2, 4
            row_vars = ['A']
            col_vars = ['B','C']
        else:
            rows, cols = 4, 4
            row_vars = ['A','B']
            col_vars = ['C','D']

        # compute Gray order for row and column indices
        row_gray = gray_code(len(row_vars))
        col_gray = gray_code(len(col_vars))

        # header labels for columns (show variable combinations)
        header = ttk.Frame(self.kmap_frame)
        header.pack()
        ttk.Label(header, text='').grid(row=0, column=0)
        for j, cg in enumerate(col_gray):
            label = ' '.join(var_names[len(row_vars)+k] + '=' + str((cg >> (len(col_vars)-1-k)) & 1) for k in range(len(col_vars)))
            ttk.Label(header, text=label, borderwidth=1, relief='solid').grid(row=0, column=j+1, padx=2, pady=2, sticky='nsew')

        grid = ttk.Frame(self.kmap_frame)
        grid.pack(pady=8)

        # build cells
        for i, rg in enumerate(row_gray):
            # row label
            row_label = ' '.join(var_names[k] + '=' + str((rg >> (len(row_vars)-1-k)) & 1) for k in range(len(row_vars)))
            ttk.Label(grid, text=row_label, borderwidth=1, relief='solid').grid(row=i+1, column=0, padx=2, pady=2, sticky='nsew')
            for j, cg in enumerate(col_gray):
                # compute minterm index: combine row bits and col bits (row as high-order)
                bits = []
                for k in range(len(row_vars)):
                    bits.append((rg >> (len(row_vars)-1-k)) & 1)
                for k in range(len(col_vars)):
                    bits.append((cg >> (len(col_vars)-1-k)) & 1)
                # bits array corresponds to variable order [row_vars..., col_vars...]
                # We want minterm index in order A B C D (A MSB)
                # Align bits to var_names
                # For n variables, bits length == n
                index = 0
                for b in bits:
                    index = (index << 1) | b
                # Initialize cell state 0
                btn = tk.Button(grid, text=f'{index}\n0', width=8, height=4, bg='white')
                btn.grid(row=i+1, column=j+1, padx=2, pady=2)
                btn.config(command=lambda b=btn, idx=index: self.toggle_cell(b, idx))
                self.cell_buttons.append((btn, index))
                self.cell_states.append(0)

        # store mapping: index -> position in cell_buttons list
        self.index_to_pos = {idx: pos for pos, (_, idx) in enumerate(self.cell_buttons)}

    def toggle_cell(self, btn, index):
        pos = self.index_to_pos[index]
        st = self.cell_states[pos]
        # cycle 0 -> 1 -> X(2) -> 0
        st = (st + 1) % 3
        self.cell_states[pos] = st
        if st == 0:
            btn.config(text=f'{index}\n0', bg='white')
        elif st == 1:
            btn.config(text=f'{index}\n1', bg='#b3ffb3')
        else:
            btn.config(text=f'{index}\nX', bg='#ffe680')

    def clear_map(self):
        for pos, (btn, idx) in enumerate(self.cell_buttons):
            self.cell_states[pos] = 0
            btn.config(text=f'{idx}\n0', bg='white')
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete('1.0', tk.END)
        self.result_text.config(state=tk.DISABLED)
        self.py_text.config(state=tk.NORMAL)
        self.py_text.delete('1.0', tk.END)
        self.py_text.config(state=tk.DISABLED)

    def evaluate(self):
        if SOPform is None:
            messagebox.showerror('Missing dependency', 'sympy is required to compute simplified expressions. Install with: pip install sympy')
            return
        n = self.var_count.get()
        minterms = []
        dontcares = []
        for pos, (btn, idx) in enumerate(self.cell_buttons):
            st = self.cell_states[pos]
            if st == 1:
                minterms.append(idx)
            elif st == 2:
                dontcares.append(idx)
        vars_sym = symbols(' '.join(self.vars))
        try:
            if not minterms and not dontcares:
                messagebox.showinfo('No minterms', 'No minterms (1) or don\'t-cares (X) set.')
                return
            sop = SOPform(vars_sym, minterms, dontcares)
            # POS alternative
            posf = POSform(vars_sym, [i for i in range(1<<n) if i not in minterms and i not in dontcares], [])
            # show
            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete('1.0', tk.END)
            self.result_text.insert(tk.END, str(sop))
            self.result_text.config(state=tk.DISABLED)

            self.py_text.config(state=tk.NORMAL)
            self.py_text.delete('1.0', tk.END)
            self.py_text.insert(tk.END, str(sop).replace('~', ' not ').replace('&', ' and ').replace('|', ' or '))
            self.py_text.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror('Error', f'Could not simplify: {e}')

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV', '*.csv')])
        if not path:
            return
        try:
            n = self.var_count.get()
            headers = self.vars + ['Value']
            with open(path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                for pos, (btn, idx) in enumerate(self.cell_buttons):
                    st = self.cell_states[pos]
                    val = '0' if st == 0 else ('1' if st == 1 else 'X')
                    # compute bits
                    bits = [(idx >> (n-1-i)) & 1 for i in range(n)]
                    writer.writerow(bits + [val])
            messagebox.showinfo('Saved', f'Truth table exported to {path}')
        except Exception as e:
            messagebox.showerror('Save error', f'Could not save file: {e}')


if __name__ == '__main__':
    app = KarnaughApp()
    app.mainloop()

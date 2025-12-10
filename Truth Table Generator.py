"""
Truth Table Generator
Single-file Python 3 desktop application using tkinter.

Features:
- Accept a boolean expression in human-friendly syntax
  - Supports operators: NOT (!, ~, ¬, NOT), AND (&, ∧, AND), OR (|, ∨, OR), XOR (^, XOR),
    IMPLIES (->, =>), IFF (<->, <=>)
  - Parentheses for grouping
  - Variable names: letters, digits and underscores, e.g. A, B, X1, p, q
- Auto-detect variables from expression (or allow user to specify order)
- Generate full truth table (all combinations) and display in a scrollable grid
- Export table to CSV
- Copy table to clipboard

Run:
python "Truth Table Generator — Python (tkinter).py"

Note: This app evaluates expressions in a strictly controlled namespace. It does
not execute arbitrary code from the expression. Operator tokens are converted
into safe helper functions before evaluation.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import re
import csv
import itertools
import io
import sys

# ---------- Expression handling (safe) ----------

# Helper boolean functions used by evaluated expressions
def _NOT(a):
    return not a

def _AND(a, b):
    return a and b

def _OR(a, b):
    return a or b

def _XOR(a, b):
    return (a and not b) or (not a and b)

def _IMP(a, b):
    # implication: A -> B is (not A) or B
    return (not a) or b

def _IFF(a, b):
    return a == b

# Map of operator tokens (regex) to replacement function names
_OPERATOR_REPLACEMENTS = [
    # biconditional must be replaced before simpler tokens
    (r'<-|<->|<=>', '_IFF'),
    (r'->|=>', '_IMP'),
    (r'\bXOR\b|\^', '_XOR'),
    (r'\bAND\b|\band\b|&|∧', '_AND'),
    (r'\bOR\b|\bor\b|\||∨', '_OR'),
    (r'\bNOT\b|\bnot\b|!|~|¬', '_NOT'),
]

# Operators words to ignore when detecting variable names
_OPERATOR_WORDS = {'AND', 'OR', 'NOT', 'XOR', 'IMP', 'IFF', 'and', 'or', 'not', 'xor'}

VAR_REGEX = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")


def normalize_expression(expr: str) -> str:
    """Convert a user expression into a safe evaluable Python expression that
    calls helper functions. Example: "A AND (NOT B)" -> "_AND(A, _NOT(B))".

    This transformation is conservative and operates by inserting function
    calls for binary / unary operators. Parentheses and variable names are
    preserved.
    """
    s = expr[:]
    # standardize spacing around arrows so regex can find them
    s = s.replace('=>', '->')

    # Replace multi-char operators first
    for pat, repl in _OPERATOR_REPLACEMENTS:
        s = re.sub(pat, f' {repl} ', s)

    # Now we have a token stream with variable names, parentheses, and function names
    tokens = re.findall(r'\(|\)|\w+|[^\s\w]', s)

    # We will construct output by applying simple shunting-like rules to convert
    # infix to function calls. Simpler approach: convert unary _NOT X -> _NOT(X)
    # and binary A _AND B -> _AND(A, B) while respecting parentheses.

    # We'll implement a small recursive descent parser for this token stream.
    idx = 0

    def peek():
        return tokens[idx] if idx < len(tokens) else None

    def consume():
        nonlocal idx
        t = tokens[idx] if idx < len(tokens) else None
        idx += 1
        return t

    def parse_atom():
        t = peek()
        if t is None:
            raise ValueError('Unexpected end of expression')
        if t == '(':
            consume()  # '('
            expr = parse_expr()
            if peek() != ')':
                raise ValueError('Missing closing parenthesis')
            consume()  # ')'
            return f'({expr})'
        # unary NOT
        if t == '_NOT':
            consume()
            # parse next atom
            atom = parse_atom()
            return f'_NOT({atom})'
        # variable or boolean literal
        if re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', t):
            consume()
            # convert True/False literals if user uses them
            if t.lower() == 'true':
                return 'True'
            if t.lower() == 'false':
                return 'False'
            return t
        # unexpected token
        raise ValueError(f'Unexpected token: {t}')

    def parse_expr():
        # parse left operand
        left = parse_atom()
        while True:
            t = peek()
            if t in ('_AND', '_OR', '_XOR', '_IMP', '_IFF'):
                op = consume()
                right = parse_atom()
                left = f'{op}({left}, {right})'
                continue
            # allow implicit end
            break
        return left

    parsed = parse_expr()
    # if tokens remain, it's an error
    if idx != len(tokens):
        # there may be stray commas or operators; try a forgiving join
        remaining = ' '.join(tokens[idx:])
        raise ValueError(f'Could not parse entire expression. Remaining: {remaining}')
    return parsed


def extract_variables(expr: str):
    names = set(m.group(0) for m in VAR_REGEX.finditer(expr))
    # remove reserved operator words
    names = {n for n in names if n not in _OPERATOR_WORDS and not hasattr(__builtins__, n)}
    # remove function names we insert
    names -= {'_AND', '_OR', '_NOT', '_XOR', '_IMP', '_IFF'}
    # Remove boolean literals
    names = {n for n in names if n.lower() not in ('true', 'false')}
    return sorted(names)


def eval_expression_for_row(parsed_expr: str, var_names, values):
    # Build safe namespace with variable boolean values and helper functions
    env = {
        '_NOT': _NOT,
        '_AND': _AND,
        '_OR': _OR,
        '_XOR': _XOR,
        '_IMP': _IMP,
        '_IFF': _IFF,
        'True': True,
        'False': False,
    }
    for name, val in zip(var_names, values):
        # variable names must be valid python identifiers; assume they are
        env[name] = bool(val)
    try:
        return bool(eval(parsed_expr, {}, env))
    except Exception as e:
        raise ValueError(f'Evaluation error: {e}')

# ---------- GUI ----------

class TruthTableApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Truth Table Generator')
        self.geometry('900x560')

        # Top controls
        top = ttk.Frame(self, padding=8)
        top.pack(fill=tk.X)

        ttk.Label(top, text='Boolean expression:').pack(side=tk.LEFT)
        self.expr_var = tk.StringVar()
        self.expr_entry = ttk.Entry(top, textvariable=self.expr_var, width=60)
        self.expr_entry.pack(side=tk.LEFT, padx=6)
        self.expr_entry.insert(0, 'A AND (NOT B) OR C')

        ttk.Button(top, text='Generate', command=self.on_generate).pack(side=tk.LEFT, padx=6)
        ttk.Button(top, text='Export CSV', command=self.on_export_csv).pack(side=tk.LEFT, padx=6)
        ttk.Button(top, text='Copy to clipboard', command=self.on_copy).pack(side=tk.LEFT, padx=6)

        # Variable order display and manual entry
        mid = ttk.Frame(self, padding=8)
        mid.pack(fill=tk.X)
        ttk.Label(mid, text='Variables (comma-separated, optional):').pack(side=tk.LEFT)
        self.vars_var = tk.StringVar()
        self.vars_entry = ttk.Entry(mid, textvariable=self.vars_var, width=40)
        self.vars_entry.pack(side=tk.LEFT, padx=6)
        ttk.Label(mid, text='(leave blank to auto-detect and sort)').pack(side=tk.LEFT, padx=6)

        # Table area (scrollable)
        table_frame = ttk.Frame(self, padding=8)
        table_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(table_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.table_inner = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.table_inner, anchor='nw')
        self.table_inner.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))

        # Status bar
        bottom = ttk.Frame(self, padding=8)
        bottom.pack(fill=tk.X)
        self.status = ttk.Label(bottom, text='Ready')
        self.status.pack(side=tk.LEFT)

        # Keep last generated table for export
        self.last_table = None
        self.last_var_names = None

    def on_generate(self):
        expr = self.expr_var.get().strip()
        if not expr:
            messagebox.showwarning('Input required', 'Please enter a boolean expression.')
            return
        try:
            # Preprocess: replace operators with function tokens
            normalized = expr[:]
            for pat, repl in _OPERATOR_REPLACEMENTS:
                normalized = re.sub(pat, f' {repl} ', normalized, flags=re.IGNORECASE)

            var_names = self.vars_var.get().strip()
            if var_names:
                var_list = [v.strip() for v in var_names.split(',') if v.strip()]
            else:
                var_list = extract_variables(normalized)

            if len(var_list) == 0:
                messagebox.showwarning('No variables', 'No variables detected — please enter variable names or include them in the expression.')
                return
            if len(var_list) > 16:
                # safety: too many variables => 2^n rows
                if not messagebox.askyesno('Many variables', f'{len(var_list)} variables detected — table will have {2**len(var_list)} rows. Continue?'):
                    return

            # Convert normalized into parsed callable form
            parsed = normalize_expression(normalized)

            # Build truth table rows
            rows = []
            for bits in itertools.product([False, True], repeat=len(var_list)):
                try:
                    val = eval_expression_for_row(parsed, var_list, bits)
                except Exception as e:
                    messagebox.showerror('Evaluation error', f'Error evaluating expression: {e}')
                    return
                rows.append((list(bits), val))

            # Store last table
            self.last_table = rows
            self.last_var_names = var_list

            # Display table
            self._render_table(var_list, rows)
            self.status.config(text=f'Generated truth table with {len(rows)} rows.')

        except Exception as e:
            messagebox.showerror('Error', f'Could not generate table: {e}')
            self.status.config(text='Error')

    def _render_table(self, var_names, rows):
        # Clear previous
        for child in self.table_inner.winfo_children():
            child.destroy()

        # Header
        header_style = {'font': ('Segoe UI', 10, 'bold'), 'borderwidth': 1, 'relief': 'solid'}
        label = ttk.Label(self.table_inner, text=' | '.join(var_names) + ' | OUT', **header_style)
        label.grid(row=0, column=0, sticky='w', padx=6, pady=4)

        # Rows
        for i, (bits, out) in enumerate(rows, start=1):
            bit_str = ' | '.join('1' if b else '0' for b in bits)
            lbl = ttk.Label(self.table_inner, text=f'{bit_str} | {1 if out else 0}', borderwidth=1, relief='solid')
            lbl.grid(row=i, column=0, sticky='w', padx=4, pady=2)

    def on_export_csv(self):
        if not self.last_table or not self.last_var_names:
            messagebox.showwarning('No table', 'Please generate a truth table first.')
            return
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files', '*.csv')], title='Save truth table as CSV')
        if not path:
            return
        try:
            with open(path, 'w', newline='') as f:
                writer = csv.writer(f)
                header = list(self.last_var_names) + ['OUT']
                writer.writerow(header)
                for bits, out in self.last_table:
                    writer.writerow([1 if b else 0 for b in bits] + [1 if out else 0])
            messagebox.showinfo('Saved', f'Truth table exported to {path}')
        except Exception as e:
            messagebox.showerror('Save error', f'Could not save file: {e}')

    def on_copy(self):
        if not self.last_table or not self.last_var_names:
            messagebox.showwarning('No table', 'Please generate a truth table first.')
            return
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(list(self.last_var_names) + ['OUT'])
        for bits, out in self.last_table:
            writer.writerow([1 if b else 0 for b in bits] + [1 if out else 0])
        txt = output.getvalue()
        try:
            self.clipboard_clear()
            self.clipboard_append(txt)
            messagebox.showinfo('Copied', 'Truth table copied to clipboard in CSV format.')
        except Exception as e:
            messagebox.showerror('Clipboard error', f'Could not copy to clipboard: {e}')


if __name__ == '__main__':
    app = TruthTableApp()
    app.mainloop()

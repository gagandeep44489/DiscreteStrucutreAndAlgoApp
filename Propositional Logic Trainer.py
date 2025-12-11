#!/usr/bin/env python3
"""
Propositional Logic Trainer
Single-file desktop app using tkinter + sympy.

Features:
- Enter propositional formulas in a simple infix syntax:
    ~A or !A   (NOT)
    A & B      (AND)
    A | B      (OR)
    A ^ B      (XOR)
    A -> B     (IMPLIES)  (also =>)
    A <-> B    (EQUIVALENT) (also <=>)
    parentheses allowed
- Parse formulas (shunting-yard) to SymPy boolean expressions
- Show truth table
- Check: tautology, contradiction, satisfiable (contingency)
- Convert to CNF / DNF / simplified form
- Practice mode: classify random formulas; scoring tracked
- Export truth table to CSV

Dependency: sympy
    pip install sympy
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import itertools
import random
import csv
from math import ceil

import sympy as sp

# ------------------ Parser (Infix -> SymPy) ------------------

TOKEN_SPEC = [
    ('LPAREN',  r'\('),
    ('RPAREN',  r'\)'),
    ('IMPL',    r'(->|=>)'),
    ('EQUIV',   r'(<->|<=>)'),
    ('AND',     r'&'),
    ('OR',      r'\|'),
    ('XOR',     r'\^'),
    ('NOT',     r'(~|!)'),
    ('NAME',    r'[A-Za-z_][A-Za-z0-9_]*'),
    ('SKIP',    r'[ \t]+'),
    ('MISMATCH',r'.'),
]

TOK_RE = re.compile('|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPEC))

# Operator metadata: precedence, associativity ('L' or 'R'), arity
OPS = {
    '~':  (5, 'R', 1, 'NOT'),
    '!':  (5, 'R', 1, 'NOT'),
    '&':  (4, 'L', 2, 'AND'),
    '|':  (3, 'L', 2, 'OR'),
    '^':  (3, 'L', 2, 'XOR'),
    '->': (2, 'R', 2, 'IMPLIES'),
    '=>': (2, 'R', 2, 'IMPLIES'),
    '<->':(1, 'L', 2, 'EQUIV'),
    '<=>':(1, 'L', 2, 'EQUIV'),
}

def tokenize(expr):
    for mo in TOK_RE.finditer(expr):
        kind = mo.lastgroup
        val = mo.group()
        if kind == 'SKIP':
            continue
        if kind == 'MISMATCH':
            raise ValueError(f"Unexpected character {val!r}")
        yield kind, val

def infix_to_rpn(expr):
    """Convert infix tokens to RPN (list of tokens)."""
    output = []
    stack = []
    for kind, val in tokenize(expr):
        if kind == 'NAME':
            output.append(('NAME', val))
        elif kind in ('NOT', 'AND', 'OR', 'XOR', 'IMPL', 'EQUIV'):
            op = val
            # normalize multi-char operators to canonical tokens
            if val in ('->', '=>'):
                op = '->'
            if val in ('<->', '<=>'):
                op = '<->'
            prec, assoc, arity, opname = OPS[op]
            while stack:
                top = stack[-1]
                if top[0] == 'OP':
                    top_op = top[1]
                    tprec, tassoc, _, _ = OPS[top_op]
                    if (assoc == 'L' and prec <= tprec) or (assoc == 'R' and prec < tprec):
                        output.append(('OP', top_op))
                        stack.pop()
                        continue
                break
            stack.append(('OP', op))
        elif kind == 'LPAREN':
            stack.append(('LPAREN', val))
        elif kind == 'RPAREN':
            while stack and stack[-1][0] != 'LPAREN':
                output.append(stack.pop())
            if not stack:
                raise ValueError("Mismatched parentheses")
            stack.pop()  # pop '('
        else:
            raise ValueError(f"Unhandled token kind: {kind}")
    while stack:
        if stack[-1][0] == 'LPAREN':
            raise ValueError("Mismatched parentheses")
        output.append(stack.pop())
    # RPN is list of ('NAME', val) or ('OP', op)
    return output

def rpn_to_sympy(rpn):
    """Evaluate RPN producing a sympy boolean expression. Creates symbols on the fly."""
    stack = []
    sym_cache = {}
    def get_symbol(name):
        if name not in sym_cache:
            sym_cache[name] = sp.Symbol(name)
        return sym_cache[name]
    for token in rpn:
        if token[0] == 'NAME':
            stack.append(get_symbol(token[1]))
        elif token[0] == 'OP':
            op = token[1]
            if op in ('~','!'):
                if not stack:
                    raise ValueError("Missing operand for NOT")
                a = stack.pop()
                stack.append(sp.Not(a))
            elif op == '&':
                b = stack.pop(); a = stack.pop()
                stack.append(sp.And(a,b))
            elif op == '|':
                b = stack.pop(); a = stack.pop()
                stack.append(sp.Or(a,b))
            elif op == '^':
                b = stack.pop(); a = stack.pop()
                stack.append(sp.Xor(a,b))
            elif op == '->':
                b = stack.pop(); a = stack.pop()
                stack.append(sp.Implies(a,b))
            elif op == '<->':
                b = stack.pop(); a = stack.pop()
                stack.append(sp.Equivalent(a,b))
            else:
                raise ValueError(f"Unknown operator {op}")
        else:
            raise ValueError("Invalid RPN token")
    if len(stack) != 1:
        raise ValueError("Invalid expression: leftover operands")
    expr = stack[0]
    return expr, list(sym_cache.values())

def parse_formula_to_sympy(text):
    """Convert textual formula to sympy expression and list of symbol objects."""
    if not text or text.strip() == "":
        raise ValueError("Empty formula")
    rpn = infix_to_rpn(text)
    expr, syms = rpn_to_sympy(rpn)
    # order variables consistently by name
    syms_sorted = sorted({s for s in syms}, key=lambda s: str(s))
    return expr, syms_sorted

# ------------------ Logical helpers ------------------

def truth_table(expr, symbols):
    """Return list of (valuation_dict, result_bool). symbols is list of sympy Symbols in chosen order."""
    rows = []
    n = len(symbols)
    for bits in itertools.product([False, True], repeat=n):
        assign = dict(zip(symbols, bits))
        val = bool(expr.xreplace(assign)) if hasattr(expr, 'xreplace') else bool(expr.subs(assign))
        rows.append((assign, val))
    return rows

def is_tautology(expr, symbols):
    for assign, val in truth_table(expr, symbols):
        if not val:
            return False
    return True

def is_contradiction(expr, symbols):
    for assign, val in truth_table(expr, symbols):
        if val:
            return False
    return True

def is_satisfiable(expr):
    # sympy satisfiable returns False for unsat, or a dict for a model
    return bool(sp.satisfiable(expr))

# ------------------ Random formula generator (for practice) ------------------

VAR_NAMES = ['P','Q','R','S','T','U','V','W']

def generate_random_formula(var_count=3, depth=3):
    vars_pool = random.sample(VAR_NAMES, var_count)
    def gen(level):
        if level == 0:
            return random.choice(vars_pool)
        op = random.choice(['NOT','AND','OR','IMPL','EQUIV','XOR'])
        if op == 'NOT':
            return f'~{gen(level-1)}'
        else:
            left = gen(level-1)
            right = gen(level-1)
            if op == 'AND':
                return f'({left} & {right})'
            if op == 'OR':
                return f'({left} | {right})'
            if op == 'XOR':
                return f'({left} ^ {right})'
            if op == 'IMPL':
                return f'({left} -> {right})'
            if op == 'EQUIV':
                return f'({left} <-> {right})'
    return gen(depth)

# ------------------ GUI ------------------

class PropositionalTrainerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Propositional Logic Trainer")
        self.geometry("1100x720")
        self.minsize(1000, 650)

        self.current_expr = None
        self.current_symbols = []
        self.practice_score = 0
        self.practice_total = 0

        self._build_ui()

    def _build_ui(self):
        # Top frame: input + actions
        top = ttk.Frame(self, padding=8)
        top.pack(fill='x')
        ttk.Label(top, text="Enter formula:").pack(side='left')
        self.formula_var = tk.StringVar()
        self.formula_entry = ttk.Entry(top, textvariable=self.formula_var, width=70)
        self.formula_entry.pack(side='left', padx=(8,6))
        ttk.Button(top, text="Parse & Preview", command=self.parse_and_preview).pack(side='left', padx=4)
        ttk.Button(top, text="Truth Table", command=self.show_truth_table).pack(side='left', padx=4)
        ttk.Button(top, text="CNF / DNF", command=self.show_cnf_dnf).pack(side='left', padx=4)
        ttk.Button(top, text="Simplify", command=self.simplify_expr).pack(side='left', padx=4)

        # Middle: left controls, right preview
        middle = ttk.Panedwindow(self, orient='horizontal')
        middle.pack(fill='both', expand=True, padx=8, pady=8)

        left = ttk.Frame(middle, width=340)
        right = ttk.Frame(middle)
        middle.add(left, weight=1)
        middle.add(right, weight=3)

        # Left controls
        ttk.Label(left, text="Properties & Checks", font=('Segoe UI', 11, 'bold')).pack(anchor='w')
        btn_frame = ttk.Frame(left)
        btn_frame.pack(fill='x', pady=(6,6))
        ttk.Button(btn_frame, text="Is Tautology?", command=self.check_tautology).pack(fill='x', pady=3)
        ttk.Button(btn_frame, text="Is Contradiction?", command=self.check_contradiction).pack(fill='x', pady=3)
        ttk.Button(btn_frame, text="Is Satisfiable?", command=self.check_satisfiable).pack(fill='x', pady=3)
        ttk.Button(btn_frame, text="Check Equivalence (2 formulas)", command=self.equivalence_window).pack(fill='x', pady=3)

        ttk.Separator(left).pack(fill='x', pady=8)

        ttk.Label(left, text="Practice Mode", font=('Segoe UI', 11, 'bold')).pack(anchor='w', pady=(6,4))
        pr_frame = ttk.Frame(left)
        pr_frame.pack(fill='x')
        ttk.Label(pr_frame, text="Variables:").grid(row=0, column=0, sticky='w')
        self.pr_vars = tk.IntVar(value=3)
        ttk.Spinbox(pr_frame, from_=1, to=6, width=4, textvariable=self.pr_vars).grid(row=0, column=1, sticky='w', padx=6)
        ttk.Label(pr_frame, text="Depth:").grid(row=1, column=0, sticky='w')
        self.pr_depth = tk.IntVar(value=3)
        ttk.Spinbox(pr_frame, from_=0, to=5, width=4, textvariable=self.pr_depth).grid(row=1, column=1, sticky='w', padx=6)

        ttk.Button(left, text="New Practice Question", command=self.new_practice).pack(fill='x', pady=(8,4))
        self.practice_question_label = ttk.Label(left, text="Question will appear here", wraplength=300)
        self.practice_question_label.pack(anchor='w', pady=(4,6))
        # choices
        self.pr_choice = tk.StringVar(value='contingent')
        for val, txt in [('tautology','Tautology'), ('contradiction','Contradiction'), ('contingent','Contingent')]:
            ttk.Radiobutton(left, text=txt, variable=self.pr_choice, value=val).pack(anchor='w')
        ttk.Button(left, text="Submit Answer", command=self.submit_practice).pack(fill='x', pady=(6,4))
        self.score_label = ttk.Label(left, text="Score: 0 / 0")
        self.score_label.pack(anchor='w', pady=(6,0))

        ttk.Separator(left).pack(fill='x', pady=8)
        ttk.Button(left, text="Export Truth Table CSV", command=self.export_truth_table).pack(fill='x')

        # Right: preview area (truth table, expression info)
        self.preview_title = ttk.Label(right, text="Preview: No formula parsed", font=('Segoe UI', 11))
        self.preview_title.pack(anchor='w')

        # Treeview for truth table
        self.table_frame = ttk.Frame(right)
        self.table_frame.pack(fill='both', expand=True, pady=(6,0))
        self.tree = None

        # Bottom: status bar
        bottom = ttk.Frame(self, padding=6)
        bottom.pack(fill='x')
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(bottom, textvariable=self.status_var).pack(side='left')

    # ---------------- UI Actions ----------------
    def parse_and_preview(self):
        text = self.formula_var.get().strip()
        try:
            expr, syms = parse_formula_to_sympy(text)
            # sympy.simplify may change symbol ordering; keep consistent by name
            syms_sorted = sorted(syms, key=lambda s: str(s))
            self.current_expr = expr
            self.current_symbols = syms_sorted
            self.preview_title.config(text=f"Preview — {text}")
            self.status_var.set("Formula parsed successfully")
            self.update_truth_table_preview(limit=500)  # show entire table if small
        except Exception as e:
            messagebox.showerror("Parse Error", str(e))
            self.status_var.set("Parse failed")

    def update_truth_table_preview(self, limit=500):
        if self.current_expr is None:
            messagebox.showinfo("No formula", "Parse a formula first.")
            return
        rows = truth_table(self.current_expr, self.current_symbols)
        # Destroy previous tree
        if self.tree:
            self.tree.destroy()
            self.tree = None
        cols = [str(s) for s in self.current_symbols] + ['Result']
        self.tree = ttk.Treeview(self.table_frame, columns=cols, show='headings')
        vsb = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=100, anchor='center')
        for assign, val in rows[:limit]:
            rowvals = [str(assign[s]) for s in self.current_symbols] + [str(val)]
            self.tree.insert('', 'end', values=rowvals)
        self.status_var.set(f"Truth table updated ({len(rows)} rows).")

    def show_truth_table(self):
        if self.current_expr is None:
            self.parse_and_preview()
            if self.current_expr is None:
                return
        # Always open a new window with full table (unless too big)
        rows = truth_table(self.current_expr, self.current_symbols)
        n = len(rows)
        if n > 1024:
            if not messagebox.askyesno("Large table", f"Truth table has {n} rows. Show anyway?"):
                return
        tbl_win = tk.Toplevel(self)
        tbl_win.title("Truth Table")
        frame = ttk.Frame(tbl_win, padding=6)
        frame.pack(fill='both', expand=True)
        tree = ttk.Treeview(frame, columns=[str(s) for s in self.current_symbols] + ['Result'], show='headings')
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        for s in self.current_symbols:
            tree.heading(str(s), text=str(s))
            tree.column(str(s), width=100, anchor='center')
        tree.heading('Result', text='Result')
        tree.column('Result', width=100, anchor='center')
        for assign, val in rows:
            rowvals = [str(assign[s]) for s in self.current_symbols] + [str(val)]
            tree.insert('', 'end', values=rowvals)

    def show_cnf_dnf(self):
        if self.current_expr is None:
            messagebox.showinfo("No formula", "Parse a formula first.")
            return
        try:
            cnf = sp.to_cnf(self.current_expr, simplify=True)
            dnf = sp.to_dnf(self.current_expr, simplify=True)
            win = tk.Toplevel(self)
            win.title("CNF / DNF")
            ttk.Label(win, text="CNF:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', padx=6, pady=(6,0))
            txt1 = tk.Text(win, height=4, wrap='word')
            txt1.pack(fill='x', padx=6); txt1.insert('1.0', str(cnf)); txt1.configure(state='disabled')
            ttk.Label(win, text="DNF:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', padx=6, pady=(6,0))
            txt2 = tk.Text(win, height=4, wrap='word')
            txt2.pack(fill='x', padx=6); txt2.insert('1.0', str(dnf)); txt2.configure(state='disabled')
            self.status_var.set("Converted to CNF and DNF")
        except Exception as e:
            messagebox.showerror("Conversion error", str(e))

    def simplify_expr(self):
        if self.current_expr is None:
            messagebox.showinfo("No formula", "Parse a formula first.")
            return
        try:
            simplified = sp.simplify_logic(self.current_expr, force=True)
            win = tk.Toplevel(self)
            win.title("Simplified")
            txt = tk.Text(win, height=6, wrap='word')
            txt.pack(fill='both', expand=True, padx=6, pady=6)
            txt.insert('1.0', str(simplified))
            txt.configure(state='disabled')
            self.status_var.set("Expression simplified")
        except Exception as e:
            messagebox.showerror("Simplify error", str(e))

    def check_tautology(self):
        if self.current_expr is None:
            self.parse_and_preview()
            if self.current_expr is None:
                return
        result = is_tautology(self.current_expr, self.current_symbols)
        messagebox.showinfo("Tautology Check", f"Tautology: {result}")
        self.status_var.set("Tautology checked")

    def check_contradiction(self):
        if self.current_expr is None:
            self.parse_and_preview()
            if self.current_expr is None:
                return
        result = is_contradiction(self.current_expr, self.current_symbols)
        messagebox.showinfo("Contradiction Check", f"Contradiction: {result}")
        self.status_var.set("Contradiction checked")

    def check_satisfiable(self):
        if self.current_expr is None:
            self.parse_and_preview()
            if self.current_expr is None:
                return
        sat = is_satisfiable(self.current_expr)
        messagebox.showinfo("Satisfiability", f"Satisfiable: {sat}")
        self.status_var.set("Satisfiability checked")

    def equivalence_window(self):
        win = tk.Toplevel(self)
        win.title("Check Equivalence")
        ttk.Label(win, text="Formula A:").pack(anchor='w', padx=6, pady=(6,0))
        a_var = tk.StringVar()
        ttk.Entry(win, textvariable=a_var, width=80).pack(fill='x', padx=6, pady=2)
        ttk.Label(win, text="Formula B:").pack(anchor='w', padx=6, pady=(6,0))
        b_var = tk.StringVar()
        ttk.Entry(win, textvariable=b_var, width=80).pack(fill='x', padx=6, pady=2)
        def do_check():
            try:
                a_expr, a_syms = parse_formula_to_sympy(a_var.get())
                b_expr, b_syms = parse_formula_to_sympy(b_var.get())
                # union symbols
                symbols = sorted({*a_syms, *b_syms}, key=lambda s: str(s))
                equiv = is_tautology(sp.Equivalent(a_expr, b_expr), symbols)
                messagebox.showinfo("Equivalence", f"Equivalent: {equiv}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        ttk.Button(win, text="Check", command=do_check).pack(padx=6, pady=8)

    # ---------------- Practice mode ----------------
    def new_practice(self):
        var_count = int(self.pr_vars.get())
        depth = int(self.pr_depth.get())
        formula = generate_random_formula(var_count=var_count, depth=depth)
        self.practice_formula = formula
        self.practice_question_label.config(text=formula)
        self.pr_choice.set('contingent')
        self.status_var.set("New practice question generated")

    def submit_practice(self):
        if not hasattr(self, 'practice_formula'):
            messagebox.showinfo("No question", "Generate a question first.")
            return
        try:
            expr, syms = parse_formula_to_sympy(self.practice_formula)
            taut = is_tautology(expr, syms)
            contra = is_contradiction(expr, syms)
            correct = 'tautology' if taut else 'contradiction' if contra else 'contingent'
            user = self.pr_choice.get()
            self.practice_total += 1
            if user == correct:
                self.practice_score += 1
                messagebox.showinfo("Result", f"Correct — the formula is {correct}.")
            else:
                messagebox.showinfo("Result", f"Incorrect — the formula is {correct}.")
            self.score_label.config(text=f"Score: {self.practice_score} / {self.practice_total}")
            self.status_var.set("Practice answer submitted")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------- Export / Utilities ----------------
    def export_truth_table(self):
        if self.current_expr is None:
            messagebox.showinfo("No formula", "Parse a formula first.")
            return
        rows = truth_table(self.current_expr, self.current_symbols)
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV", "*.csv"), ("All files", "*.*")])
        if not path:
            return
        try:
            with open(path, 'w', newline='') as f:
                writer = csv.writer(f)
                header = [str(s) for s in self.current_symbols] + ['Result']
                writer.writerow(header)
                for assign, val in rows:
                    row = [assign[s] for s in self.current_symbols] + [val]
                    writer.writerow(row)
            messagebox.showinfo("Exported", f"Truth table exported to {path}")
            self.status_var.set("Truth table exported")
        except Exception as e:
            messagebox.showerror("Export error", str(e))

if __name__ == "__main__":
    app = PropositionalTrainerApp()
    app.mainloop()

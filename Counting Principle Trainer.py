"""
Counting Principle Trainer
A simple desktop app (Tkinter) to practice Fundamental Counting Principle, Permutations, and Combinations.
Save as counting_trainer.py and run: python counting_trainer.py

Features:
- Generate practice problems for three types: Counting Principle, Permutations, Combinations
- Multiple-choice answers, score tracking, hints and step-by-step solution
- Difficulty slider to control size of numbers
- Progress and reset

This is a single-file app with only standard-library dependencies (tkinter, math, random).
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
import math

# Helpers

def nPr(n, r):
    if r > n or n < 0 or r < 0:
        return 0
    try:
        return math.perm(n, r)
    except AttributeError:
        return math.factorial(n) // math.factorial(n - r)


def nCr(n, r):
    if r > n or n < 0 or r < 0:
        return 0
    try:
        return math.comb(n, r)
    except AttributeError:
        return math.factorial(n) // (math.factorial(r) * math.factorial(n - r))


class ProblemGenerator:
    def __init__(self, difficulty=1):
        self.difficulty = difficulty

    def set_difficulty(self, d):
        self.difficulty = max(1, int(d))

    def _rand_range(self):
        # difficulty controls the size of numbers
        if self.difficulty == 1:
            return (2, 6)
        elif self.difficulty == 2:
            return (2, 9)
        elif self.difficulty == 3:
            return (2, 12)
        else:
            return (2, 15)

    def generate(self, kind=None):
        kinds = ["Counting Principle", "Permutations (nPr)", "Combinations (nCr)"]
        if kind is None:
            kind = random.choice(kinds)
        elif kind not in kinds:
            kind = "Counting Principle"

        lo, hi = self._rand_range()

        if kind == "Counting Principle":
            # Random number of groups (2-4)
            groups = random.randint(2, min(4, self.difficulty + 1))
            sizes = [random.randint(lo, hi) for _ in range(groups)]
            statement = f"If there are {', '.join(str(s) for s in sizes[:-1])} and {sizes[-1]} choices respectively, how many total possible outcomes are there?"
            answer = 1
            for s in sizes:
                answer *= s
            hint = f"Multiply the sizes: {' x '.join(str(s) for s in sizes)} = {answer}"
            solution = hint
            return {"type": kind, "statement": statement, "answer": answer, "hint": hint, "solution": solution}

        elif kind == "Permutations (nPr)":
            n = random.randint(lo + 1, hi + 2)
            r = random.randint(1, min(n, self.difficulty + 2))
            statement = f"How many ordered ways to choose {r} from {n}? (nPr)"
            answer = nPr(n, r)
            hint = f"Use nPr = n! / (n-r)! => {n}! / ({n}-{r})!"
            solution = f"{answer} (computed as nPr({n},{r}))"
            return {"type": kind, "statement": statement, "answer": answer, "hint": hint, "solution": solution}

        else:  # Combinations
            n = random.randint(lo + 1, hi + 2)
            r = random.randint(1, min(n, self.difficulty + 2))
            statement = f"How many ways to choose {r} from {n} where order does NOT matter? (nCr)"
            answer = nCr(n, r)
            hint = f"Use nCr = n! / (r!(n-r)!) => {n}! / ({r}! * {n - r}!)"
            solution = f"{answer} (computed as nCr({n},{r}))"
            return {"type": kind, "statement": statement, "answer": answer, "hint": hint, "solution": solution}


class CountingTrainerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Counting Principle Trainer")
        self.geometry("720x420")
        self.resizable(False, False)

        self.generator = ProblemGenerator(difficulty=1)
        self.score = 0
        self.total = 0
        self.current = None

        self._build_ui()
        self.new_problem()

    def _build_ui(self):
        frm = ttk.Frame(self, padding=12)
        frm.pack(fill=tk.BOTH, expand=True)

        # Top: controls
        ctrl = ttk.Frame(frm)
        ctrl.pack(fill=tk.X)

        ttk.Label(ctrl, text="Problem type:").pack(side=tk.LEFT)
        self.type_var = tk.StringVar(value="Any")
        type_menu = ttk.Combobox(ctrl, textvariable=self.type_var, values=["Any", "Counting Principle", "Permutations (nPr)", "Combinations (nCr)"], state="readonly", width=22)
        type_menu.pack(side=tk.LEFT, padx=6)

        ttk.Label(ctrl, text="Difficulty:").pack(side=tk.LEFT, padx=(10, 0))
        self.diff_var = tk.IntVar(value=1)
        diff_slider = ttk.Scale(ctrl, from_=1, to=4, command=self._on_diff_change, orient=tk.HORIZONTAL, length=120)
        diff_slider.set(1)
        diff_slider.pack(side=tk.LEFT, padx=6)

        gen_btn = ttk.Button(ctrl, text="New Problem", command=self.new_problem)
        gen_btn.pack(side=tk.RIGHT)

        # Middle: problem and choices
        mid = ttk.Frame(frm, relief=tk.RIDGE, padding=12)
        mid.pack(fill=tk.BOTH, expand=True, pady=10)

        self.statement = tk.Text(mid, height=3, wrap=tk.WORD, font=(None, 12))
        self.statement.pack(fill=tk.X)
        self.statement.config(state=tk.DISABLED)

        self.choices_var = tk.IntVar(value=-1)
        self.choice_buttons = []
        for i in range(4):
            rb = ttk.Radiobutton(mid, text=f"Option {i+1}", variable=self.choices_var, value=i)
            rb.pack(anchor=tk.W, pady=2)
            self.choice_buttons.append(rb)

        # Bottom: actions and info
        bottom = ttk.Frame(frm)
        bottom.pack(fill=tk.X)

        check_btn = ttk.Button(bottom, text="Check Answer", command=self.check_answer)
        check_btn.pack(side=tk.LEFT)

        hint_btn = ttk.Button(bottom, text="Hint", command=self.show_hint)
        hint_btn.pack(side=tk.LEFT, padx=6)

        show_btn = ttk.Button(bottom, text="Show Solution", command=self.show_solution)
        show_btn.pack(side=tk.LEFT)

        self.progress_lbl = ttk.Label(bottom, text="Score: 0/0 | Accuracy: N/A")
        self.progress_lbl.pack(side=tk.RIGHT)

    def _on_diff_change(self, val):
        d = int(float(val))
        self.diff_var.set(d)
        self.generator.set_difficulty(d)

    def new_problem(self):
        kind = self.type_var.get()
        if kind == "Any" or kind == "":
            kind = None
        self.current = self.generator.generate(kind)
        self.total += 1
        self.choices_var.set(-1)
        # Display statement
        self.statement.config(state=tk.NORMAL)
        self.statement.delete("1.0", tk.END)
        self.statement.insert(tk.END, f"Type: {self.current['type']}\n\n{self.current['statement']}")
        self.statement.config(state=tk.DISABLED)

        # Generate 4 options (one correct + 3 distractors)
        correct = self.current['answer']
        options = {correct}
        attempts = 0
        while len(options) < 4 and attempts < 200:
            attempts += 1
            distractor = self._make_distractor(correct, self.current['type'])
            options.add(distractor)
        options = list(options)
        random.shuffle(options)

        for i, rb in enumerate(self.choice_buttons):
            rb.config(text=f"{options[i]}")

        # save options for checking
        self.current['options'] = options

        self._update_progress_label()

    def _make_distractor(self, correct, kind):
        # create plausible wrong answers
        if kind == "Counting Principle":
            # Off by multiplying or dividing by a small factor
            if correct <= 12:
                return max(1, correct + random.choice([-2, -1, 1, 2]))
            delta = random.choice([-3, -2, -1, 1, 2, 3])
            return max(1, correct + delta)
        elif kind.startswith("Permutations"):
            # swap n and r or use nCr instead of nPr
            val = correct
            if random.random() < 0.4:
                # use a nearby factorial-related value
                return max(1, correct + random.choice([-10, -6, -3, 3, 6, 10]))
            return max(1, int(correct * random.choice([1, 0.5, 2]) + random.choice([-2, -1, 1, 2])))
        else:
            # combinations distractors
            if correct <= 10:
                return max(0, correct + random.choice([-3, -2, -1, 1, 2, 3]))
            return max(0, int(correct * random.choice([1, 0.5, 1.5]) + random.choice([-5, -3, -1, 1, 3, 5])))

    def check_answer(self):
        sel = self.choices_var.get()
        if sel == -1:
            messagebox.showinfo("No selection", "Please choose an option first.")
            return
        picked = self.current['options'][sel]
        correct = self.current['answer']
        if int(picked) == int(correct):
            self.score += 1
            messagebox.showinfo("Correct!", "Nice — that's the right answer.")
        else:
            messagebox.showerror("Incorrect", f"Wrong answer. Correct answer is {correct}.")
        self._update_progress_label()
        # auto-generate next
        self.new_problem()

    def show_hint(self):
        if not self.current:
            return
        messagebox.showinfo("Hint", self.current.get('hint', 'No hint available.'))

    def show_solution(self):
        if not self.current:
            return
        messagebox.showinfo("Solution", self.current.get('solution', 'No solution available.'))

    def _update_progress_label(self):
        acc = f"{(self.score/self.total*100):.0f}%" if self.total > 0 else "N/A"
        self.progress_lbl.config(text=f"Score: {self.score}/{self.total} | Accuracy: {acc}")


if __name__ == '__main__':
    app = CountingTrainerApp()
    app.mainloop()

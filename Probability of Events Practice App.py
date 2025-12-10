"""
Probability of Events Practice App
Single-file Python 3 desktop application using tkinter.

Features:
- Generate random practice questions on basic probability events:
  - P(A ∪ B) given P(A), P(B), P(A ∩ B)
  - P(A ∩ B) given P(A), P(B) and independence or overlap
  - P(A | B) (conditional probability) given P(A ∩ B) and P(B)
  - Complement: P(A^c)
  - Independence check (given P(A), P(B), P(A ∩ B))
  - Bayes (simple) when possible
- Accept numeric answers; supports fractions (like 1/3) or decimals.
- Immediate feedback and step-by-step explanation.
- Keeps score and shows attempts.

Requirements:
- Python 3.x
- tkinter (standard library)

Run:
python "Probability of Events Practice App — Python (tkinter).py"

"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
from fractions import Fraction
import math

# ----- Utility functions -----

def fmt_prob(x):
    """Format probability for display (as fraction when nice)."""
    try:
        fr = Fraction(x).limit_denominator(100)
        if abs(float(fr) - x) < 1e-9:
            return str(fr)
    except Exception:
        pass
    return f"{x:.4f}".rstrip('0').rstrip('.')


def parse_input(s):
    """Parse user input which may be a fraction like '1/3' or decimal '0.333'."""
    s = s.strip()
    if not s:
        raise ValueError("Empty input")
    if '/' in s:
        a, b = s.split('/')
        return float(Fraction(int(a.strip()), int(b.strip())))
    else:
        return float(s)


def close_enough(user_val, correct_val, tol=1e-2):
    """Check numeric equality with tolerance (absolute)."""
    return abs(user_val - correct_val) <= tol


# ----- Question generation -----

PROBLEM_TYPES = [
    "Union: P(A ∪ B)",
    "Intersection: P(A ∩ B)",
    "Conditional: P(A | B)",
    "Complement: P(A^c)",
    "Independence check",
    "Bayes (P(A|B) via Bayes)"
]


def random_probability(low=0.05, high=0.8):
    return round(random.uniform(low, high), 3)


def generate_union_question():
    pA = random_probability()
    pB = random_probability()
    # ensure intersection is legal
    max_inter = min(pA, pB)
    inter = round(random.uniform(0, max_inter), 3)
    statement = f"Given P(A) = {fmt_prob(pA)}, P(B) = {fmt_prob(pB)}, and P(A ∩ B) = {fmt_prob(inter)}.\nFind P(A ∪ B)."
    answer = pA + pB - inter
    explanation = f"P(A ∪ B) = P(A) + P(B) - P(A ∩ B) = {fmt_prob(pA)} + {fmt_prob(pB)} - {fmt_prob(inter)} = {fmt_prob(answer)}"
    return statement, answer, explanation


def generate_intersection_question():
    pA = random_probability()
    pB = random_probability()
    # randomly decide if independent or not
    independent = random.choice([True, False])
    if independent:
        inter = round(pA * pB, 3)
        statement = f"Given P(A) = {fmt_prob(pA)} and P(B) = {fmt_prob(pB)}. Assume A and B are independent.\nFind P(A ∩ B)."
        explanation = f"For independent events, P(A ∩ B) = P(A) * P(B) = {fmt_prob(pA)} * {fmt_prob(pB)} = {fmt_prob(inter)}"
        return statement, inter, explanation
    else:
        # provide intersection explicitly but ask to compute? Instead provide P(A), P(B) and P(A∪B)
        # so we can compute intersection from union formula
        inter = round(random.uniform(0, min(pA, pB)), 3)
        statement = f"Given P(A) = {fmt_prob(pA)}, P(B) = {fmt_prob(pB)}, and P(A ∪ B) = {fmt_prob(pA + pB - inter)}.\nFind P(A ∩ B)."
        answer = inter
        explanation = f"P(A ∩ B) = P(A) + P(B) - P(A ∪ B) = {fmt_prob(pA)} + {fmt_prob(pB)} - {fmt_prob(pA + pB - inter)} = {fmt_prob(inter)}"
        return statement, answer, explanation


def generate_conditional_question():
    # generate P(A∩B) and P(B)
    pB = random_probability(0.05, 0.9)
    pA_and_B = round(random.uniform(0, pB), 3)
    # ensure P(A) may be larger than intersection
    pA = max(pA_and_B, random_probability(0.05, 0.9))
    statement = f"Given P(A ∩ B) = {fmt_prob(pA_and_B)} and P(B) = {fmt_prob(pB)}.\nFind P(A | B)."
    if pB == 0:
        answer = 0.0
    else:
        answer = pA_and_B / pB
    explanation = f"P(A | B) = P(A ∩ B) / P(B) = {fmt_prob(pA_and_B)} / {fmt_prob(pB)} = {fmt_prob(answer)}"
    return statement, answer, explanation


def generate_complement_question():
    pA = random_probability()
    statement = f"Given P(A) = {fmt_prob(pA)}.\nFind P(A^c) (the probability that A does not occur)."
    answer = 1 - pA
    explanation = f"P(A^c) = 1 - P(A) = 1 - {fmt_prob(pA)} = {fmt_prob(answer)}"
    return statement, answer, explanation


def generate_independence_check_question():
    pA = random_probability()
    pB = random_probability()
    # possibly make consistent or inconsistent
    # pick an intersection; sometimes equal to pA*pB sometimes not
    if random.random() < 0.6:
        inter = round(pA * pB, 3)
        independent = True
    else:
        # choose different intersection
        inter = round(random.uniform(0, min(pA, pB)), 3)
        independent = abs(inter - pA * pB) < 1e-6
    statement = f"Given P(A) = {fmt_prob(pA)}, P(B) = {fmt_prob(pB)}, and P(A ∩ B) = {fmt_prob(inter)}.\nAre A and B independent? (Answer 'yes' or 'no')"
    answer = "yes" if independent else "no"
    explanation = "Events A and B are independent if P(A ∩ B) = P(A) * P(B).\n"
    explanation += f"Here P(A) * P(B) = {fmt_prob(pA * pB)}, while P(A ∩ B) = {fmt_prob(inter)}.\nHence: "
    explanation += "Independent." if independent else "Not independent."
    return statement, answer, explanation


def generate_bayes_question():
    # Create a simple Bayes scenario with two hypotheses A and A^c and evidence B
    pA = random_probability(0.05, 0.6)
    # P(B|A) and P(B|A^c)
    pB_given_A = random_probability(0.2, 0.95)
    pB_given_notA = random_probability(0.0, min(0.6, pB_given_A - 0.05))
    # compute P(B)
    pB = pB_given_A * pA + pB_given_notA * (1 - pA)
    # target: P(A|B)
    if pB == 0:
        answer = 0.0
    else:
        answer = (pB_given_A * pA) / pB
    statement = (
        f"Suppose event A has prior probability P(A) = {fmt_prob(pA)}.\n"
        f"P(B | A) = {fmt_prob(pB_given_A)} and P(B | A^c) = {fmt_prob(pB_given_notA)}.\n"
        f"Compute P(A | B) using Bayes' theorem."
    )
    explanation = (
        "By Bayes: P(A|B) = P(B|A)P(A) / P(B), where P(B) = P(B|A)P(A) + P(B|A^c)P(A^c).\n"
        f"P(B) = {fmt_prob(pB)}. So P(A|B) = ({fmt_prob(pB_given_A)} * {fmt_prob(pA)}) / {fmt_prob(pB)} = {fmt_prob(answer)}"
    )
    return statement, answer, explanation


def generate_question(ptype=None):
    if ptype is None:
        ptype = random.choice(PROBLEM_TYPES)
    if ptype == "Union: P(A ∪ B)":
        return generate_union_question()
    elif ptype == "Intersection: P(A ∩ B)":
        return generate_intersection_question()
    elif ptype == "Conditional: P(A | B)":
        return generate_conditional_question()
    elif ptype == "Complement: P(A^c)":
        return generate_complement_question()
    elif ptype == "Independence check":
        return generate_independence_check_question()
    elif ptype == "Bayes (P(A|B) via Bayes)":
        return generate_bayes_question()
    else:
        return generate_union_question()


# ----- GUI -----

class ProbabilityPracticeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Probability of Events Practice App")
        self.geometry("760x420")
        self.resizable(False, False)

        self.style = ttk.Style(self)

        # State
        self.current_question = None
        self.current_answer = None
        self.current_explanation = None
        self.attempts = 0
        self.correct = 0

        # Controls
        top_frame = ttk.Frame(self, padding=10)
        top_frame.pack(fill=tk.X)

        ttk.Label(top_frame, text="Problem type:").pack(side=tk.LEFT)
        self.ptype_var = tk.StringVar(value=PROBLEM_TYPES[0])
        self.ptype_combo = ttk.Combobox(top_frame, textvariable=self.ptype_var, values=PROBLEM_TYPES, state='readonly')
        self.ptype_combo.pack(side=tk.LEFT, padx=8)

        self.random_cb_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(top_frame, text="Randomize type", variable=self.random_cb_var).pack(side=tk.LEFT, padx=8)

        ttk.Button(top_frame, text="Generate", command=self.on_generate).pack(side=tk.LEFT, padx=8)
        ttk.Button(top_frame, text="Hint", command=self.on_hint).pack(side=tk.LEFT, padx=8)

        # Problem area
        mid_frame = ttk.Frame(self, padding=10)
        mid_frame.pack(fill=tk.BOTH, expand=True)

        self.problem_text = tk.Text(mid_frame, height=6, wrap=tk.WORD, font=("Segoe UI", 11))
        self.problem_text.pack(fill=tk.X)
        self.problem_text.configure(state=tk.DISABLED)

        ans_frame = ttk.Frame(mid_frame)
        ans_frame.pack(fill=tk.X, pady=10)

        ttk.Label(ans_frame, text="Your answer:").pack(side=tk.LEFT)
        self.answer_var = tk.StringVar()
        self.answer_entry = ttk.Entry(ans_frame, textvariable=self.answer_var, width=20)
        self.answer_entry.pack(side=tk.LEFT, padx=8)

        ttk.Button(ans_frame, text="Check", command=self.on_check).pack(side=tk.LEFT, padx=8)
        ttk.Button(ans_frame, text="Show Explanation", command=self.on_show_explanation).pack(side=tk.LEFT, padx=8)

        # Feedback and score
        bottom_frame = ttk.Frame(self, padding=10)
        bottom_frame.pack(fill=tk.BOTH, expand=True)

        self.feedback_label = ttk.Label(bottom_frame, text="Welcome — generate a question to begin.", anchor=tk.CENTER)
        self.feedback_label.pack(fill=tk.X)

        self.score_label = ttk.Label(bottom_frame, text=self._score_text())
        self.score_label.pack(fill=tk.X, pady=6)

        ttk.Button(bottom_frame, text="Reset Score", command=self.reset_score).pack(side=tk.LEFT)
        ttk.Button(bottom_frame, text="Exit", command=self.destroy).pack(side=tk.RIGHT)

        # Generate first question
        self.on_generate()

    def _score_text(self):
        return f"Attempts: {self.attempts}   Correct: {self.correct}"

    def reset_score(self):
        self.attempts = 0
        self.correct = 0
        self.score_label.config(text=self._score_text())
        self.feedback_label.config(text="Score reset.")

    def on_generate(self):
        ptype = None if self.random_cb_var.get() else self.ptype_var.get()
        q, a, expl = generate_question(ptype)
        self.current_question = q
        self.current_answer = a
        self.current_explanation = expl
        self.answer_var.set("")
        self.feedback_label.config(text="New question generated. Enter answer and click Check.")
        self._display_problem(q)

    def _display_problem(self, text):
        self.problem_text.configure(state=tk.NORMAL)
        self.problem_text.delete('1.0', tk.END)
        self.problem_text.insert(tk.END, text)
        self.problem_text.configure(state=tk.DISABLED)

    def on_hint(self):
        # Provide a short hint based on question type keywords
        q = self.current_question or ""
        hint = "Think about the relevant probability rule."
        if "union" in q.lower() or '∪' in q:
            hint = "Use P(A ∪ B) = P(A) + P(B) - P(A ∩ B)."
        elif 'conditional' in q.lower() or '|' in q:
            hint = "Use P(A | B) = P(A ∩ B) / P(B)."
        elif "complement" in q.lower() or 'A^c' in q:
            hint = "P(A^c) = 1 - P(A)."
        elif 'independent' in q.lower():
            hint = "Check whether P(A ∩ B) equals P(A) * P(B)."
        elif 'bayes' in q.lower() or 'bayes' in self.current_explanation.lower():
            hint = "Compute P(B) first: P(B) = P(B|A)P(A) + P(B|A^c)P(A^c), then apply Bayes."
        messagebox.showinfo("Hint", hint)

    def on_check(self):
        user_text = self.answer_var.get().strip()
        if not user_text:
            messagebox.showwarning("Input needed", "Please enter an answer (decimal or fraction).")
            return
        self.attempts += 1
        # For independence check, answer is yes/no
        try:
            if isinstance(self.current_answer, str):
                # expect 'yes' or 'no'
                got = user_text.lower()
                correct = self.current_answer.lower()
                if got in ('yes', 'y', 'no', 'n'):
                    got_short = 'yes' if got in ('yes', 'y') else 'no'
                else:
                    raise ValueError("Answer must be 'yes' or 'no' for this question.")
                if got_short == correct:
                    self.correct += 1
                    self.feedback_label.config(text=f"Correct — {correct.capitalize()}.")
                else:
                    self.feedback_label.config(text=f"Incorrect. Correct answer: {correct.capitalize()}.")
                self.score_label.config(text=self._score_text())
                return

            # parse numeric answer
            user_val = parse_input(user_text)
            correct_val = float(self.current_answer)
            if close_enough(user_val, correct_val):
                self.correct += 1
                self.feedback_label.config(text=f"Correct — {fmt_prob(correct_val)}.")
            else:
                self.feedback_label.config(text=f"Incorrect — your answer {user_text} vs correct {fmt_prob(correct_val)} (tolerance ±0.01).")
            self.score_label.config(text=self._score_text())
        except Exception as e:
            messagebox.showerror("Error", f"Could not check the answer: {e}")

    def on_show_explanation(self):
        if not self.current_explanation:
            messagebox.showinfo("Explanation", "No explanation available.")
            return
        messagebox.showinfo("Explanation", self.current_explanation)


if __name__ == '__main__':
    app = ProbabilityPracticeApp()
    app.mainloop()

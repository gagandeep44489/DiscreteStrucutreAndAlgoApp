import tkinter as tk
from tkinter import messagebox
from sympy import symbols, Implies, simplify_logic
import random

A, B, C = symbols('A B C')

PUZZLES = [
    {
        "question": "If A implies B and B implies C, and A is True. What is C?",
        "logic": Implies(A, B) & Implies(B, C) & A,
        "answer": True
    },
    {
        "question": "If A AND B is True, and A is True. Is B True?",
        "logic": A & B,
        "answer": True
    },
    {
        "question": "If A OR B is True, and A is False. Is B True?",
        "logic": A | B,
        "answer": True
    }
]

class LogicPuzzleGame:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Logic Puzzle Game")
        self.score = 0
        self.current = random.choice(PUZZLES)

        self.label = tk.Label(root, text=self.current["question"], wraplength=400)
        self.label.pack(pady=10)

        self.var = tk.BooleanVar()

        tk.Radiobutton(root, text="True", variable=self.var, value=True).pack()
        tk.Radiobutton(root, text="False", variable=self.var, value=False).pack()

        tk.Button(root, text="Submit", command=self.check_answer).pack(pady=5)
        tk.Button(root, text="Hint", command=self.show_hint).pack()

        self.score_label = tk.Label(root, text="Score: 0")
        self.score_label.pack(pady=5)

    def check_answer(self):
        if self.var.get() == self.current["answer"]:
            self.score += 1
            messagebox.showinfo("Correct", "Correct logic!")
        else:
            messagebox.showerror("Wrong", "Incorrect reasoning.")
        self.score_label.config(text=f"Score: {self.score}")
        self.next_puzzle()

    def show_hint(self):
        messagebox.showinfo("Hint", "Break the logic into smaller implications.")

    def next_puzzle(self):
        self.current = random.choice(PUZZLES)
        self.label.config(text=self.current["question"])

if __name__ == "__main__":
    root = tk.Tk()
    app = LogicPuzzleGame(root)
    root.mainloop()

# Simplified Logic Quiz App
# Author: Gagandeep Singh
# Purpose: Educational / Logical Reasoning Tool
# Tech Stack: Python, Tkinter

import tkinter as tk
from tkinter import messagebox

class LogicQuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simplified Logic Quiz App")
        self.root.geometry("600x400")

        # Sample questions (Question, Options, Correct Answer)
        self.questions = [
            ("What is the next number in the series: 2, 4, 8, 16, ?", ["18", "32", "24", "20"], "32"),
            ("If all cats are animals and all animals are living beings, are all cats living beings?", ["Yes", "No"], "Yes"),
            ("Which one is the odd one out?", ["Circle", "Triangle", "Square", "Pentagon"], "Circle"),
            ("If A is taller than B and B is taller than C, who is the shortest?", ["A", "B", "C"], "C"),
        ]

        self.current_q = 0
        self.score = 0

        self.create_ui()
        self.show_question()

    def create_ui(self):
        self.question_label = tk.Label(self.root, text="", font=("Arial", 14), wraplength=500)
        self.question_label.pack(pady=20)

        self.options_frame = tk.Frame(self.root)
        self.options_frame.pack(pady=10)

        self.option_vars = []
        self.option_buttons = []

        for i in range(4):  # Max 4 options
            var = tk.StringVar()
            btn = tk.Radiobutton(self.options_frame, text="", variable=var, value="", font=("Arial", 12))
            btn.pack(anchor='w')
            self.option_vars.append(var)
            self.option_buttons.append(btn)

        self.submit_btn = tk.Button(self.root, text="Submit", command=self.check_answer)
        self.submit_btn.pack(pady=20)

    def show_question(self):
        if self.current_q >= len(self.questions):
            messagebox.showinfo("Quiz Completed", f"Your score: {self.score}/{len(self.questions)}")
            self.root.quit()
            return

        q, opts, _ = self.questions[self.current_q]
        self.question_label.config(text=q)

        for i, btn in enumerate(self.option_buttons):
            if i < len(opts):
                btn.config(text=opts[i], value=opts[i], variable=self.option_vars[i])
                btn.pack(anchor='w')
            else:
                btn.pack_forget()

    def check_answer(self):
        _, _, correct = self.questions[self.current_q]
        selected = None
        for var in self.option_vars:
            val = var.get()
            if val:
                selected = val
                break

        if selected == correct:
            self.score += 1

        self.current_q += 1
        self.show_question()

if __name__ == "__main__":
    root = tk.Tk()
    app = LogicQuizApp(root)
    root.mainloop()
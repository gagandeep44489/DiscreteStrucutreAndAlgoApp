import tkinter as tk
from tkinter import messagebox
import random

class SetTrainerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Complement and Difference Trainer")
        self.root.geometry("600x500")

        self.score = 0
        self.total_questions = 0

        self.create_widgets()
        self.generate_sets()

    def create_widgets(self):
        self.title_label = tk.Label(self.root, text="Complement & Difference Trainer",
                                    font=("Arial", 16, "bold"))
        self.title_label.pack(pady=10)

        self.set_display = tk.Label(self.root, text="", font=("Arial", 12))
        self.set_display.pack(pady=10)

        self.question_label = tk.Label(self.root, text="", font=("Arial", 12, "bold"))
        self.question_label.pack(pady=5)

        self.answer_entry = tk.Entry(self.root, width=40)
        self.answer_entry.pack(pady=5)

        self.submit_btn = tk.Button(self.root, text="Submit Answer",
                                    command=self.check_answer)
        self.submit_btn.pack(pady=5)

        self.next_btn = tk.Button(self.root, text="Next Question",
                                  command=self.next_question)
        self.next_btn.pack(pady=5)

        self.score_label = tk.Label(self.root, text="Score: 0/0",
                                    font=("Arial", 12))
        self.score_label.pack(pady=10)

    def generate_sets(self):
        universal = set(random.sample(range(1, 21), 10))
        self.U = universal
        self.A = set(random.sample(list(universal), random.randint(3, 6)))
        self.B = set(random.sample(list(universal), random.randint(3, 6)))

        self.set_display.config(
            text=f"Universal Set U: {sorted(self.U)}\n"
                 f"Set A: {sorted(self.A)}\n"
                 f"Set B: {sorted(self.B)}"
        )

        self.questions = [
            ("A - B", self.A - self.B),
            ("B - A", self.B - self.A),
            ("Complement of A", self.U - self.A),
            ("Complement of B", self.U - self.B),
        ]

        self.current_index = 0
        self.load_question()

    def load_question(self):
        question_text = f"Find: {self.questions[self.current_index][0]}"
        self.question_label.config(text=question_text)
        self.answer_entry.delete(0, tk.END)

    def parse_input(self, user_input):
        try:
            if user_input.strip() == "":
                return set()
            return set(int(x.strip()) for x in user_input.split(","))
        except:
            return None

    def check_answer(self):
        user_input = self.answer_entry.get()
        user_set = self.parse_input(user_input)

        if user_set is None:
            messagebox.showerror("Invalid Input",
                                 "Enter numbers separated by commas (e.g., 1,2,3)")
            return

        correct_set = self.questions[self.current_index][1]

        self.total_questions += 1

        if user_set == correct_set:
            self.score += 1
            messagebox.showinfo("Correct!", "Well done!")
        else:
            messagebox.showinfo(
                "Incorrect",
                f"Correct Answer: {sorted(correct_set)}"
            )

        self.score_label.config(
            text=f"Score: {self.score}/{self.total_questions}"
        )

    def next_question(self):
        if self.current_index < len(self.questions) - 1:
            self.current_index += 1
            self.load_question()
        else:
            messagebox.showinfo("Round Complete",
                                f"Final Score: {self.score}/{self.total_questions}")
            self.generate_sets()


if __name__ == "__main__":
    root = tk.Tk()
    app = SetTrainerApp(root)
    root.mainloop()

import tkinter as tk
from tkinter import messagebox
import random

# --------------------------
# 1. Finite Question Set
# --------------------------
questions = [
    {
        "question": "What is 2 + 2?",
        "options": ["3", "4", "5", "6"],
        "answer": "4"
    },
    {
        "question": "What is the capital of France?",
        "options": ["London", "Berlin", "Paris", "Rome"],
        "answer": "Paris"
    },
    {
        "question": "Which language is used for data science?",
        "options": ["HTML", "Python", "CSS", "Photoshop"],
        "answer": "Python"
    },
    {
        "question": "What is 10 * 5?",
        "options": ["50", "15", "100", "40"],
        "answer": "50"
    },
    {
        "question": "Which data structure uses FIFO?",
        "options": ["Stack", "Queue", "Tree", "Graph"],
        "answer": "Queue"
    }
]

# --------------------------
# 2. Quiz Logic
# --------------------------
score = 0
question_index = 0
random.shuffle(questions)

# --------------------------
# 3. GUI Setup
# --------------------------
root = tk.Tk()
root.title("Finite Set Quiz Generator")
root.geometry("500x350")

tk.Label(root, text="Finite Set Quiz Generator",
         font=("Arial", 16)).pack(pady=10)

question_label = tk.Label(root, text="", wraplength=450, font=("Arial", 12))
question_label.pack(pady=15)

selected_option = tk.StringVar()

option_buttons = []

for i in range(4):
    btn = tk.Radiobutton(root, text="", variable=selected_option,
                         value="", font=("Arial", 11))
    btn.pack(anchor="w")
    option_buttons.append(btn)

# --------------------------
# 4. Load Question
# --------------------------
def load_question():
    global question_index
    if question_index < len(questions):
        q = questions[question_index]
        question_label.config(text=q["question"])
        selected_option.set(None)

        for i, option in enumerate(q["options"]):
            option_buttons[i].config(text=option, value=option)
    else:
        show_result()

# --------------------------
# 5. Submit Answer
# --------------------------
def submit_answer():
    global score, question_index

    if not selected_option.get():
        messagebox.showwarning("Warning", "Please select an answer")
        return

    correct_answer = questions[question_index]["answer"]

    if selected_option.get() == correct_answer:
        score += 1

    question_index += 1
    load_question()

# --------------------------
# 6. Show Result
# --------------------------
def show_result():
    percentage = (score / len(questions)) * 100
    messagebox.showinfo(
        "Quiz Completed",
        f"Your Score: {score}/{len(questions)}\n"
        f"Percentage: {percentage:.2f}%"
    )
    root.destroy()

submit_button = tk.Button(root, text="Submit Answer",
                          command=submit_answer,
                          bg="blue", fg="white")
submit_button.pack(pady=15)

# Start Quiz
load_question()

root.mainloop()

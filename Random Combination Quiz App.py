"""
Random Combination Quiz App
Single-file tkinter desktop application.

Run: save this file as random_combination_quiz.py and run `python random_combination_quiz.py`.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import random

class RandomCombinationQuizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Random Combination Quiz")
        # a reasonable default size; window is resizable
        self.geometry("900x600")
        self.minsize(700, 480)
        self.resizable(True, True)

        # State
        self.items = []
        self.k = 2
        self.num_questions = 5
        self.current_question = 0
        self.score = 0
        self.questions = []  # list of sets
        self.reveal_time_ms = 2500  # milliseconds to reveal the combination

        self._build_ui()

    def _build_ui(self):
        # Use grid on root so resizing works nicely
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)  # make question row expand

        # Top frame - configuration
        cfg_frame = ttk.LabelFrame(self, text="Configuration", padding=8)
        cfg_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=6)
        # let the cfg_frame expand horizontally but not take too much vertical space
        cfg_frame.columnconfigure(0, weight=1)
        cfg_frame.columnconfigure(1, weight=0)
        cfg_frame.columnconfigure(2, weight=0)
        cfg_frame.columnconfigure(3, weight=0)
        cfg_frame.rowconfigure(1, weight=1)

        ttk.Label(cfg_frame, text="Items (comma separated):").grid(row=0, column=0, columnspan=4, sticky="w")
        self.items_text = tk.Text(cfg_frame, height=4, wrap="word")
        self.items_text.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=6)

        ttk.Label(cfg_frame, text="Combination size (k):").grid(row=2, column=0, sticky="w", pady=(4,0))
        self.k_spin = ttk.Spinbox(cfg_frame, from_=1, to=100, width=6, command=self._on_k_change)
        self.k_spin.set(self.k)
        self.k_spin.grid(row=2, column=1, sticky="w", pady=(4,0), padx=(6,0))

        ttk.Label(cfg_frame, text="Number of questions:").grid(row=2, column=2, sticky="w", pady=(4,0))
        self.num_q_spin = ttk.Spinbox(cfg_frame, from_=1, to=2000, width=6)
        self.num_q_spin.set(self.num_questions)
        self.num_q_spin.grid(row=2, column=3, sticky="w", pady=(4,0), padx=(6,0))

        ttk.Label(cfg_frame, text="Reveal time (seconds):").grid(row=3, column=0, sticky="w", pady=(6,0))
        self.reveal_spin = ttk.Spinbox(cfg_frame, from_=1, to=60, width=6)
        self.reveal_spin.set(int(self.reveal_time_ms/1000))
        self.reveal_spin.grid(row=3, column=1, sticky="w", pady=(6,0), padx=(6,0))

        start_btn = ttk.Button(cfg_frame, text="Start Quiz", command=self.start_quiz)
        start_btn.grid(row=3, column=3, sticky="e", padx=(0,6), pady=(6,0))

        # Middle frame - question display (this expands)
        q_frame = ttk.LabelFrame(self, text="Question", padding=8)
        q_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=6)
        q_frame.columnconfigure(0, weight=1)
        q_frame.rowconfigure(0, weight=1)

        self.question_label = ttk.Label(q_frame, text="Press 'Start Quiz' to begin.",
                                        font=(None, 14), wraplength=760, justify="center")
        self.question_label.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        # update wraplength when question frame resizes
        def update_wrap(event):
            # subtract some padding so text doesn't touch edges
            new_wrap = max(200, event.width - 40)
            self.question_label.configure(wraplength=new_wrap)
        q_frame.bind("<Configure>", update_wrap)

        # Bottom frame - answer area and controls
        ans_frame = ttk.LabelFrame(self, text="Answer / Controls", padding=8)
        ans_frame.grid(row=2, column=0, sticky="nsew", padx=8, pady=6)
        ans_frame.columnconfigure(0, weight=1)
        ans_frame.columnconfigure(1, weight=0)

        # Scrollable checkbox area on the left
        checkbox_outer = ttk.Frame(ans_frame)
        checkbox_outer.grid(row=0, column=0, sticky="nsew")
        checkbox_outer.rowconfigure(0, weight=1)
        checkbox_outer.columnconfigure(0, weight=1)

        # Canvas + scrollbar
        self.checkbox_canvas = tk.Canvas(checkbox_outer, highlightthickness=0)
        self.checkbox_canvas.grid(row=0, column=0, sticky="nsew")
        vsb = ttk.Scrollbar(checkbox_outer, orient="vertical", command=self.checkbox_canvas.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.checkbox_canvas.configure(yscrollcommand=vsb.set)

        # Inner frame that will hold checkbuttons
        self.checkbox_container = ttk.Frame(self.checkbox_canvas)
        self.checkbox_window = self.checkbox_canvas.create_window((0,0), window=self.checkbox_container, anchor="nw")

        def _on_checkbox_config(event):
            # update canvas scrollregion
            self.checkbox_canvas.configure(scrollregion=self.checkbox_canvas.bbox("all"))
        self.checkbox_container.bind("<Configure>", _on_checkbox_config)

        def _on_canvas_config(event):
            # keep the inner frame width in sync with canvas width
            canvas_width = event.width
            try:
                self.checkbox_canvas.itemconfigure(self.checkbox_window, width=canvas_width)
            except Exception:
                pass
        self.checkbox_canvas.bind("<Configure>", _on_canvas_config)

        # Controls on the right
        control_frame = ttk.Frame(ans_frame)
        control_frame.grid(row=0, column=1, sticky="ne", padx=(8,0))

        self.submit_btn = ttk.Button(control_frame, text="Submit Answer", command=self.submit_answer, state="disabled")
        self.submit_btn.pack(padx=4, pady=4, fill="x")

        self.next_btn = ttk.Button(control_frame, text="Next", command=self.next_question, state="disabled")
        self.next_btn.pack(padx=4, pady=4, fill="x")

        self.score_label = ttk.Label(control_frame, text=f"Score: {self.score}/{self.num_questions}")
        self.score_label.pack(padx=4, pady=8)

        reset_btn = ttk.Button(control_frame, text="Reset", command=self.reset_quiz)
        reset_btn.pack(padx=4, pady=4, fill="x")

        # some padding for a nicer look
        for child in cfg_frame.winfo_children():
            try:
                child.grid_configure(padx=6, pady=3)
            except Exception:
                pass

    def _on_k_change(self):
        try:
            self.k = int(self.k_spin.get())
        except Exception:
            self.k = 2

    def parse_items(self):
        raw = self.items_text.get("1.0", "end").strip()
        if not raw:
            return []
        # split by comma or newline, strip whitespace, remove empty
        parts = [p.strip() for p in raw.replace('\n', ',').split(',')]
        parts = [p for p in parts if p]
        # remove duplicates while preserving order
        seen = set()
        items = []
        for p in parts:
            if p not in seen:
                seen.add(p)
                items.append(p)
        return items

    def start_quiz(self):
        self.items = self.parse_items()
        if len(self.items) < 1:
            messagebox.showwarning("No items", "Please enter at least one item to quiz on.")
            return
        try:
            self.k = int(self.k_spin.get())
            self.num_questions = int(self.num_q_spin.get())
            self.reveal_time_ms = int(self.reveal_spin.get()) * 1000
        except Exception:
            messagebox.showerror("Invalid input", "Please make sure numeric fields are valid integers.")
            return

        if self.k < 1 or self.k > len(self.items):
            messagebox.showwarning("Invalid combination size", f"Combination size k must be between 1 and {len(self.items)}.")
            return

        # Generate questions as random combinations (allow repeated questions if combinations fewer than num_questions)
        from itertools import combinations
        all_combs = list(combinations(self.items, self.k))
        if not all_combs:
            messagebox.showerror("Error", "Unable to create any combinations with the given items and k.")
            return

        # Shuffle and pick
        random.shuffle(all_combs)
        if len(all_combs) >= self.num_questions:
            chosen = all_combs[:self.num_questions]
        else:
            # allow repeats if not enough unique combinations
            chosen = [random.choice(all_combs) for _ in range(self.num_questions)]

        # Convert to set for easier checking
        self.questions = [set(c) for c in chosen]

        # Reset counters
        self.current_question = 0
        self.score = 0
        self.update_score_label()

        # Disable config controls while quiz is running
        self.submit_btn.config(state="disabled")
        self.next_btn.config(state="disabled")

        self._show_current_question()

    def _show_current_question(self):
        qset = self.questions[self.current_question]
        # Display the combination as a bullet list
        display_text = "\n".join(f"• {item}" for item in qset)
        header = f"Question {self.current_question+1} of {self.num_questions}\n\n"
        self.question_label.config(text=header + display_text)

        # After reveal_time_ms hide the text and show the checkboxes
        self.after(self.reveal_time_ms, self._hide_and_show_checkboxes)

        # Ensure checkboxes area is cleared
        for child in self.checkbox_container.winfo_children():
            child.destroy()

        # disable submit/next until reveal period is over
        self.submit_btn.config(state="disabled")
        self.next_btn.config(state="disabled")

        # Reset scroll to top
        try:
            self.checkbox_canvas.yview_moveto(0)
        except Exception:
            pass

    def _hide_and_show_checkboxes(self):
        # Hide question text
        self.question_label.config(text="Select the items that were shown in the combination.")

        # Create checkboxes for all items inside the inner frame
        self.checkbox_vars = {}
        for child in self.checkbox_container.winfo_children():
            child.destroy()

        # We'll arrange checkboxes in a single column for clarity (scrollable)
        for i, item in enumerate(self.items):
            var = tk.BooleanVar(value=False)
            cb = ttk.Checkbutton(self.checkbox_container, text=item, variable=var)
            cb.grid(row=i, column=0, sticky="w", padx=6, pady=2)
            self.checkbox_vars[item] = var

        # Ensure scrollbar region updated
        self.checkbox_canvas.configure(scrollregion=self.checkbox_canvas.bbox("all"))

        # Enable submit button
        self.submit_btn.config(state="normal")
        # Next remains disabled until after submission
        self.next_btn.config(state="disabled")

    def submit_answer(self):
        # Collect selected items
        selected = {item for item, var in self.checkbox_vars.items() if var.get()}
        correct = self.questions[self.current_question]

        # Compute score for this question: full points only if exact match
        if selected == correct:
            self.score += 1
            message = "Correct!"
        else:
            # give feedback: which were missing and which were extra
            missing = correct - selected
            extra = selected - correct
            parts = []
            if missing:
                parts.append("Missing: " + ", ".join(sorted(missing)))
            if extra:
                parts.append("Incorrect selections: " + ", ".join(sorted(extra)))
            message = "Not quite. " + "; ".join(parts)

        messagebox.showinfo("Result", message)
        self.update_score_label()

        # Disable submit, enable next (or finish)
        self.submit_btn.config(state="disabled")
        if self.current_question + 1 < self.num_questions:
            self.next_btn.config(state="normal")
        else:
            # Quiz finished
            self._finish_quiz()

    def next_question(self):
        self.current_question += 1
        # Clear checkboxes
        for child in self.checkbox_container.winfo_children():
            child.destroy()
        self._show_current_question()

    def update_score_label(self):
        self.score_label.config(text=f"Score: {self.score}/{self.num_questions}")

    def _finish_quiz(self):
        # Clear checkboxes
        for child in self.checkbox_container.winfo_children():
            child.destroy()

        self.question_label.config(text=f"Quiz finished. Your score: {self.score}/{self.num_questions}")
        self.next_btn.config(state="disabled")
        self.submit_btn.config(state="disabled")

    def reset_quiz(self):
        self.items_text.delete("1.0", "end")
        self.k_spin.set(2)
        self.num_q_spin.set(5)
        self.reveal_spin.set(3)
        self.question_label.config(text="Press 'Start Quiz' to begin.")
        for child in self.checkbox_container.winfo_children():
            child.destroy()
        self.score = 0
        self.num_questions = 5
        self.update_score_label()


if __name__ == "__main__":
    app = RandomCombinationQuizApp()
    app.mainloop()

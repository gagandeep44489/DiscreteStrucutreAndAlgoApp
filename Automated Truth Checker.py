import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from textblob import TextBlob

# Optional: For online API calls
# import requests
# from bs4 import BeautifulSoup

class TruthCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Automated Truth Checker")
        self.root.geometry("800x500")

        # Title
        ttk.Label(
            root,
            text="Automated Truth Checker",
            font=("Arial", 18, "bold")
        ).pack(pady=10)

        # Input
        ttk.Label(root, text="Enter a statement or claim:").pack(anchor="w", padx=10)
        self.input_text = scrolledtext.ScrolledText(root, height=10, wrap=tk.WORD)
        self.input_text.pack(fill="both", padx=10, pady=5, expand=True)

        # Buttons
        control_frame = ttk.Frame(root)
        control_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(control_frame, text="Check Truthfulness", command=self.check_truth).pack(side="left")
        ttk.Button(control_frame, text="Clear", command=self.clear_text).pack(side="right")

        # Output
        self.result_label = ttk.Label(root, text="Result: ", font=("Arial", 12, "bold"))
        self.result_label.pack(pady=10)

        self.status_label = ttk.Label(root, text="Status: Ready", foreground="green")
        self.status_label.pack(pady=5)

    def clear_text(self):
        self.input_text.delete("1.0", tk.END)
        self.result_label.config(text="Result: ")
        self.status_label.config(text="Status: Ready", foreground="green")

    def check_truth(self):
        statement = self.input_text.get("1.0", tk.END).strip()
        if not statement:
            messagebox.showwarning("Input Error", "Please enter a statement.")
            return

        self.status_label.config(text="Status: Checking...", foreground="blue")
        self.root.update_idletasks()

        # ---------- Demo Truth Scoring (Offline / Safe) ----------
        # Positive polarity = likely true
        # Negative polarity = likely false
        blob = TextBlob(statement)
        polarity = blob.sentiment.polarity

        # Simple keyword scoring
        truth_keywords = ["official", "confirmed", "report", "data", "study", "verified"]
        false_keywords = ["rumor", "hoax", "fake", "unverified", "false", "alleged"]

        score = 0
        for word in truth_keywords:
            if word in statement.lower():
                score += 1
        for word in false_keywords:
            if word in statement.lower():
                score -= 1

        # Combine polarity and keyword score
        combined_score = polarity + (score * 0.1)

        # Determine truthfulness
        if combined_score > 0.2:
            result = "Likely True"
        elif combined_score < -0.1:
            result = "Likely False"
        else:
            result = "Uncertain / Needs Verification"

        self.result_label.config(text=f"Result: {result} (Score: {combined_score:.2f})")
        self.status_label.config(text="Status: Completed", foreground="green")


if __name__ == "__main__":
    root = tk.Tk()
    app = TruthCheckerApp(root)
    root.mainloop()

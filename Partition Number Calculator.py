"""
Partition Number Calculator (desktop app)
- Save as partition_calculator.py
- Run with: python partition_calculator.py

Features:
- Compute exact partition number p(n) using Euler's pentagonal theorem recurrence.
- Handles reasonably large n (depends on machine memory/time).
- Shows computation time and keeps a session history.
- Option to export history to a text file.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time
import math

# -----------------------
# Partition number logic
# -----------------------
from functools import lru_cache

@lru_cache(maxsize=None)
def partition(n: int) -> int:
    """
    Return the partition number p(n) using Euler's recurrence with generalized pentagonal numbers.
    p(0) = 1, p(n<0) = 0
    This function uses memoization (lru_cache) to speed up repeated requests.

    Complexity: roughly O(n * sqrt(n)) in naive loops; the recurrence uses about sqrt(n) terms per n.
    """
    if n < 0:
        return 0
    if n == 0:
        return 1

    total = 0
    k = 1
    # signs go + + - - + + - - ...
    while True:
        # generalized pentagonal numbers: g(k) = k*(3k-1)/2 and g(-k) = k*(3k+1)/2
        g1 = k * (3 * k - 1) // 2
        g2 = k * (3 * k + 1) // 2

        if g1 > n and g2 > n:
            break

        sign = 1 if (k % 2 == 1) else -1  # + for k odd, - for k even

        if g1 <= n:
            total += sign * partition(n - g1)
        if g2 <= n:
            total += sign * partition(n - g2)

        k += 1

    return total

# -----------------------
# GUI (Tkinter)
# -----------------------
class PartitionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Partition Number Calculator")
        self.geometry("640x420")
        self.minsize(540, 380)

        # Style
        style = ttk.Style(self)
        style.configure("TButton", padding=6)
        style.configure("TLabel", padding=4)

        # Input frame
        input_frame = ttk.Frame(self, padding=10)
        input_frame.pack(fill='x')

        ttk.Label(input_frame, text="Enter a non-negative integer n:").pack(side='left')
        self.n_var = tk.StringVar()
        self.entry = ttk.Entry(input_frame, textvariable=self.n_var, width=14)
        self.entry.pack(side='left', padx=(8, 8))
        self.entry.bind("<Return>", lambda e: self.compute())

        self.compute_btn = ttk.Button(input_frame, text="Compute p(n)", command=self.compute)
        self.compute_btn.pack(side='left')

        clear_btn = ttk.Button(input_frame, text="Clear History", command=self.clear_history)
        clear_btn.pack(side='right')

        # Result frame
        result_frame = ttk.LabelFrame(self, text="Result", padding=10)
        result_frame.pack(fill='both', padx=10, pady=(6,10), expand=False)

        self.result_text = tk.Text(result_frame, height=4, wrap='word', state='disabled')
        self.result_text.pack(fill='both', expand=True)

        # History frame
        history_frame = ttk.LabelFrame(self, text="Session History (n → p(n), time)", padding=10)
        history_frame.pack(fill='both', padx=10, pady=(0,10), expand=True)

        self.history_listbox = tk.Listbox(history_frame)
        self.history_listbox.pack(side='left', fill='both', expand=True)
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.history_listbox.config(yscrollcommand=scrollbar.set)

        # Export / About
        bottom_frame = ttk.Frame(self, padding=8)
        bottom_frame.pack(fill='x')
        export_btn = ttk.Button(bottom_frame, text="Export History", command=self.export_history)
        export_btn.pack(side='left')
        about_btn = ttk.Button(bottom_frame, text="About", command=self.show_about)
        about_btn.pack(side='right')

        # Keep track of history as list of tuples
        self.history = []

    def compute(self):
        s = self.n_var.get().strip()
        if s == "":
            messagebox.showinfo("Input required", "Please enter a non-negative integer.")
            return

        # Validate integer input
        try:
            n = int(s)
        except ValueError:
            messagebox.showerror("Invalid input", f"'{s}' is not an integer. Enter a non-negative integer.")
            return

        if n < 0:
            messagebox.showerror("Invalid input", "Please enter a non-negative integer (n >= 0).")
            return

        # Disable compute button while working
        self.compute_btn.config(state='disabled')
        self.update_idletasks()

        start = time.time()
        try:
            value = partition(n)
        except RecursionError:
            # For extremely large n, recursion depth could be problematic; inform user
            messagebox.showerror("Computation error", "Recursion limit reached for this n. Try a smaller n.")
            self.compute_btn.config(state='normal')
            return
        end = time.time()

        elapsed = end - start
        elapsed_str = f"{elapsed:.4f} s"

        # Display result
        res_str = f"p({n}) = {value}\nComputed in {elapsed_str}"
        self._set_result_text(res_str)

        # Update history
        hist_item = f"{n} → {value}    ({elapsed_str})"
        self.history.append((n, value, elapsed))
        self.history_listbox.insert('end', hist_item)
        # Auto-scroll to last
        self.history_listbox.see('end')

        # Re-enable
        self.compute_btn.config(state='normal')

    def _set_result_text(self, txt: str):
        self.result_text.config(state='normal')
        self.result_text.delete('1.0', 'end')
        self.result_text.insert('end', txt)
        self.result_text.config(state='disabled')

    def clear_history(self):
        if not self.history:
            return
        if messagebox.askyesno("Clear history", "Are you sure you want to clear the session history?"):
            self.history.clear()
            self.history_listbox.delete(0, 'end')

    def export_history(self):
        if not self.history:
            messagebox.showinfo("No history", "No history to export.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Export history to..."
        )
        if not file_path:
            return
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("Partition Number Calculator - Session History\n")
                f.write("n\tp(n)\ttime_seconds\n")
                for n, val, t in self.history:
                    f.write(f"{n}\t{val}\t{t:.6f}\n")
            messagebox.showinfo("Exported", f"History exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export failed", f"Could not export history:\n{e}")

    def show_about(self):
        about_text = (
            "Partition Number Calculator\n\n"
            "Computes exact partition numbers p(n) using Euler's "
            "generalized pentagonal recurrence.\n\n"
            "Author: Generated by ChatGPT\n"
            "Notes:\n"
            "- p(0) = 1\n"
            "- Computation is exact but may become slow for very large n (thousands+).\n"
            "- Uses memoization, so repeated calculations are fast.\n"
        )
        messagebox.showinfo("About", about_text)

# -----------------------
# Run the app
# -----------------------
def main():
    app = PartitionApp()
    app.mainloop()

if __name__ == "__main__":
    main()

import tkinter as tk
from tkinter import ttk, messagebox


class DynamicProgrammingPatternSolver:
    def __init__(self, root):
        self.root = root
        self.root.title("Dynamic Programming Pattern Solver")
        self.root.geometry("860x680")

        tk.Label(
            root,
            text="Dynamic Programming Pattern Solver",
            font=("Arial", 18, "bold"),
        ).pack(pady=10)

        tk.Label(
            root,
            text=(
                "Choose a classic DP pattern and provide inputs.\n"
                "Examples are shown under each input field."
            ),
            justify="center",
        ).pack(pady=4)

        form = tk.Frame(root)
        form.pack(pady=8)

        tk.Label(form, text="Pattern:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.pattern = ttk.Combobox(
            form,
            values=[
                "Fibonacci (1D DP)",
                "0/1 Knapsack (Include/Exclude)",
                "Longest Common Subsequence (2D DP)",
                "Coin Change - Minimum Coins",
            ],
            width=42,
            state="readonly",
        )
        self.pattern.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.pattern.bind("<<ComboboxSelected>>", self.update_input_hints)

        self.input1_label = tk.Label(form, text="Input 1")
        self.input1_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.input1_entry = tk.Entry(form, width=52)
        self.input1_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        self.input2_label = tk.Label(form, text="Input 2")
        self.input2_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.input2_entry = tk.Entry(form, width=52)
        self.input2_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        self.input3_label = tk.Label(form, text="Input 3")
        self.input3_label.grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.input3_entry = tk.Entry(form, width=52)
        self.input3_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        button_row = tk.Frame(root)
        button_row.pack(pady=8)

        tk.Button(button_row, text="Solve", command=self.solve_pattern).grid(
            row=0, column=0, padx=5
        )
        tk.Button(button_row, text="Clear", command=self.clear_output).grid(
            row=0, column=1, padx=5
        )

        self.output = tk.Text(root, height=24, width=102)
        self.output.pack(pady=10)

        self.pattern.current(0)
        self.update_input_hints()

    def update_input_hints(self, _event=None):
        selected = self.pattern.get()

        if selected == "Fibonacci (1D DP)":
            self.input1_label.config(text="n")
            self.input2_label.config(text="Input 2 (unused)")
            self.input3_label.config(text="Input 3 (unused)")

            self.input1_entry.delete(0, tk.END)
            self.input1_entry.insert(0, "10")
            self.input2_entry.delete(0, tk.END)
            self.input3_entry.delete(0, tk.END)

        elif selected == "0/1 Knapsack (Include/Exclude)":
            self.input1_label.config(text="Weights (comma separated)")
            self.input2_label.config(text="Values (comma separated)")
            self.input3_label.config(text="Capacity")

            self.input1_entry.delete(0, tk.END)
            self.input1_entry.insert(0, "2,3,4,5")
            self.input2_entry.delete(0, tk.END)
            self.input2_entry.insert(0, "3,4,5,8")
            self.input3_entry.delete(0, tk.END)
            self.input3_entry.insert(0, "5")

        elif selected == "Longest Common Subsequence (2D DP)":
            self.input1_label.config(text="String 1")
            self.input2_label.config(text="String 2")
            self.input3_label.config(text="Input 3 (unused)")

            self.input1_entry.delete(0, tk.END)
            self.input1_entry.insert(0, "ABCBDAB")
            self.input2_entry.delete(0, tk.END)
            self.input2_entry.insert(0, "BDCAB")
            self.input3_entry.delete(0, tk.END)

        else:
            self.input1_label.config(text="Coins (comma separated)")
            self.input2_label.config(text="Target Amount")
            self.input3_label.config(text="Input 3 (unused)")

            self.input1_entry.delete(0, tk.END)
            self.input1_entry.insert(0, "1,3,4")
            self.input2_entry.delete(0, tk.END)
            self.input2_entry.insert(0, "6")
            self.input3_entry.delete(0, tk.END)

    def clear_output(self):
        self.output.delete(1.0, tk.END)

    def solve_pattern(self):
        self.output.delete(1.0, tk.END)
        selected = self.pattern.get()

        try:
            if selected == "Fibonacci (1D DP)":
                n = int(self.input1_entry.get())
                value, trace = self.solve_fibonacci(n)
                self.output.insert(tk.END, "Pattern: 1D DP (Fibonacci)\n")
                self.output.insert(tk.END, f"F({n}) = {value}\n\n")
                self.output.insert(tk.END, trace)

            elif selected == "0/1 Knapsack (Include/Exclude)":
                weights = self.parse_int_list(self.input1_entry.get())
                values = self.parse_int_list(self.input2_entry.get())
                capacity = int(self.input3_entry.get())

                if len(weights) != len(values):
                    raise ValueError("Weights and values must have the same length.")

                best, trace = self.solve_knapsack(weights, values, capacity)
                self.output.insert(tk.END, "Pattern: Include/Exclude DP (0/1 Knapsack)\n")
                self.output.insert(tk.END, f"Best Value = {best}\n\n")
                self.output.insert(tk.END, trace)

            elif selected == "Longest Common Subsequence (2D DP)":
                s1 = self.input1_entry.get().strip()
                s2 = self.input2_entry.get().strip()
                length, sequence, trace = self.solve_lcs(s1, s2)
                self.output.insert(tk.END, "Pattern: 2D Grid DP (LCS)\n")
                self.output.insert(tk.END, f"LCS Length = {length}\n")
                self.output.insert(tk.END, f"LCS Sequence = {sequence}\n\n")
                self.output.insert(tk.END, trace)

            else:
                coins = self.parse_int_list(self.input1_entry.get())
                amount = int(self.input2_entry.get())
                minimum, trace = self.solve_coin_change(coins, amount)
                self.output.insert(tk.END, "Pattern: Unbounded Choice DP (Coin Change)\n")
                self.output.insert(tk.END, f"Minimum Coins for {amount} = {minimum}\n\n")
                self.output.insert(tk.END, trace)

        except ValueError as error:
            messagebox.showerror("Input Error", str(error))
        except Exception:
            messagebox.showerror("Error", "Invalid input provided.")

    @staticmethod
    def parse_int_list(raw_text):
        values = [item.strip() for item in raw_text.split(",") if item.strip()]
        if not values:
            raise ValueError("Please provide at least one integer.")
        return [int(item) for item in values]

    @staticmethod
    def solve_fibonacci(n):
        if n < 0:
            raise ValueError("n must be non-negative.")
        if n <= 1:
            return n, f"DP Table: [{n}]"

        dp = [0] * (n + 1)
        dp[1] = 1
        for i in range(2, n + 1):
            dp[i] = dp[i - 1] + dp[i - 2]

        return dp[n], f"DP Table: {dp}"

    @staticmethod
    def solve_knapsack(weights, values, capacity):
        if capacity < 0:
            raise ValueError("Capacity cannot be negative.")

        n = len(weights)
        dp = [[0] * (capacity + 1) for _ in range(n + 1)]

        for i in range(1, n + 1):
            for c in range(capacity + 1):
                if weights[i - 1] <= c:
                    include = values[i - 1] + dp[i - 1][c - weights[i - 1]]
                    exclude = dp[i - 1][c]
                    dp[i][c] = max(include, exclude)
                else:
                    dp[i][c] = dp[i - 1][c]

        lines = ["DP Table:"]
        for row in dp:
            lines.append(" ".join(f"{value:3d}" for value in row))

        return dp[n][capacity], "\n".join(lines)

    @staticmethod
    def solve_lcs(s1, s2):
        if not s1 or not s2:
            raise ValueError("Both strings are required for LCS.")

        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i - 1] == s2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

        sequence_chars = []
        i, j = m, n
        while i > 0 and j > 0:
            if s1[i - 1] == s2[j - 1]:
                sequence_chars.append(s1[i - 1])
                i -= 1
                j -= 1
            elif dp[i - 1][j] >= dp[i][j - 1]:
                i -= 1
            else:
                j -= 1

        sequence = "".join(reversed(sequence_chars))

        lines = ["DP Table:"]
        for row in dp:
            lines.append(" ".join(f"{value:2d}" for value in row))

        return dp[m][n], sequence, "\n".join(lines)

    @staticmethod
    def solve_coin_change(coins, amount):
        if amount < 0:
            raise ValueError("Amount cannot be negative.")
        if any(coin <= 0 for coin in coins):
            raise ValueError("Coin values must be positive integers.")

        inf = float("inf")
        dp = [0] + [inf] * amount

        for total in range(1, amount + 1):
            for coin in coins:
                if coin <= total and dp[total - coin] != inf:
                    dp[total] = min(dp[total], dp[total - coin] + 1)

        minimum = dp[amount] if dp[amount] != inf else -1
        formatted = ["∞" if value == inf else str(value) for value in dp]
        trace = f"DP Array: [{', '.join(formatted)}]"

        return minimum, trace


if __name__ == "__main__":
    root = tk.Tk()
    app = DynamicProgrammingPatternSolver(root)
    root.mainloop()
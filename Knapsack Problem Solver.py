import tkinter as tk
from tkinter import messagebox


class KnapsackSolverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Knapsack Problem Solver")
        self.root.geometry("900x700")
        self.root.resizable(False, False)

        self.create_widgets()

    def create_widgets(self):
        tk.Label(
            self.root,
            text="Knapsack Problem Solver (0/1)",
            font=("Arial", 16, "bold"),
        ).pack(pady=10)

        instructions = (
            "Enter item values and weights as comma-separated numbers.\n"
            "Example Values: 60,100,120\n"
            "Example Weights: 10,20,30"
        )
        tk.Label(self.root, text=instructions, justify="center").pack(pady=5)

        tk.Label(self.root, text="Item Values:").pack()
        self.entry_values = tk.Entry(self.root, width=65)
        self.entry_values.pack(pady=5)

        tk.Label(self.root, text="Item Weights:").pack()
        self.entry_weights = tk.Entry(self.root, width=65)
        self.entry_weights.pack(pady=5)

        tk.Label(self.root, text="Knapsack Capacity:").pack()
        self.entry_capacity = tk.Entry(self.root, width=25)
        self.entry_capacity.pack(pady=5)

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=12)

        tk.Button(
            button_frame,
            text="Solve",
            width=15,
            command=self.solve_knapsack,
        ).grid(row=0, column=0, padx=8)

        tk.Button(
            button_frame,
            text="Reset",
            width=15,
            command=self.reset_fields,
        ).grid(row=0, column=1, padx=8)

        tk.Button(
            button_frame,
            text="Load Sample",
            width=15,
            command=self.load_sample,
        ).grid(row=0, column=2, padx=8)

        tk.Label(self.root, text="Result", font=("Arial", 13, "bold")).pack(pady=5)
        self.result_text = tk.Text(self.root, width=105, height=22, wrap="word")
        self.result_text.pack(padx=10, pady=8)
        self.result_text.configure(state="disabled")

    def parse_input_list(self, text):
        return [int(x.strip()) for x in text.split(",") if x.strip()]

    def solve_knapsack(self):
        try:
            values = self.parse_input_list(self.entry_values.get())
            weights = self.parse_input_list(self.entry_weights.get())
            capacity = int(self.entry_capacity.get())

            if capacity < 0:
                raise ValueError("Capacity must be non-negative")
            if not values or not weights:
                raise ValueError("Values and weights cannot be empty")
            if len(values) != len(weights):
                raise ValueError("Values and weights must have same number of items")
            if any(w <= 0 for w in weights):
                raise ValueError("Weights must be positive integers")

            max_value, selected_items, dp_table = self.knapsack_01(values, weights, capacity)
            self.display_result(values, weights, capacity, max_value, selected_items, dp_table)

        except ValueError as error:
            messagebox.showerror("Input Error", f"Invalid input: {error}")
        except Exception:
            messagebox.showerror("Error", "Unexpected error occurred while solving.")

    def knapsack_01(self, values, weights, capacity):
        n = len(values)
        dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]

        for i in range(1, n + 1):
            current_value = values[i - 1]
            current_weight = weights[i - 1]
            for c in range(capacity + 1):
                if current_weight <= c:
                    dp[i][c] = max(
                        dp[i - 1][c],
                        dp[i - 1][c - current_weight] + current_value,
                    )
                else:
                    dp[i][c] = dp[i - 1][c]

        selected_items = []
        c = capacity
        for i in range(n, 0, -1):
            if dp[i][c] != dp[i - 1][c]:
                selected_items.append(i - 1)
                c -= weights[i - 1]

        selected_items.reverse()
        return dp[n][capacity], selected_items, dp

    def display_result(self, values, weights, capacity, max_value, selected_items, dp_table):
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", tk.END)

        self.result_text.insert(tk.END, "========== Knapsack Solution ==========" + "\n")
        self.result_text.insert(tk.END, f"Capacity: {capacity}\n")
        self.result_text.insert(tk.END, f"Maximum Value: {max_value}\n\n")

        if selected_items:
            self.result_text.insert(tk.END, "Selected Items (0-based index):\n")
            total_weight = 0
            total_value = 0
            for index in selected_items:
                self.result_text.insert(
                    tk.END,
                    f"  Item {index}: Value={values[index]}, Weight={weights[index]}\n",
                )
                total_weight += weights[index]
                total_value += values[index]

            self.result_text.insert(tk.END, "\n")
            self.result_text.insert(tk.END, f"Total Selected Weight: {total_weight}\n")
            self.result_text.insert(tk.END, f"Total Selected Value: {total_value}\n\n")
        else:
            self.result_text.insert(tk.END, "No items selected.\n\n")

        self.result_text.insert(tk.END, "DP Table (rows: items, columns: capacity):\n")
        for row_index, row in enumerate(dp_table):
            row_label = f"i={row_index:>2}: "
            row_values = " ".join(f"{value:>4}" for value in row)
            self.result_text.insert(tk.END, row_label + row_values + "\n")

        self.result_text.configure(state="disabled")

    def load_sample(self):
        self.entry_values.delete(0, tk.END)
        self.entry_weights.delete(0, tk.END)
        self.entry_capacity.delete(0, tk.END)

        self.entry_values.insert(0, "60,100,120")
        self.entry_weights.insert(0, "10,20,30")
        self.entry_capacity.insert(0, "50")

        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, "Sample data loaded. Click Solve to run.\n")
        self.result_text.configure(state="disabled")

    def reset_fields(self):
        self.entry_values.delete(0, tk.END)
        self.entry_weights.delete(0, tk.END)
        self.entry_capacity.delete(0, tk.END)

        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.configure(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = KnapsackSolverApp(root)
    root.mainloop()
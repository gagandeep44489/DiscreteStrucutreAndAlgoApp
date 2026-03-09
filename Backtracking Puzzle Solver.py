import tkinter as tk
from tkinter import messagebox


class BacktrackingPuzzleSolver:
    def __init__(self, root):
        self.root = root
        self.root.title("Backtracking Puzzle Solver (N-Queens)")
        self.root.geometry("820x680")
        self.root.resizable(False, False)

        self.create_widgets()

    def create_widgets(self):
        tk.Label(
            self.root,
            text="Backtracking Puzzle Solver",
            font=("Arial", 18, "bold"),
        ).pack(pady=10)

        tk.Label(
            self.root,
            text="Solve the N-Queens puzzle using Backtracking",
            font=("Arial", 11),
        ).pack(pady=3)

        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=8)

        tk.Label(input_frame, text="Board Size (N):", font=("Arial", 11)).grid(
            row=0, column=0, padx=6
        )
        self.entry_n = tk.Entry(input_frame, width=12)
        self.entry_n.grid(row=0, column=1, padx=6)
        self.entry_n.insert(0, "8")

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=8)

        tk.Button(
            button_frame,
            text="Solve",
            width=12,
            bg="#4CAF50",
            fg="white",
            command=self.solve,
        ).grid(row=0, column=0, padx=6)

        tk.Button(
            button_frame,
            text="Reset",
            width=12,
            bg="#f44336",
            fg="white",
            command=self.reset,
        ).grid(row=0, column=1, padx=6)

        result_frame = tk.Frame(self.root)
        result_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(result_frame)
        scrollbar.pack(side="right", fill="y")

        self.output = tk.Text(
            result_frame,
            wrap="none",
            yscrollcommand=scrollbar.set,
            font=("Courier New", 11),
            height=28,
            width=95,
        )
        self.output.pack(fill="both", expand=True)
        scrollbar.config(command=self.output.yview)

        self.status_var = tk.StringVar(value="Enter board size N (4 to 12) and click Solve.")
        tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Arial", 10, "italic"),
            fg="#333333",
        ).pack(pady=4)

    def is_safe(self, board, row, col, n):
        for i in range(col):
            if board[row][i] == 1:
                return False

        i, j = row, col
        while i >= 0 and j >= 0:
            if board[i][j] == 1:
                return False
            i -= 1
            j -= 1

        i, j = row, col
        while i < n and j >= 0:
            if board[i][j] == 1:
                return False
            i += 1
            j -= 1

        return True

    def solve_backtracking(self, board, col, n, placements):
        if col >= n:
            return True

        for row in range(n):
            placements["attempts"] += 1
            if self.is_safe(board, row, col, n):
                board[row][col] = 1
                placements["placed"] += 1

                if self.solve_backtracking(board, col + 1, n, placements):
                    return True

                board[row][col] = 0
                placements["backtracks"] += 1

        return False

    def format_board(self, board):
        n = len(board)
        separator = "+" + "---+" * n + "\n"
        board_view = separator

        for row in board:
            row_cells = "|"
            for cell in row:
                row_cells += " Q |" if cell == 1 else " . |"
            board_view += row_cells + "\n" + separator

        return board_view

    def solve(self):
        try:
            n = int(self.entry_n.get().strip())
            if n < 4 or n > 12:
                messagebox.showerror("Invalid Input", "Please enter N between 4 and 12.")
                return

            self.output.delete("1.0", tk.END)
            board = [[0 for _ in range(n)] for _ in range(n)]
            stats = {"attempts": 0, "placed": 0, "backtracks": 0}

            solved = self.solve_backtracking(board, 0, n, stats)

            if solved:
                board_visual = self.format_board(board)
                self.output.insert(tk.END, f"Solved {n}-Queens Puzzle\n\n")
                self.output.insert(tk.END, board_visual)
                self.output.insert(
                    tk.END,
                    "\nStatistics:\n"
                    f"- Safety checks / attempts: {stats['attempts']}\n"
                    f"- Queen placements: {stats['placed']}\n"
                    f"- Backtracks: {stats['backtracks']}\n",
                )
                self.status_var.set(f"Solution found for N = {n}.")
            else:
                self.output.insert(tk.END, f"No solution exists for N = {n}.\n")
                self.status_var.set(f"No solution found for N = {n}.")

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer for N.")

    def reset(self):
        self.entry_n.delete(0, tk.END)
        self.entry_n.insert(0, "8")
        self.output.delete("1.0", tk.END)
        self.status_var.set("Enter board size N (4 to 12) and click Solve.")


if __name__ == "__main__":
    root = tk.Tk()
    app = BacktrackingPuzzleSolver(root)
    root.mainloop()
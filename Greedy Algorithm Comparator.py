import tkinter as tk
from tkinter import messagebox, ttk


class GreedyAlgorithmComparator:
    def __init__(self, root):
        self.root = root
        self.root.title("Greedy Algorithm Comparator")
        self.root.geometry("1050x680")

        title = tk.Label(
            root,
            text="Compare Multiple Greedy Strategies for Activity Scheduling",
            font=("Arial", 14, "bold"),
        )
        title.pack(pady=10)

        instructions = (
            "Enter one activity per line in this format:\n"
            "name,start,end,profit\n"
            "Example: A,1,4,20"
        )
        tk.Label(root, text=instructions, justify=tk.LEFT).pack(anchor="w", padx=12)

        self.input_text = tk.Text(root, height=9, width=90)
        self.input_text.pack(padx=12, pady=8, fill=tk.X)
        self.input_text.insert(
            tk.END,
            "A,1,4,20\n"
            "B,3,5,10\n"
            "C,0,6,40\n"
            "D,5,7,30\n"
            "E,8,9,25\n"
            "F,5,9,60\n"
            "G,6,10,35\n"
            "H,8,11,45\n",
        )

        button_frame = tk.Frame(root)
        button_frame.pack(fill=tk.X, padx=12)

        tk.Button(button_frame, text="Compare Greedy Strategies", command=self.run_comparison).pack(
            side=tk.LEFT, pady=6
        )
        tk.Button(button_frame, text="Load Sample", command=self.load_sample).pack(side=tk.LEFT, padx=8)
        tk.Button(button_frame, text="Clear", command=self.clear_all).pack(side=tk.LEFT)

        self.tree_frame = tk.Frame(root)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        self.columns = ["Name", "Start", "End", "Profit", "Duration"]
        self.tree = ttk.Treeview(self.tree_frame, columns=self.columns, show="headings", height=10)
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)

        result_label = tk.Label(root, text="Strategy Results", font=("Arial", 12, "bold"))
        result_label.pack(anchor="w", padx=12)

        self.result_text = tk.Text(root, height=11, width=120)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=12, pady=(4, 12))

    def load_sample(self):
        self.clear_all()
        self.input_text.insert(
            tk.END,
            "A,1,3,30\n"
            "B,2,5,20\n"
            "C,4,6,25\n"
            "D,6,7,50\n"
            "E,5,8,28\n"
            "F,7,9,22\n"
            "G,8,10,35\n",
        )

    def clear_all(self):
        self.input_text.delete("1.0", tk.END)
        self.result_text.delete("1.0", tk.END)
        for row in self.tree.get_children():
            self.tree.delete(row)

    def parse_activities(self):
        raw = self.input_text.get("1.0", tk.END).strip().splitlines()
        activities = []

        if not raw:
            raise ValueError("Please provide at least one activity.")

        for line_no, line in enumerate(raw, start=1):
            parts = [p.strip() for p in line.split(",")]
            if len(parts) != 4:
                raise ValueError(
                    f"Line {line_no}: expected 4 values (name,start,end,profit)."
                )

            name, start_txt, end_txt, profit_txt = parts
            try:
                start = float(start_txt)
                end = float(end_txt)
                profit = float(profit_txt)
            except ValueError:
                raise ValueError(
                    f"Line {line_no}: start, end, and profit must be numeric values."
                )

            if end <= start:
                raise ValueError(f"Line {line_no}: end time must be greater than start time.")

            activities.append(
                {
                    "name": name,
                    "start": start,
                    "end": end,
                    "profit": profit,
                    "duration": end - start,
                }
            )

        return activities

    @staticmethod
    def compatible(last_end, activity):
        return activity["start"] >= last_end

    def earliest_finish_time(self, activities):
        ordered = sorted(activities, key=lambda x: (x["end"], x["start"]))
        chosen = []
        last_end = float("-inf")

        for act in ordered:
            if self.compatible(last_end, act):
                chosen.append(act)
                last_end = act["end"]

        return chosen

    def highest_profit_first(self, activities):
        ordered = sorted(activities, key=lambda x: (-x["profit"], x["end"]))
        chosen = []
        last_end = float("-inf")

        for act in ordered:
            if self.compatible(last_end, act):
                chosen.append(act)
                last_end = act["end"]

        return chosen

    def best_profit_density(self, activities):
        ordered = sorted(
            activities,
            key=lambda x: (-(x["profit"] / x["duration"]), x["end"]),
        )
        chosen = []
        last_end = float("-inf")

        for act in ordered:
            if self.compatible(last_end, act):
                chosen.append(act)
                last_end = act["end"]

        return chosen

    @staticmethod
    def summarize(selection):
        total_profit = sum(a["profit"] for a in selection)
        total_time = sum(a["duration"] for a in selection)
        names = [a["name"] for a in sorted(selection, key=lambda x: x["start"])]
        return total_profit, total_time, names

    def show_activities(self, activities):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for act in sorted(activities, key=lambda x: x["start"]):
            self.tree.insert(
                "",
                tk.END,
                values=(
                    act["name"],
                    f"{act['start']:.2f}",
                    f"{act['end']:.2f}",
                    f"{act['profit']:.2f}",
                    f"{act['duration']:.2f}",
                ),
            )

    def run_comparison(self):
        try:
            activities = self.parse_activities()
        except ValueError as err:
            messagebox.showerror("Input Error", str(err))
            return

        self.show_activities(activities)

        strategies = {
            "Earliest Finish Time": self.earliest_finish_time(activities),
            "Highest Profit First": self.highest_profit_first(activities),
            "Best Profit Density": self.best_profit_density(activities),
        }

        self.result_text.delete("1.0", tk.END)

        best_name = None
        best_profit = float("-inf")

        for strategy_name, selection in strategies.items():
            total_profit, total_time, names = self.summarize(selection)
            if total_profit > best_profit:
                best_profit = total_profit
                best_name = strategy_name

            self.result_text.insert(tk.END, f"{strategy_name}\n")
            self.result_text.insert(tk.END, f"  Selected activities: {', '.join(names) if names else 'None'}\n")
            self.result_text.insert(tk.END, f"  Total activities : {len(selection)}\n")
            self.result_text.insert(tk.END, f"  Total busy time  : {total_time:.2f}\n")
            self.result_text.insert(tk.END, f"  Total profit     : {total_profit:.2f}\n\n")

        self.result_text.insert(
            tk.END,
            f"Best strategy for this input (by total profit): {best_name} ({best_profit:.2f})\n",
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = GreedyAlgorithmComparator(root)
    root.mainloop()
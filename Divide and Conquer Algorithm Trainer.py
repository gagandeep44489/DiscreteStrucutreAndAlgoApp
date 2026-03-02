import tkinter as tk
from tkinter import ttk, messagebox


class DivideAndConquerTrainer:
    def __init__(self, root):
        self.root = root
        self.root.title("Divide and Conquer Algorithm Trainer")
        self.root.geometry("980x640")

        self.algorithm_var = tk.StringVar(value="Binary Search")

        header = tk.Frame(root)
        header.pack(fill=tk.X, padx=12, pady=(10, 6))

        tk.Label(
            header,
            text="Choose Algorithm",
            font=("Arial", 11, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=(0, 8))

        chooser = ttk.Combobox(
            header,
            textvariable=self.algorithm_var,
            state="readonly",
            width=30,
            values=["Binary Search", "Merge Sort", "Quick Sort"],
        )
        chooser.grid(row=0, column=1, sticky="w")
        chooser.bind("<<ComboboxSelected>>", self.update_template)

        tk.Button(header, text="Load Example", command=self.load_example).grid(
            row=0, column=2, padx=8
        )
        tk.Button(header, text="Run Trainer", command=self.run_trainer).grid(row=0, column=3)

        input_frame = tk.LabelFrame(root, text="Input")
        input_frame.pack(fill=tk.X, padx=12, pady=6)

        tk.Label(input_frame, text="Array (comma-separated integers):").grid(
            row=0, column=0, sticky="w", padx=8, pady=(8, 4)
        )
        self.array_entry = tk.Entry(input_frame, width=90)
        self.array_entry.grid(row=1, column=0, padx=8, pady=(0, 8), sticky="we")

        tk.Label(input_frame, text="Target (for Binary Search only):").grid(
            row=2, column=0, sticky="w", padx=8, pady=(2, 4)
        )
        self.target_entry = tk.Entry(input_frame, width=30)
        self.target_entry.grid(row=3, column=0, padx=8, pady=(0, 8), sticky="w")

        input_frame.grid_columnconfigure(0, weight=1)

        notebook = ttk.Notebook(root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=(6, 12))

        steps_frame = tk.Frame(notebook)
        summary_frame = tk.Frame(notebook)

        notebook.add(steps_frame, text="Step-by-Step Trace")
        notebook.add(summary_frame, text="Concept Summary")

        self.steps_box = tk.Text(steps_frame, wrap="word", font=("Consolas", 11))
        self.steps_box.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        step_scroll = tk.Scrollbar(steps_frame, command=self.steps_box.yview)
        step_scroll.pack(fill=tk.Y, side=tk.RIGHT)
        self.steps_box.config(yscrollcommand=step_scroll.set)

        self.summary_box = tk.Text(summary_frame, wrap="word", font=("Arial", 11))
        self.summary_box.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        summary_scroll = tk.Scrollbar(summary_frame, command=self.summary_box.yview)
        summary_scroll.pack(fill=tk.Y, side=tk.RIGHT)
        self.summary_box.config(yscrollcommand=summary_scroll.set)

        self.update_template()

    def update_template(self, _event=None):
        algo = self.algorithm_var.get()
        if algo == "Binary Search":
            self.array_entry.delete(0, tk.END)
            self.array_entry.insert(0, "2, 5, 9, 14, 21, 34, 55")
            self.target_entry.delete(0, tk.END)
            self.target_entry.insert(0, "21")
        elif algo == "Merge Sort":
            self.array_entry.delete(0, tk.END)
            self.array_entry.insert(0, "38, 27, 43, 3, 9, 82, 10")
            self.target_entry.delete(0, tk.END)
        else:
            self.array_entry.delete(0, tk.END)
            self.array_entry.insert(0, "10, 7, 8, 9, 1, 5")
            self.target_entry.delete(0, tk.END)

        self.steps_box.delete("1.0", tk.END)
        self.summary_box.delete("1.0", tk.END)

    def load_example(self):
        self.update_template()

    def parse_array(self):
        raw = self.array_entry.get().strip()
        if not raw:
            raise ValueError("Please provide at least one number in the array field.")

        parts = [part.strip() for part in raw.split(",") if part.strip()]
        if not parts:
            raise ValueError("Array parsing failed. Use comma-separated integers.")

        try:
            return [int(value) for value in parts]
        except ValueError as error:
            raise ValueError("Array contains a non-integer value.") from error

    def run_trainer(self):
        try:
            numbers = self.parse_array()
        except ValueError as error:
            messagebox.showerror("Input Error", str(error))
            return

        algo = self.algorithm_var.get()
        self.steps_box.delete("1.0", tk.END)
        self.summary_box.delete("1.0", tk.END)

        if algo == "Binary Search":
            target_text = self.target_entry.get().strip()
            if not target_text:
                messagebox.showerror("Input Error", "Please provide a target value for Binary Search.")
                return
            try:
                target = int(target_text)
            except ValueError:
                messagebox.showerror("Input Error", "Target must be an integer.")
                return

            if numbers != sorted(numbers):
                messagebox.showwarning(
                    "Array Sorted Automatically",
                    "Binary Search requires sorted data. The array will be sorted first.",
                )
                numbers = sorted(numbers)

            trace, summary = self.binary_search_trace(numbers, target)
        elif algo == "Merge Sort":
            trace, summary = self.merge_sort_trace(numbers)
        else:
            trace, summary = self.quick_sort_trace(numbers)

        self.steps_box.insert(tk.END, "\n".join(trace))
        self.summary_box.insert(tk.END, summary)

    def binary_search_trace(self, arr, target):
        trace = ["BINARY SEARCH TRACE", f"Array: {arr}", f"Target: {target}", ""]
        low, high = 0, len(arr) - 1
        step = 1

        while low <= high:
            mid = (low + high) // 2
            trace.append(
                f"Step {step}: low={low}, high={high}, mid={mid}, arr[mid]={arr[mid]}"
            )
            if arr[mid] == target:
                trace.append(f"Found target {target} at index {mid}.")
                break
            if arr[mid] < target:
                trace.append(f"{arr[mid]} < {target}, so search right half.")
                low = mid + 1
            else:
                trace.append(f"{arr[mid]} > {target}, so search left half.")
                high = mid - 1
            trace.append("")
            step += 1
        else:
            trace.append(f"Target {target} not found.")

        summary = (
            "Binary Search Summary\n"
            "- Strategy: Repeatedly cut the search interval in half.\n"
            "- Requirement: Input must be sorted.\n"
            "- Time Complexity: O(log n).\n"
            "- Space Complexity: O(1) for iterative version.\n"
            "- Typical use: Fast lookups in sorted lists."
        )
        return trace, summary

    def merge_sort_trace(self, arr):
        trace = ["MERGE SORT TRACE", f"Original: {arr}", ""]

        def merge_sort(items, depth=0):
            indent = "  " * depth
            trace.append(f"{indent}Split: {items}")
            if len(items) <= 1:
                trace.append(f"{indent}Base case reached: {items}")
                return items

            mid = len(items) // 2
            left = merge_sort(items[:mid], depth + 1)
            right = merge_sort(items[mid:], depth + 1)

            merged = []
            i = j = 0
            while i < len(left) and j < len(right):
                if left[i] <= right[j]:
                    merged.append(left[i])
                    i += 1
                else:
                    merged.append(right[j])
                    j += 1

            merged.extend(left[i:])
            merged.extend(right[j:])
            trace.append(f"{indent}Merge {left} and {right} -> {merged}")
            return merged

        result = merge_sort(arr)
        trace.extend(["", f"Sorted Result: {result}"])

        summary = (
            "Merge Sort Summary\n"
            "- Strategy: Divide array into halves, sort each half recursively, then merge.\n"
            "- Time Complexity: O(n log n) in all cases.\n"
            "- Space Complexity: O(n) additional memory.\n"
            "- Strength: Stable and predictable performance."
        )
        return trace, summary

    def quick_sort_trace(self, arr):
        trace = ["QUICK SORT TRACE", f"Original: {arr}", ""]

        def quick_sort(items, depth=0):
            indent = "  " * depth
            if len(items) <= 1:
                trace.append(f"{indent}Base case: {items}")
                return items

            pivot = items[-1]
            left = [x for x in items[:-1] if x <= pivot]
            right = [x for x in items[:-1] if x > pivot]
            trace.append(
                f"{indent}Pivot={pivot}, Left={left}, Right={right}, Recurse on both sides"
            )

            return quick_sort(left, depth + 1) + [pivot] + quick_sort(right, depth + 1)

        result = quick_sort(arr)
        trace.extend(["", f"Sorted Result: {result}"])

        summary = (
            "Quick Sort Summary\n"
            "- Strategy: Pick a pivot and partition into smaller and larger elements.\n"
            "- Average Time Complexity: O(n log n).\n"
            "- Worst-case Time Complexity: O(n^2), often due to bad pivot choices.\n"
            "- Space Complexity: O(log n) average recursion stack.\n"
            "- Strength: Typically very fast in practice."
        )
        return trace, summary


if __name__ == "__main__":
    root = tk.Tk()
    app = DivideAndConquerTrainer(root)
    root.mainloop()
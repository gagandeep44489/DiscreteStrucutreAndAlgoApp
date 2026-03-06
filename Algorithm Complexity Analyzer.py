import math
import tkinter as tk
from tkinter import ttk, messagebox


COMPLEXITY_FUNCTIONS = {
    "O(1)": lambda n: 1,
    "O(log n)": lambda n: math.log2(max(2, n)),
    "O(n)": lambda n: n,
    "O(n log n)": lambda n: n * math.log2(max(2, n)),
    "O(n²)": lambda n: n**2,
    "O(n³)": lambda n: n**3,
    "O(2ⁿ)": lambda n: 2**n,
}


ALGORITHMS = {
    "Binary Search": "O(log n)",
    "Linear Search": "O(n)",
    "Merge Sort": "O(n log n)",
    "Quick Sort (average)": "O(n log n)",
    "Bubble Sort": "O(n²)",
    "Floyd-Warshall": "O(n³)",
    "Tower of Hanoi": "O(2ⁿ)",
    "Hash Table Lookup (average)": "O(1)",
}


class ComplexityAnalyzerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Algorithm Complexity Analyzer")
        self.geometry("980x650")
        self.minsize(900, 600)

        self.algorithm_var = tk.StringVar(value="Binary Search")
        self.custom_name_var = tk.StringVar()
        self.complexity_var = tk.StringVar(value="O(n)")
        self.sizes_var = tk.StringVar(value="10, 100, 1000, 5000")

        self.plotted_data = []

        self._build_ui()

    def _build_ui(self) -> None:
        container = ttk.Frame(self, padding=16)
        container.pack(fill="both", expand=True)

        title = ttk.Label(
            container,
            text="Algorithm Complexity Analyzer",
            font=("Segoe UI", 18, "bold"),
        )
        title.pack(anchor="w")

        subtitle = ttk.Label(
            container,
            text="Compare asymptotic growth by plotting operation estimates across input sizes.",
            foreground="#4b5563",
        )
        subtitle.pack(anchor="w", pady=(0, 12))

        controls_frame = ttk.LabelFrame(container, text="Inputs", padding=12)
        controls_frame.pack(fill="x", pady=(0, 12))

        ttk.Label(controls_frame, text="Preset Algorithm:").grid(row=0, column=0, sticky="w")
        algo_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.algorithm_var,
            values=list(ALGORITHMS.keys()),
            state="readonly",
            width=30,
        )
        algo_combo.grid(row=0, column=1, sticky="ew", padx=8)

        ttk.Button(
            controls_frame,
            text="Add Preset",
            command=self.add_preset_algorithm,
        ).grid(row=0, column=2, padx=(4, 0))

        ttk.Separator(controls_frame, orient="horizontal").grid(
            row=1, column=0, columnspan=3, sticky="ew", pady=10
        )

        ttk.Label(controls_frame, text="Custom Algorithm Name:").grid(row=2, column=0, sticky="w")
        ttk.Entry(controls_frame, textvariable=self.custom_name_var).grid(
            row=2, column=1, sticky="ew", padx=8
        )

        ttk.Label(controls_frame, text="Complexity:").grid(row=3, column=0, sticky="w", pady=(8, 0))
        ttk.Combobox(
            controls_frame,
            textvariable=self.complexity_var,
            values=list(COMPLEXITY_FUNCTIONS.keys()),
            state="readonly",
            width=20,
        ).grid(row=3, column=1, sticky="w", padx=8, pady=(8, 0))

        ttk.Button(
            controls_frame,
            text="Add Custom",
            command=self.add_custom_algorithm,
        ).grid(row=3, column=2, padx=(4, 0), pady=(8, 0))

        ttk.Label(controls_frame, text="Input Sizes (comma-separated):").grid(
            row=4, column=0, sticky="w", pady=(10, 0)
        )
        ttk.Entry(controls_frame, textvariable=self.sizes_var).grid(
            row=4, column=1, columnspan=2, sticky="ew", padx=8, pady=(10, 0)
        )

        controls_frame.columnconfigure(1, weight=1)

        content = ttk.Frame(container)
        content.pack(fill="both", expand=True)

        list_frame = ttk.LabelFrame(content, text="Selected Algorithms", padding=10)
        list_frame.pack(side="left", fill="both", expand=False, padx=(0, 8))

        self.selected_listbox = tk.Listbox(list_frame, height=18, width=38)
        self.selected_listbox.pack(fill="both", expand=True)

        actions = ttk.Frame(list_frame)
        actions.pack(fill="x", pady=(10, 0))

        ttk.Button(actions, text="Remove Selected", command=self.remove_selected).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(actions, text="Clear All", command=self.clear_all).pack(side="left")

        chart_frame = ttk.LabelFrame(content, text="Growth Chart", padding=10)
        chart_frame.pack(side="left", fill="both", expand=True)

        self.canvas = tk.Canvas(chart_frame, bg="white", highlightthickness=1, highlightbackground="#d1d5db")
        self.canvas.pack(fill="both", expand=True)

        bottom_actions = ttk.Frame(container)
        bottom_actions.pack(fill="x", pady=(12, 0))

        ttk.Button(bottom_actions, text="Analyze", command=self.analyze).pack(side="left")
        ttk.Button(bottom_actions, text="Export Values", command=self.export_report).pack(side="left", padx=8)

        self.output_text = tk.Text(container, height=8, wrap="word")
        self.output_text.pack(fill="x", pady=(12, 0))
        self.output_text.configure(state="disabled")

        self.bind("<Configure>", lambda _event: self.redraw_chart())

    def add_preset_algorithm(self) -> None:
        name = self.algorithm_var.get().strip()
        complexity = ALGORITHMS.get(name)
        if complexity:
            self.selected_listbox.insert("end", f"{name} | {complexity}")

    def add_custom_algorithm(self) -> None:
        name = self.custom_name_var.get().strip()
        complexity = self.complexity_var.get().strip()

        if not name:
            messagebox.showerror("Missing Name", "Please provide a custom algorithm name.")
            return

        self.selected_listbox.insert("end", f"{name} | {complexity}")
        self.custom_name_var.set("")

    def remove_selected(self) -> None:
        selected = self.selected_listbox.curselection()
        for index in reversed(selected):
            self.selected_listbox.delete(index)
        self.analyze()

    def clear_all(self) -> None:
        self.selected_listbox.delete(0, "end")
        self.plotted_data = []
        self._set_output("")
        self.redraw_chart()

    def parse_input_sizes(self):
        raw = self.sizes_var.get().strip()
        if not raw:
            raise ValueError("Input sizes cannot be empty.")

        sizes = []
        for token in raw.split(","):
            token = token.strip()
            if not token:
                continue
            n = int(token)
            if n <= 0:
                raise ValueError("All input sizes must be positive integers.")
            sizes.append(n)

        if not sizes:
            raise ValueError("Please provide at least one valid input size.")

        return sorted(set(sizes))

    def analyze(self) -> None:
        try:
            sizes = self.parse_input_sizes()
        except ValueError as exc:
            messagebox.showerror("Invalid Input Sizes", str(exc))
            return

        entries = self.selected_listbox.get(0, "end")
        if not entries:
            messagebox.showinfo("No Algorithms", "Add at least one algorithm to analyze.")
            return

        data = []
        lines = ["Estimated operation counts:\n"]

        for entry in entries:
            name, complexity = [part.strip() for part in entry.split("|", maxsplit=1)]
            fn = COMPLEXITY_FUNCTIONS[complexity]
            values = [fn(n) for n in sizes]
            data.append((name, complexity, sizes, values))

            lines.append(f"{name} ({complexity})")
            for n, value in zip(sizes, values):
                lines.append(f"  n={n:<6} -> {value:.2f}")
            lines.append("")

        self.plotted_data = data
        self._set_output("\n".join(lines).strip())
        self.redraw_chart()

    def redraw_chart(self) -> None:
        self.canvas.delete("all")
        if not self.plotted_data:
            self.canvas.create_text(
                self.canvas.winfo_width() // 2,
                self.canvas.winfo_height() // 2,
                text="Run Analyze to draw complexity curves.",
                fill="#6b7280",
                font=("Segoe UI", 11),
            )
            return

        width = max(100, self.canvas.winfo_width())
        height = max(100, self.canvas.winfo_height())

        left, right, top, bottom = 55, 25, 25, 45
        plot_w = width - left - right
        plot_h = height - top - bottom

        all_sizes = sorted({n for _, _, sizes, _ in self.plotted_data for n in sizes})
        all_values = [v for _, _, _, vals in self.plotted_data for v in vals]

        min_x, max_x = min(all_sizes), max(all_sizes)
        min_y, max_y = 0, max(all_values)
        if max_y == 0:
            max_y = 1

        colors = ["#2563eb", "#dc2626", "#16a34a", "#9333ea", "#ea580c", "#0f766e", "#db2777"]

        self.canvas.create_line(left, top, left, height - bottom, fill="#111827", width=1)
        self.canvas.create_line(left, height - bottom, width - right, height - bottom, fill="#111827", width=1)

        for i in range(6):
            y_value = min_y + (max_y - min_y) * (i / 5)
            y = height - bottom - (plot_h * i / 5)
            self.canvas.create_line(left, y, width - right, y, fill="#e5e7eb")
            self.canvas.create_text(left - 8, y, text=f"{y_value:.0f}", anchor="e", font=("Segoe UI", 8))

        for n in all_sizes:
            x = left + self._scale(n, min_x, max_x, plot_w)
            self.canvas.create_line(x, top, x, height - bottom, fill="#f3f4f6")
            self.canvas.create_text(x, height - bottom + 14, text=str(n), font=("Segoe UI", 8))

        for idx, (name, complexity, sizes, values) in enumerate(self.plotted_data):
            color = colors[idx % len(colors)]
            points = []
            for n, value in zip(sizes, values):
                x = left + self._scale(n, min_x, max_x, plot_w)
                y = height - bottom - self._scale(value, min_y, max_y, plot_h)
                points.extend((x, y))
                self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill=color, outline=color)

            if len(points) >= 4:
                self.canvas.create_line(*points, fill=color, width=2, smooth=True)

            legend_y = top + idx * 18
            self.canvas.create_rectangle(width - right - 190, legend_y - 6, width - right - 178, legend_y + 6, fill=color, outline=color)
            self.canvas.create_text(
                width - right - 172,
                legend_y,
                text=f"{name} ({complexity})",
                anchor="w",
                font=("Segoe UI", 9),
            )

        self.canvas.create_text(width // 2, height - 14, text="Input Size (n)", font=("Segoe UI", 9, "bold"))
        self.canvas.create_text(14, height // 2, text="Operations", angle=90, font=("Segoe UI", 9, "bold"))

    @staticmethod
    def _scale(value, minimum, maximum, span):
        if maximum == minimum:
            return span / 2
        return (value - minimum) * span / (maximum - minimum)

    def export_report(self) -> None:
        if not self.plotted_data:
            messagebox.showinfo("No Data", "Run analysis before exporting.")
            return

        report_lines = ["Algorithm Complexity Analyzer Report", "=" * 38, ""]
        for name, complexity, sizes, values in self.plotted_data:
            report_lines.append(f"{name} ({complexity})")
            for n, value in zip(sizes, values):
                report_lines.append(f"  n={n}: {value:.2f}")
            report_lines.append("")

        report_text = "\n".join(report_lines).strip() + "\n"

        try:
            with open("complexity_report.txt", "w", encoding="utf-8") as report_file:
                report_file.write(report_text)
            messagebox.showinfo("Exported", "Report saved as complexity_report.txt")
        except OSError as exc:
            messagebox.showerror("Export Failed", str(exc))

    def _set_output(self, text: str) -> None:
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", text)
        self.output_text.configure(state="disabled")


if __name__ == "__main__":
    app = ComplexityAnalyzerApp()
    app.mainloop()
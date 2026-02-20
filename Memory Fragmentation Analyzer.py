import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt

class MemoryFragmentationAnalyzer:

    def __init__(self, root):
        self.root = root
        self.root.title("Memory Fragmentation Analyzer")

        tk.Label(root, text="Enter Memory Blocks (comma separated sizes):").pack()
        self.blocks_entry = tk.Entry(root, width=50)
        self.blocks_entry.pack()

        tk.Label(root, text="Enter Process Sizes (comma separated):").pack()
        self.process_entry = tk.Entry(root, width=50)
        self.process_entry.pack()

        tk.Label(root, text="Allocation Strategy:").pack()
        self.strategy_var = tk.StringVar(value="First Fit")
        tk.OptionMenu(root, self.strategy_var, 
                      "First Fit", "Best Fit", "Worst Fit").pack()

        tk.Button(root, text="Analyze", command=self.analyze).pack(pady=10)

    def analyze(self):
        try:
            blocks = list(map(int, self.blocks_entry.get().split(",")))
            processes = list(map(int, self.process_entry.get().split(",")))
            strategy = self.strategy_var.get()

            allocation = [-1] * len(processes)
            remaining_blocks = blocks.copy()

            for i, process in enumerate(processes):
                index = -1

                if strategy == "First Fit":
                    for j in range(len(remaining_blocks)):
                        if remaining_blocks[j] >= process:
                            index = j
                            break

                elif strategy == "Best Fit":
                    best_size = float('inf')
                    for j in range(len(remaining_blocks)):
                        if remaining_blocks[j] >= process and remaining_blocks[j] < best_size:
                            best_size = remaining_blocks[j]
                            index = j

                elif strategy == "Worst Fit":
                    worst_size = -1
                    for j in range(len(remaining_blocks)):
                        if remaining_blocks[j] >= process and remaining_blocks[j] > worst_size:
                            worst_size = remaining_blocks[j]
                            index = j

                if index != -1:
                    allocation[i] = index
                    remaining_blocks[index] -= process

            internal_frag = sum(
                remaining_blocks[i] for i in range(len(blocks))
            )

            total_memory = sum(blocks)
            used_memory = sum(processes[i] for i in range(len(processes)) if allocation[i] != -1)
            utilization = (used_memory / total_memory) * 100

            result = f"Strategy: {strategy}\n"
            result += f"Total Memory: {total_memory}\n"
            result += f"Used Memory: {used_memory}\n"
            result += f"Memory Utilization: {utilization:.2f}%\n"
            result += f"Internal Fragmentation: {internal_frag}"

            messagebox.showinfo("Analysis Result", result)

            self.plot_memory(blocks, remaining_blocks)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def plot_memory(self, original, remaining):
        plt.figure()
        plt.bar(range(len(original)), original, label="Original")
        plt.bar(range(len(remaining)), remaining, bottom=0, alpha=0.6, label="Remaining")
        plt.title("Memory Blocks Visualization")
        plt.xlabel("Block Index")
        plt.ylabel("Memory Size")
        plt.legend()
        plt.show()


if __name__ == "__main__":
    root = tk.Tk()
    app = MemoryFragmentationAnalyzer(root)
    root.mainloop()
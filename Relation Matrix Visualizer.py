import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt


class RelationMatrixApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Relation Matrix Visualizer")
        self.root.geometry("550x420")
        self.root.resizable(False, False)

        tk.Label(root, text="Relation Matrix Visualizer",
                 font=("Arial", 16, "bold")).pack(pady=10)

        tk.Label(root, text="Set A (comma-separated):").pack()
        self.set_a_entry = tk.Entry(root, width=50)
        self.set_a_entry.pack(pady=5)

        tk.Label(root, text="Set B (comma-separated):").pack()
        self.set_b_entry = tk.Entry(root, width=50)
        self.set_b_entry.pack(pady=5)

        tk.Label(
            root,
            text="Relation pairs (one per line, format: a,1)"
        ).pack()

        self.relation_text = tk.Text(root, height=8, width=50)
        self.relation_text.pack(pady=5)

        tk.Button(
            root,
            text="Visualize Relation Matrix",
            font=("Arial", 11, "bold"),
            command=self.visualize_matrix
        ).pack(pady=10)

    def visualize_matrix(self):
        set_a = [x.strip() for x in self.set_a_entry.get().split(",") if x.strip()]
        set_b = [x.strip() for x in self.set_b_entry.get().split(",") if x.strip()]

        if not set_a or not set_b:
            messagebox.showerror("Error", "Both sets must be provided.")
            return

        a_index = {v: i for i, v in enumerate(set_a)}
        b_index = {v: i for i, v in enumerate(set_b)}

        matrix = np.zeros((len(set_a), len(set_b)), dtype=int)

        relations = self.relation_text.get("1.0", tk.END).strip().splitlines()

        for r in relations:
            try:
                a, b = [x.strip() for x in r.split(",")]
                if a in a_index and b in b_index:
                    matrix[a_index[a]][b_index[b]] = 1
                else:
                    raise ValueError
            except:
                messagebox.showerror(
                    "Input Error",
                    f"Invalid relation: {r}"
                )
                return

        self.plot_matrix(matrix, set_a, set_b)

    def plot_matrix(self, matrix, set_a, set_b):
        plt.figure(figsize=(6, 4))
        plt.imshow(matrix, cmap="Blues")

        plt.xticks(range(len(set_b)), set_b)
        plt.yticks(range(len(set_a)), set_a)

        for i in range(len(set_a)):
            for j in range(len(set_b)):
                plt.text(j, i, matrix[i, j],
                         ha="center", va="center")

        plt.title("Relation Matrix")
        plt.xlabel("Set B")
        plt.ylabel("Set A")
        plt.colorbar(label="Relation (0/1)")
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    root = tk.Tk()
    app = RelationMatrixApp(root)
    root.mainloop()

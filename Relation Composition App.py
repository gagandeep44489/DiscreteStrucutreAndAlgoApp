import tkinter as tk
from tkinter import messagebox

class RelationCompositionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Relation Composition App")
        self.root.geometry("700x500")

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Enter Relation R (format: a,b; b,c; c,d)").pack(pady=5)
        self.relation_r_entry = tk.Entry(self.root, width=80)
        self.relation_r_entry.pack(pady=5)

        tk.Label(self.root, text="Enter Relation S (format: b,e; c,f; d,g)").pack(pady=5)
        self.relation_s_entry = tk.Entry(self.root, width=80)
        self.relation_s_entry.pack(pady=5)

        tk.Button(self.root, text="Compute R ∘ S", command=self.compute_composition).pack(pady=10)
        tk.Button(self.root, text="Clear", command=self.clear_all).pack(pady=5)

        self.result_text = tk.Text(self.root, height=15, width=80)
        self.result_text.pack(pady=10)

    def parse_relation(self, input_text):
        pairs = input_text.split(";")
        relation = []
        for pair in pairs:
            pair = pair.strip()
            if pair:
                elements = pair.split(",")
                if len(elements) != 2:
                    raise ValueError("Invalid pair format.")
                relation.append((elements[0].strip(), elements[1].strip()))
        return relation

    def compute_composition(self):
        try:
            R_input = self.relation_r_entry.get()
            S_input = self.relation_s_entry.get()

            R = self.parse_relation(R_input)
            S = self.parse_relation(S_input)

            composition = []

            for (x, y) in R:
                for (a, z) in S:
                    if y == a:
                        composition.append((x, z))

            self.result_text.delete(1.0, tk.END)

            if composition:
                result_str = "R ∘ S = { " + ", ".join([f"({x},{z})" for x, z in composition]) + " }"
            else:
                result_str = "R ∘ S = ∅ (Empty Relation)"

            self.result_text.insert(tk.END, result_str)

        except Exception as e:
            messagebox.showerror("Input Error", "Please enter relations in correct format.")

    def clear_all(self):
        self.relation_r_entry.delete(0, tk.END)
        self.relation_s_entry.delete(0, tk.END)
        self.result_text.delete(1.0, tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = RelationCompositionApp(root)
    root.mainloop()
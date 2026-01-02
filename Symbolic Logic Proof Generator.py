import tkinter as tk
from tkinter import messagebox

class LogicProofGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Symbolic Logic Proof Generator")
        self.root.geometry("600x500")
        self.create_widgets()

    def create_widgets(self):
        title = tk.Label(
            self.root,
            text="Symbolic Logic Proof Generator",
            font=("Arial", 14, "bold")
        )
        title.pack(pady=10)

        tk.Label(self.root, text="Enter Premises (one per line):").pack()
        self.premises_text = tk.Text(self.root, height=8)
        self.premises_text.pack(fill="x", padx=10, pady=5)

        tk.Label(self.root, text="Enter Conclusion:").pack()
        self.conclusion_entry = tk.Entry(self.root)
        self.conclusion_entry.pack(fill="x", padx=10, pady=5)

        btn = tk.Button(
            self.root, text="Generate Proof",
            command=self.generate_proof
        )
        btn.pack(pady=10)

        tk.Label(self.root, text="Generated Proof:").pack()
        self.output_text = tk.Text(self.root, height=12)
        self.output_text.pack(fill="both", padx=10, pady=5)

    def generate_proof(self):
        self.output_text.delete("1.0", tk.END)

        premises = [
            p.strip() for p in self.premises_text.get("1.0", tk.END).splitlines()
            if p.strip()
        ]
        conclusion = self.conclusion_entry.get().strip()

        if not premises or not conclusion:
            messagebox.showerror("Error", "Please enter premises and conclusion.")
            return

        proof = []
        known = set()

        for i, p in enumerate(premises, start=1):
            proof.append(f"Step {i}: {p}   (Premise)")
            known.add(p)

        step = len(proof) + 1

        # Modus Ponens
        for stmt in known:
            if "->" in stmt:
                A, B = map(str.strip, stmt.split("->"))
                if A in known and B == conclusion:
                    proof.append(
                        f"Step {step}: {B}   (Modus Ponens from {A} -> {B})"
                    )
                    self.display_proof(proof)
                    return

        proof.append("No valid proof found with current rules.")
        self.display_proof(proof)

    def display_proof(self, proof_steps):
        for line in proof_steps:
            self.output_text.insert(tk.END, line + "\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = LogicProofGenerator(root)
    root.mainloop()

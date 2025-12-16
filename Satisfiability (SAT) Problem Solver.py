import tkinter as tk
from tkinter import filedialog, messagebox
from pysat.solvers import Solver

class SATSolverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Satisfiability (SAT) Problem Solver")
        self.root.geometry("800x500")

        # Controls frame
        control_frame = tk.Frame(root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        load_btn = tk.Button(control_frame, text="Load CNF File", command=self.load_cnf)
        load_btn.pack(side=tk.LEFT, padx=5)

        solve_btn = tk.Button(control_frame, text="Solve SAT", command=self.solve_sat)
        solve_btn.pack(side=tk.LEFT, padx=10)

        clear_btn = tk.Button(control_frame, text="Clear", command=self.clear_output)
        clear_btn.pack(side=tk.LEFT, padx=10)

        # Output frame
        self.output_text = tk.Text(root, wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.cnf_clauses = None

    def load_cnf(self):
        file_path = filedialog.askopenfilename(filetypes=[("CNF Files", "*.cnf"), ("Text Files", "*.txt")])
        if not file_path:
            return
        try:
            self.cnf_clauses = []
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line == '' or line.startswith('c') or line.startswith('p'):
                        continue
                    clause = [int(x) for x in line.split() if x != '0']
                    self.cnf_clauses.append(clause)
            self.output_text.insert(tk.END, f"Loaded CNF with {len(self.cnf_clauses)} clauses\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CNF file:\n{e}")

    def solve_sat(self):
        if not self.cnf_clauses:
            messagebox.showwarning("Warning", "Load a CNF file first")
            return
        try:
            with Solver(name='g3') as solver:
                for clause in self.cnf_clauses:
                    solver.add_clause(clause)
                sat_result = solver.solve()
                if sat_result:
                    model = solver.get_model()
                    self.output_text.insert(tk.END, "SATISFIABLE\n")
                    self.output_text.insert(tk.END, f"Model: {model}\n")
                else:
                    self.output_text.insert(tk.END, "UNSATISFIABLE\n")
        except Exception as e:
            messagebox.showerror("Error", f"Error solving SAT:\n{e}")

    def clear_output(self):
        self.output_text.delete('1.0', tk.END)
        self.cnf_clauses = None

if __name__ == "__main__":
    root = tk.Tk()
    app = SATSolverApp(root)
    root.mainloop()
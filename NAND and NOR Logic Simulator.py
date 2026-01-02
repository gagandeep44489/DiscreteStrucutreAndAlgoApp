import tkinter as tk
from tkinter import ttk, messagebox

class LogicSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("NAND / NOR Logic Simulator")
        self.root.geometry("400x300")

        self.create_widgets()

    def create_widgets(self):
        title = tk.Label(
            self.root,
            text="NAND / NOR Logic Simulator",
            font=("Arial", 14, "bold")
        )
        title.pack(pady=10)

        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Input A").grid(row=0, column=0, padx=10)
        tk.Label(input_frame, text="Input B").grid(row=0, column=1, padx=10)

        self.a_var = tk.IntVar(value=0)
        self.b_var = tk.IntVar(value=0)

        ttk.Combobox(
            input_frame,
            textvariable=self.a_var,
            values=[0, 1],
            width=5,
            state="readonly"
        ).grid(row=1, column=0)

        ttk.Combobox(
            input_frame,
            textvariable=self.b_var,
            values=[0, 1],
            width=5,
            state="readonly"
        ).grid(row=1, column=1)

        gate_frame = tk.Frame(self.root)
        gate_frame.pack(pady=10)

        self.gate_var = tk.StringVar(value="NAND")

        ttk.Radiobutton(
            gate_frame, text="NAND Gate",
            variable=self.gate_var, value="NAND"
        ).pack(side="left", padx=10)

        ttk.Radiobutton(
            gate_frame, text="NOR Gate",
            variable=self.gate_var, value="NOR"
        ).pack(side="left", padx=10)

        simulate_btn = tk.Button(
            self.root, text="Simulate",
            command=self.simulate
        )
        simulate_btn.pack(pady=15)

        self.result_label = tk.Label(
            self.root,
            text="Output: ",
            font=("Arial", 12, "bold")
        )
        self.result_label.pack(pady=10)

    def simulate(self):
        A = self.a_var.get()
        B = self.b_var.get()
        gate = self.gate_var.get()

        if gate == "NAND":
            output = int(not (A and B))
        elif gate == "NOR":
            output = int(not (A or B))
        else:
            messagebox.showerror("Error", "Invalid Gate Selected")
            return

        self.result_label.config(
            text=f"Output ({gate}): {output}"
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = LogicSimulator(root)
    root.mainloop()

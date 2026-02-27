import tkinter as tk
from tkinter import messagebox

class RecursionTreeVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Recursion Tree Visualizer")
        self.root.geometry("1000x700")

        title = tk.Label(root, text="Recursion Tree Visualizer",
                         font=("Arial", 16, "bold"))
        title.pack(pady=10)

        control_frame = tk.Frame(root)
        control_frame.pack()

        tk.Label(control_frame, text="Enter n:").grid(row=0, column=0, padx=5)
        self.input_entry = tk.Entry(control_frame, width=10)
        self.input_entry.grid(row=0, column=1, padx=5)

        tk.Button(control_frame, text="Visualize Factorial",
                  command=self.visualize_factorial).grid(row=0, column=2, padx=5)

        tk.Button(control_frame, text="Visualize Fibonacci",
                  command=self.visualize_fibonacci).grid(row=0, column=3, padx=5)

        tk.Button(control_frame, text="Clear",
                  command=self.clear_canvas).grid(row=0, column=4, padx=5)

        self.canvas = tk.Canvas(root, bg="white", width=950, height=550)
        self.canvas.pack(pady=20)

    # -------------------------
    # Clear Canvas
    # -------------------------
    def clear_canvas(self):
        self.canvas.delete("all")

    # -------------------------
    # Factorial Tree
    # -------------------------
    def visualize_factorial(self):
        self.clear_canvas()

        try:
            n = int(self.input_entry.get())
            if n < 0:
                raise ValueError
        except:
            messagebox.showerror("Error", "Please enter a valid non-negative integer.")
            return

        self.draw_factorial(n, 500, 50, 200)

    def draw_factorial(self, n, x, y, offset):
        self.canvas.create_oval(x-25, y-20, x+25, y+20, fill="lightblue")
        self.canvas.create_text(x, y, text=f"fact({n})")

        if n <= 1:
            return

        child_x = x
        child_y = y + 100

        self.canvas.create_line(x, y+20, child_x, child_y-20)

        self.draw_factorial(n-1, child_x, child_y, offset // 2)

    # -------------------------
    # Fibonacci Tree
    # -------------------------
    def visualize_fibonacci(self):
        self.clear_canvas()

        try:
            n = int(self.input_entry.get())
            if n < 0 or n > 8:   # limit to avoid too large tree
                raise ValueError
        except:
            messagebox.showerror("Error", "Enter integer between 0 and 8 (Fibonacci grows fast).")
            return

        self.draw_fibonacci(n, 500, 50, 250)

    def draw_fibonacci(self, n, x, y, offset):
        self.canvas.create_oval(x-25, y-20, x+25, y+20, fill="lightgreen")
        self.canvas.create_text(x, y, text=f"fib({n})")

        if n <= 1:
            return

        left_x = x - offset
        right_x = x + offset
        child_y = y + 100

        self.canvas.create_line(x, y+20, left_x, child_y-20)
        self.canvas.create_line(x, y+20, right_x, child_y-20)

        self.draw_fibonacci(n-1, left_x, child_y, offset // 2)
        self.draw_fibonacci(n-2, right_x, child_y, offset // 2)


# -------------------------
# Run App
# -------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = RecursionTreeVisualizer(root)
    root.mainloop()
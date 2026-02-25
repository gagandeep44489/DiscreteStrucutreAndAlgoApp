import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib_venn import venn2

def parse_set(input_text):
    try:
        return set(map(int, input_text.split(',')))
    except:
        messagebox.showerror("Input Error", "Enter numbers separated by commas (e.g., 1,2,3)")
        return None

def show_union():
    A = parse_set(entry_A.get())
    B = parse_set(entry_B.get())
    if A is None or B is None:
        return

    result = A.union(B)
    result_label.config(text=f"A ∪ B = {result}")
    draw_venn(A, B, "Union (A ∪ B)")

def show_intersection():
    A = parse_set(entry_A.get())
    B = parse_set(entry_B.get())
    if A is None or B is None:
        return

    result = A.intersection(B)
    result_label.config(text=f"A ∩ B = {result}")
    draw_venn(A, B, "Intersection (A ∩ B)")

def show_difference():
    A = parse_set(entry_A.get())
    B = parse_set(entry_B.get())
    if A is None or B is None:
        return

    result = A.difference(B)
    result_label.config(text=f"A − B = {result}")
    draw_venn(A, B, "Difference (A − B)")

def show_demorgan():
    A = parse_set(entry_A.get())
    B = parse_set(entry_B.get())
    if A is None or B is None:
        return

    universal = set(range(1, 21))
    left = universal - (A.union(B))
    right = (universal - A).intersection(universal - B)

    result_label.config(text=f"De Morgan Verified: {left == right}")
    draw_venn(A, B, "De Morgan's Law")

def draw_venn(A, B, title):
    for widget in frame_graph.winfo_children():
        widget.destroy()

    fig = plt.Figure(figsize=(4,4))
    ax = fig.add_subplot(111)
    venn2([A, B], set_labels=('A', 'B'), ax=ax)
    ax.set_title(title)

    canvas = FigureCanvasTkAgg(fig, master=frame_graph)
    canvas.draw()
    canvas.get_tk_widget().pack()

# GUI Setup
root = tk.Tk()
root.title("Set Theory Theorem Visual Proof Generator")
root.geometry("600x650")
root.resizable(False, False)

tk.Label(root, text="Set Theory Theorem Visual Proof Generator",
         font=("Arial", 14, "bold")).pack(pady=10)

tk.Label(root, text="Enter Set A (e.g., 1,2,3)").pack()
entry_A = tk.Entry(root, width=40)
entry_A.pack(pady=5)

tk.Label(root, text="Enter Set B (e.g., 2,3,4)").pack()
entry_B = tk.Entry(root, width=40)
entry_B.pack(pady=5)

tk.Button(root, text="Union (A ∪ B)", command=show_union, bg="blue", fg="white").pack(pady=5)
tk.Button(root, text="Intersection (A ∩ B)", command=show_intersection, bg="green", fg="white").pack(pady=5)
tk.Button(root, text="Difference (A − B)", command=show_difference, bg="orange", fg="white").pack(pady=5)
tk.Button(root, text="Verify De Morgan's Law", command=show_demorgan, bg="purple", fg="white").pack(pady=5)

result_label = tk.Label(root, text="", font=("Arial", 12, "bold"))
result_label.pack(pady=10)

frame_graph = tk.Frame(root)
frame_graph.pack(pady=10)

root.mainloop()
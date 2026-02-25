import tkinter as tk
import random
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# ---------- Sorting Algorithms ----------

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
            yield arr

def merge_sort(arr):
    if len(arr) <= 1:
        return arr

    mid = len(arr)//2
    left = arr[:mid]
    right = arr[mid:]

    yield from merge_sort(left)
    yield from merge_sort(right)

    i = j = k = 0

    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            arr[k] = left[i]
            i += 1
        else:
            arr[k] = right[j]
            j += 1
        k += 1
        yield arr

    while i < len(left):
        arr[k] = left[i]
        i += 1
        k += 1
        yield arr

    while j < len(right):
        arr[k] = right[j]
        j += 1
        k += 1
        yield arr

def quick_sort(arr, low, high):
    if low < high:
        pivot = partition(arr, low, high)
        yield arr
        yield from quick_sort(arr, low, pivot-1)
        yield from quick_sort(arr, pivot+1, high)

def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] < pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i+1], arr[high] = arr[high], arr[i+1]
    return i+1

# ---------- GUI & Visualization ----------

def generate_array():
    global data
    data = [random.randint(10, 100) for _ in range(30)]
    draw_data(data)

def draw_data(data):
    ax.clear()
    ax.bar(range(len(data)), data)
    canvas.draw()

def start_sort():
    algo = algorithm_menu.get()

    if algo == "Bubble Sort":
        generator = bubble_sort(data)
    elif algo == "Merge Sort":
        generator = merge_sort(data)
    elif algo == "Quick Sort":
        generator = quick_sort(data, 0, len(data)-1)
    else:
        return

    animate(generator)

def animate(generator):
    try:
        next(generator)
        draw_data(data)
        root.after(100, lambda: animate(generator))
    except StopIteration:
        draw_data(data)

# ---------- Main Window ----------

root = tk.Tk()
root.title("Sorting Algorithm Visualizer")
root.geometry("800x600")
root.resizable(False, False)

data = []

# Controls
frame_controls = tk.Frame(root)
frame_controls.pack(pady=10)

algorithm_menu = tk.StringVar()
algorithm_menu.set("Bubble Sort")

tk.OptionMenu(frame_controls, algorithm_menu,
              "Bubble Sort", "Merge Sort", "Quick Sort").pack(side=tk.LEFT, padx=10)

tk.Button(frame_controls, text="Generate Array",
          command=generate_array).pack(side=tk.LEFT, padx=10)

tk.Button(frame_controls, text="Start Sorting",
          command=start_sort).pack(side=tk.LEFT, padx=10)

# Graph
fig, ax = plt.subplots(figsize=(8, 4))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

root.mainloop()
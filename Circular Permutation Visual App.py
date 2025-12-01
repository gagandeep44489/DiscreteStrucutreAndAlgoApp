import tkinter as tk
from tkinter import ttk, messagebox
import itertools
import time
import threading


class CircularPermApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Circular Permutation Visualizer")
        self.root.geometry("850x600")
        self.root.resizable(False, False)

        # --- FIX: Define play delay before widgets ---
        self.play_delay_ms = 800  # default animation speed (milliseconds)

        self.is_playing = False
        self.items = []
        self.permutations = []
        self.current_index = 0

        self.create_widgets()

    # ---------------------------------------------------------
    def create_widgets(self):
        frame = tk.Frame(self.root, pady=10)
        frame.pack()

        tk.Label(frame, text="Enter items separated by commas:",
                 font=("Arial", 12)).pack()

        self.input_box = tk.Entry(frame, font=("Arial", 14), width=40)
        self.input_box.pack(pady=5)

        generate_btn = tk.Button(frame, text="Generate Circular Permutations",
                                 font=("Arial", 12, "bold"),
                                 command=self.generate_permutations)
        generate_btn.pack(pady=10)

        # Display area
        self.display = tk.Text(self.root, height=12, width=80,
                               font=("Courier", 14))
        self.display.pack(pady=10)

        # Playback controls
        controls = tk.Frame(self.root)
        controls.pack(pady=10)

        tk.Button(controls, text="⏮ Previous", width=12,
                  command=self.prev_perm).grid(row=0, column=0, padx=10)

        tk.Button(controls, text="▶ Play", width=12,
                  command=self.start_play).grid(row=0, column=1, padx=10)

        tk.Button(controls, text="⏹ Stop", width=12,
                  command=self.stop_play).grid(row=0, column=2, padx=10)

        tk.Button(controls, text="⏭ Next", width=12,
                  command=self.next_perm).grid(row=0, column=3, padx=10)

        speed_frame = tk.Frame(self.root)
        speed_frame.pack(pady=10)

        tk.Label(speed_frame, text="Speed (ms per step):",
                 font=("Arial", 12)).pack(side=tk.LEFT)

        # FIX: play_delay_ms is now defined
        self.speed_var = tk.IntVar(value=self.play_delay_ms)

        tk.Entry(speed_frame, textvariable=self.speed_var, width=7,
                 font=("Arial", 12)).pack(side=tk.LEFT, padx=5)

    # ---------------------------------------------------------
    def generate_permutations(self):
        text = self.input_box.get().strip()
        if not text:
            messagebox.showerror("Error", "Please enter some items.")
            return

        self.items = [x.strip() for x in text.split(",") if x.strip()]

        if len(self.items) < 2:
            messagebox.showerror("Error",
                                 "Enter at least 2 items for circular permutation.")
            return

        # Circular permutations: fix first element, permute others
        self.permutations = []
        base = self.items[0]
        for perm in itertools.permutations(self.items[1:]):
            self.permutations.append([base] + list(perm))

        self.current_index = 0
        self.show_current()

    # ---------------------------------------------------------
    def show_current(self):
        if not self.permutations:
            return

        self.display.delete(1.0, tk.END)

        perm = self.permutations[self.current_index]

        # Show as circular
        circ = "  →  ".join(perm)
        circ += "  → (back to start)"

        self.display.insert(tk.END, f"Permutation {self.current_index + 1} / {len(self.permutations)}\n\n")
        self.display.insert(tk.END, circ)

    # ---------------------------------------------------------
    def prev_perm(self):
        if self.permutations:
            self.current_index = (self.current_index - 1) % len(self.permutations)
            self.show_current()

    def next_perm(self):
        if self.permutations:
            self.current_index = (self.current_index + 1) % len(self.permutations)
            self.show_current()

    # ---------------------------------------------------------
    def start_play(self):
        if not self.permutations:
            return

        self.is_playing = True
        threading.Thread(target=self.autoplay, daemon=True).start()

    def stop_play(self):
        self.is_playing = False

    def autoplay(self):
        while self.is_playing:
            self.next_perm()
            time.sleep(self.speed_var.get() / 1000)

    # ---------------------------------------------------------
    def run(self):
        self.root.mainloop()


# ---------------------------------------------------------
def main():
    app = CircularPermApp()
    app.run()


if __name__ == "__main__":
    main()

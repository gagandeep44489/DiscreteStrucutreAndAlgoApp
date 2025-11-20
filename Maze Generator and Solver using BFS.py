"""
Maze Generator & Solver (BFS) - Desktop App (Tkinter)
Save as: maze_generator_solver.py
Run:      python maze_generator_solver.py

Features:
 - Random maze generation using the recursive backtracker algorithm (depth-first).
 - Maze solving using Breadth-First Search (BFS).
 - Visual, interactive Tkinter UI: draw maze, animate generation and BFS solution.
 - Controls: set rows/cols, cell size, animation speed; buttons to Generate, Solve (BFS),
   Clear solution, Toggle animation.
 - Start cell = top-left; Goal cell = bottom-right (changeable in code if needed).
 - No external dependencies (uses Python standard library + Tkinter).

Notes:
 - For best results, try modest grid sizes first (e.g., 20x30 with cell_size 20).
 - On slow machines, reduce cell size or grid dimensions.
"""

import tkinter as tk
from tkinter import ttk
import random
from collections import deque

# ---------- Maze model ----------
class Maze:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        # Each cell has walls: [top, right, bottom, left] (True = wall exists)
        self.walls = [[[True, True, True, True] for _ in range(cols)] for _ in range(rows)]
        self.visited = [[False] * cols for _ in range(rows)]

    def reset(self):
        self.walls = [[[True, True, True, True] for _ in range(self.cols)] for _ in range(self.rows)]
        self.visited = [[False] * self.cols for _ in range(self.rows)]

    def neighbors(self, r, c):
        """
        Return list of (nr, nc, direction_index) where direction_index is:
        0 = top, 1 = right, 2 = bottom, 3 = left
        """
        res = []
        if r > 0:
            res.append((r-1, c, 0))
        if c < self.cols - 1:
            res.append((r, c+1, 1))
        if r < self.rows - 1:
            res.append((r+1, c, 2))
        if c > 0:
            res.append((r, c-1, 3))
        return res

    def remove_wall(self, r, c, dir_idx):
        # Remove wall on cell (r,c) in direction dir_idx and the opposite wall on neighbor
        self.walls[r][c][dir_idx] = False
        dr = [-1, 0, 1, 0]
        dc = [0, 1, 0, -1]
        or_dir = (dir_idx + 2) % 4
        nr = r + dr[dir_idx]
        nc = c + dc[dir_idx]
        if 0 <= nr < self.rows and 0 <= nc < self.cols:
            self.walls[nr][nc][or_dir] = False


# ---------- Maze generator (recursive backtracker) ----------
def generate_maze_dfs(maze, start=(0,0), animate_callback=None, delay=0):
    """
    Generate maze using randomized DFS (recursive backtracker).
    animate_callback(cell_row, cell_col) is called when a cell is visited (for UI animation).
    If delay > 0, animate_callback should be used to slow things down.
    """
    stack = []
    r0, c0 = start
    maze.visited[r0][c0] = True
    stack.append((r0, c0))

    dr = [-1, 0, 1, 0]
    dc = [0, 1, 0, -1]

    while stack:
        r, c = stack[-1]
        if animate_callback:
            animate_callback(r, c)
            if delay:
                maze_app.root.update()
                maze_app.root.after(delay)
        # gather unvisited neighbors
        unv = []
        for i, (nr, nc, d) in enumerate( ((r-1,c,0),(r,c+1,1),(r+1,c,2),(r,c-1,3)) ):
            if 0 <= nr < maze.rows and 0 <= nc < maze.cols and not maze.visited[nr][nc]:
                unv.append((nr, nc, d))
        if unv:
            nr, nc, dir_idx = random.choice(unv)
            maze.remove_wall(r, c, dir_idx)
            maze.visited[nr][nc] = True
            stack.append((nr, nc))
        else:
            stack.pop()


# ---------- BFS solver ----------
def bfs_solve(maze, start=(0,0), goal=None, animate_step_callback=None, delay=0):
    """
    Solve the maze using BFS, returning the path as a list of (r,c) from start to goal.
    animate_step_callback(r,c) is invoked when a cell is expanded (to animate search).
    """
    if goal is None:
        goal = (maze.rows - 1, maze.cols - 1)

    sr, sc = start
    gr, gc = goal

    q = deque()
    q.append((sr, sc))
    parent = { (sr, sc): None }
    visited = set([(sr, sc)])

    drs = [-1, 0, 1, 0]
    dcs = [0, 1, 0, -1]

    while q:
        r, c = q.popleft()
        if animate_step_callback:
            animate_step_callback(r, c)
            if delay:
                maze_app.root.update()
                maze_app.root.after(delay)
        if (r, c) == (gr, gc):
            # reconstruct path
            path = []
            cur = (gr, gc)
            while cur:
                path.append(cur)
                cur = parent[cur]
            path.reverse()
            return path
        # explore neighbors that are open (no wall)
        for d in range(4):
            if not maze.walls[r][c][d]:
                nr = r + drs[d]
                nc = c + dcs[d]
                if 0 <= nr < maze.rows and 0 <= nc < maze.cols and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    parent[(nr, nc)] = (r, c)
                    q.append((nr, nc))
    return None  # no path


# ---------- Tkinter GUI ----------
class MazeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Maze Generator & Solver (BFS)")
        self.running = False

        # Default parameters
        self.rows = tk.IntVar(value=20)
        self.cols = tk.IntVar(value=30)
        self.cell_size = tk.IntVar(value=20)  # pixels per cell
        self.gen_delay = tk.IntVar(value=5)   # ms delay between generation steps (0 = no animation)
        self.solve_delay = tk.IntVar(value=10) # ms delay between BFS steps
        self.show_generation = tk.BooleanVar(value=True)
        self.show_bfs = tk.BooleanVar(value=True)

        self._build_ui()

        # Maze instance
        self.maze = None
        self.canvas_items = {}  # optional mapping for cell highlight rectangles

    def _build_ui(self):
        frm = ttk.Frame(self.root, padding=8)
        frm.grid(sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Controls frame
        ctrl = ttk.Frame(frm)
        ctrl.grid(row=0, column=0, sticky="ew")
        ctrl.columnconfigure(8, weight=1)

        ttk.Label(ctrl, text="Rows:").grid(row=0, column=0, padx=4)
        ttk.Entry(ctrl, textvariable=self.rows, width=5).grid(row=0, column=1)
        ttk.Label(ctrl, text="Cols:").grid(row=0, column=2, padx=4)
        ttk.Entry(ctrl, textvariable=self.cols, width=5).grid(row=0, column=3)
        ttk.Label(ctrl, text="Cell size:").grid(row=0, column=4, padx=4)
        ttk.Entry(ctrl, textvariable=self.cell_size, width=5).grid(row=0, column=5)

        ttk.Button(ctrl, text="Generate Maze", command=self.on_generate).grid(row=0, column=6, padx=6)
        ttk.Button(ctrl, text="Solve (BFS)", command=self.on_solve).grid(row=0, column=7, padx=6)
        ttk.Button(ctrl, text="Clear Solution", command=self.clear_solution).grid(row=0, column=8, padx=6, sticky="e")

        # Options frame
        opts = ttk.Frame(frm)
        opts.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        ttk.Label(opts, text="Generation delay (ms):").grid(row=0, column=0)
        ttk.Entry(opts, textvariable=self.gen_delay, width=6).grid(row=0, column=1, padx=(2,12))
        ttk.Checkbutton(opts, text="Animate generation", variable=self.show_generation).grid(row=0, column=2, padx=(2,10))

        ttk.Label(opts, text="BFS delay (ms):").grid(row=0, column=3)
        ttk.Entry(opts, textvariable=self.solve_delay, width=6).grid(row=0, column=4, padx=(2,12))
        ttk.Checkbutton(opts, text="Animate BFS", variable=self.show_bfs).grid(row=0, column=5, padx=(2,10))

        # Canvas area
        self.canvas = tk.Canvas(frm, bg="white")
        self.canvas.grid(row=2, column=0, sticky="nsew", pady=(8,0))
        frm.rowconfigure(2, weight=1)
        frm.columnconfigure(0, weight=1)

        # Status bar
        self.status_var = tk.StringVar(value="Ready.")
        status = ttk.Label(frm, textvariable=self.status_var, relief="sunken", anchor="w")
        status.grid(row=3, column=0, sticky="ew", pady=(6,0))

        # Bind resizing to redraw
        self.root.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        # redraw on window size change (coarse)
        # avoid too many redraws by using after_cancel pattern if necessary
        if hasattr(self, "_resize_after"):
            self.root.after_cancel(self._resize_after)
        self._resize_after = self.root.after(150, self.redraw_canvas)

    def create_maze_model(self):
        r = max(2, int(self.rows.get()))
        c = max(2, int(self.cols.get()))
        self.maze = Maze(r, c)

    def on_generate(self):
        if self.running:
            return
        try:
            self.create_maze_model()
            self.redraw_canvas()
            self.status_var.set("Generating maze...")
            self.running = True
            # run generator
            delay = int(self.gen_delay.get()) if self.show_generation.get() else 0
            generate_maze_dfs(self.maze, start=(0,0),
                              animate_callback=self._animate_generation if self.show_generation.get() else None,
                              delay=delay)
            self.running = False
            self.status_var.set("Maze generated.")
            self.redraw_canvas()
            # reset any solution overlays
            self.clear_solution(overwrite=False)
        except Exception as e:
            self.status_var.set(f"Error generating: {e}")
            self.running = False

    def _animate_generation(self, r, c):
        # Highlight current cell quickly
        cs = int(self.cell_size.get())
        x0 = c * cs
        y0 = r * cs
        x1 = x0 + cs
        y1 = y0 + cs
        # Draw a translucent rectangle highlight; remove previous after short time
        if getattr(self, "_gen_highlight", None):
            self.canvas.delete(self._gen_highlight)
        self._gen_highlight = self.canvas.create_rectangle(x0, y0, x1, y1, fill="#cfe8ff", outline="")
        # also optionally draw walls incrementally
        self._draw_cell_walls(r, c)

    def _draw_cell_walls(self, r, c):
        # Draw just the walls for the cell (helps incremental visual)
        cs = int(self.cell_size.get())
        x = c * cs
        y = r * cs
        walls = self.maze.walls[r][c]
        if walls[0]:
            self.canvas.create_line(x, y, x + cs, y)
        else:
            # erase if previously drawn line exists? we simply overdraw background
            pass
        if walls[1]:
            self.canvas.create_line(x + cs, y, x + cs, y + cs)
        if walls[2]:
            self.canvas.create_line(x, y + cs, x + cs, y + cs)
        if walls[3]:
            self.canvas.create_line(x, y, x, y + cs)

    def redraw_canvas(self):
        # Draw the full maze onto the canvas (walls)
        self.canvas.delete("all")
        if not self.maze:
            return
        cs = int(self.cell_size.get())
        width = self.maze.cols * cs
        height = self.maze.rows * cs
        # Resize canvas to fit content while staying within window size
        # but we allow scrollbars later (not implemented) — for now fit to content
        self.canvas.config(width=width, height=height, scrollregion=(0,0,width,height))
        # Draw grid background
        self.canvas.create_rectangle(0, 0, width, height, fill="white", outline="")
        # Draw walls
        for r in range(self.maze.rows):
            for c in range(self.maze.cols):
                x = c * cs
                y = r * cs
                walls = self.maze.walls[r][c]
                if walls[0]:
                    self.canvas.create_line(x, y, x + cs, y)
                if walls[1]:
                    self.canvas.create_line(x + cs, y, x + cs, y + cs)
                if walls[2]:
                    self.canvas.create_line(x, y + cs, x + cs, y + cs)
                if walls[3]:
                    self.canvas.create_line(x, y, x, y + cs)
        # mark start and goal
        self._draw_start_goal()

    def _draw_start_goal(self):
        cs = int(self.cell_size.get())
        # start (0,0) fill green
        self.canvas.create_rectangle(2, 2, cs-2, cs-2, fill="#8ef08e", outline="")
        # goal (rows-1, cols-1) fill red
        x0 = (self.maze.cols-1) * cs + 2
        y0 = (self.maze.rows-1) * cs + 2
        x1 = x0 + cs - 4
        y1 = y0 + cs - 4
        self.canvas.create_rectangle(x0, y0, x1, y1, fill="#ff9a9a", outline="")

    def on_solve(self):
        if self.running or not self.maze:
            return
        self.clear_solution()
        self.status_var.set("Solving with BFS...")
        self.running = True
        delay = int(self.solve_delay.get()) if self.show_bfs.get() else 0
        path = bfs_solve(self.maze, start=(0,0), goal=(self.maze.rows-1, self.maze.cols-1),
                         animate_step_callback=self._animate_bfs if self.show_bfs.get() else None,
                         delay=delay)
        self.running = False
        if path:
            self._draw_solution(path)
            self.status_var.set(f"Solution found: {len(path)} steps.")
        else:
            self.status_var.set("No path found.")

    def _animate_bfs(self, r, c):
        # draw visited cell with light color
        cs = int(self.cell_size.get())
        x0 = c * cs + cs * 0.15
        y0 = r * cs + cs * 0.15
        x1 = x0 + cs * 0.7
        y1 = y0 + cs * 0.7
        rect = self.canvas.create_rectangle(x0, y0, x1, y1, fill="#f0f0ff", outline="")
        # keep track to allow clearing later
        if not hasattr(self, "_bfs_vis_items"):
            self._bfs_vis_items = []
        self._bfs_vis_items.append(rect)

    def _draw_solution(self, path):
        # overlay a path line
        cs = int(self.cell_size.get())
        coords = []
        for (r, c) in path:
            x = c * cs + cs/2
            y = r * cs + cs/2
            coords.append((x, y))
        # draw polyline
        for i in range(len(coords) - 1):
            x0, y0 = coords[i]
            x1, y1 = coords[i+1]
            self.canvas.create_line(x0, y0, x1, y1, width=max(2, cs//5), fill="#2b6cff", capstyle="round", joinstyle="round")
        # mark path cells with small circles
        for (x, y) in coords:
            self.canvas.create_oval(x - cs*0.08, y - cs*0.08, x + cs*0.08, y + cs*0.08, fill="#2b6cff", outline="")

    def clear_solution(self, overwrite=True):
        # Remove BFS visualization items (but preserve walls)
        if hasattr(self, "_bfs_vis_items"):
            for it in self._bfs_vis_items:
                try:
                    self.canvas.delete(it)
                except Exception:
                    pass
            self._bfs_vis_items = []
        # If requested, redraw to clean stray highlights
        if overwrite and self.maze:
            self.redraw_canvas()
            self.status_var.set("Solution cleared.")

# ---------- Main ----------
def main():
    global maze_app
    root = tk.Tk()
    maze_app = MazeApp(root)
    # Set an initial size for a comfortable layout
    root.geometry("900x600")
    root.mainloop()

if __name__ == "__main__":
    main()

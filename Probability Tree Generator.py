"""
Probability Tree Generator (Tkinter)
- Create probability trees with custom branching per level.
- Visualize the tree on a Canvas.
- Label edges with probabilities and compute path probabilities.
- Export canvas to PostScript (which can be converted to PNG externally).

How to use:
1. Enter number of levels (depth), e.g., 3
2. Enter branching per level as comma-separated integers, e.g., "2,3,2"
   - The length should be equal to number of levels.
   - Example interpretation: Level1 has 2 branches, Level2 has 3 branches for each branch of level1, etc.
3. Enter branch labels per level (optional) as semicolon-separated groups, e.g.
   "H,T;1,2,3;X,Y" where each group corresponds to level's branch labels.
   If omitted or incomplete, labels default to "B1,B2,..."
4. Enter probabilities per level as semicolon-separated groups (same format as labels),
   e.g. "0.5,0.5;0.2,0.5,0.3;0.3,0.7"
   Probabilities in a group should sum to 1 (per parent branch). If you give one group
   it will be applied to every parent at that level.
5. Click "Generate Tree"
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math

CANVAS_WIDTH = 900
CANVAS_HEIGHT = 600
NODE_RADIUS = 18
LEVEL_GAP = 120

def parse_list_groups(text, levels, default_from_count=None):
    """
    Parse semicolon-separated groups, each group is comma-separated values.
    Returns list of groups (length == levels). If fewer groups provided, last group repeated.
    If empty, returns generated defaults using default_from_count function when provided.
    """
    if not text.strip():
        if default_from_count:
            return [default_from_count(i) for i in range(levels)]
        return [[]]*levels
    groups = [g.strip() for g in text.split(";") if g.strip() != ""]
    parsed = []
    for g in groups:
        parsed.append([s.strip() for s in g.split(",") if s.strip() != ""])
    # extend or repeat last group to reach levels
    if len(parsed) < levels:
        last = parsed[-1] if parsed else []
        while len(parsed) < levels:
            parsed.append(last)
    return parsed[:levels]

def safe_float(s, default=0.0):
    try:
        return float(s)
    except:
        return default

class TreeNode:
    def __init__(self, level, index, label=None):
        self.level = level
        self.index = index  # index within its level (0..count-1)
        self.label = label
        self.children = []  # list of (prob, label, TreeNode)
        self.x = 0
        self.y = 0

class ProbabilityTreeApp:
    def __init__(self, root):
        self.root = root
        root.title("Probability Tree Generator")
        root.geometry("1150x680")
        self.setup_ui()

    def setup_ui(self):
        control_frame = ttk.Frame(self.root, padding=8)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(control_frame, text="Levels (depth):").grid(row=0, column=0, sticky=tk.W)
        self.levels_var = tk.StringVar(value="3")
        ttk.Entry(control_frame, textvariable=self.levels_var, width=20).grid(row=0, column=1, pady=3)

        ttk.Label(control_frame, text="Branching per level:").grid(row=1, column=0, sticky=tk.W)
        self.branching_var = tk.StringVar(value="2,2,2")
        ttk.Entry(control_frame, textvariable=self.branching_var, width=30).grid(row=1, column=1, pady=3)

        ttk.Label(control_frame, text="Branch labels per level (optional):").grid(row=2, column=0, sticky=tk.W)
        ttk.Label(control_frame, text="(semicolons separate levels)").grid(row=3, column=0, columnspan=2, sticky=tk.W)
        self.labels_var = tk.StringVar(value="H,T;A,B;X,Y")
        ttk.Entry(control_frame, textvariable=self.labels_var, width=38).grid(row=4, column=0, columnspan=2, pady=3)

        ttk.Label(control_frame, text="Probabilities per level (optional):").grid(row=5, column=0, sticky=tk.W)
        ttk.Label(control_frame, text="(groups semicolon-separated)").grid(row=6, column=0, columnspan=2, sticky=tk.W)
        self.probs_var = tk.StringVar(value="0.5,0.5;0.3,0.4,0.3;0.6,0.4")
        ttk.Entry(control_frame, textvariable=self.probs_var, width=38).grid(row=7, column=0, columnspan=2, pady=3)

        ttk.Button(control_frame, text="Generate Tree", command=self.generate_tree).grid(row=8, column=0, columnspan=2, pady=8, sticky="ew")

        ttk.Separator(control_frame).grid(row=9, column=0, columnspan=2, sticky="ew", pady=8)

        ttk.Label(control_frame, text="Outcomes & Path Probabilities:").grid(row=10, column=0, columnspan=2, sticky=tk.W)
        self.outcomes_text = tk.Text(control_frame, width=40, height=22, wrap=tk.NONE)
        self.outcomes_text.grid(row=11, column=0, columnspan=2, pady=3)

        ttk.Button(control_frame, text="Export Canvas (PostScript)", command=self.export_canvas).grid(row=12, column=0, columnspan=2, pady=6, sticky="ew")

        # Canvas area
        canvas_frame = ttk.Frame(self.root)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(canvas_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        # initialize
        self.current_tree = None
        self.canvas_width = CANVAS_WIDTH
        self.canvas_height = CANVAS_HEIGHT

    def on_canvas_resize(self, event):
        self.canvas_width = event.width
        self.canvas_height = event.height
        # optional: redraw automatically on resize if we have a tree
        if self.current_tree:
            self.draw_tree(self.current_tree)

    def generate_tree(self):
        # parse inputs
        try:
            levels = int(self.levels_var.get())
            if levels <= 0 or levels > 8:
                messagebox.showerror("Invalid levels", "Levels must be between 1 and 8 (to keep the tree readable).")
                return
        except ValueError:
            messagebox.showerror("Invalid input", "Levels must be an integer.")
            return

        # branching per level
        branches_raw = [b.strip() for b in self.branching_var.get().split(",") if b.strip() != ""]
        branching = []
        try:
            for i in range(levels):
                if i < len(branches_raw):
                    b = int(branches_raw[i])
                else:
                    b = int(branches_raw[-1]) if branches_raw else 2
                if b <= 0 or b > 6:
                    messagebox.showerror("Invalid branching", "Each level's branching must be 1..6 to keep the tree manageable.")
                    return
                branching.append(b)
        except Exception as e:
            messagebox.showerror("Invalid branching input", f"Branching values must be integers. Error: {e}")
            return

        # labels per level
        def default_labels(level_index):
            cnt = branching[level_index]
            return [f"B{i+1}" for i in range(cnt)]
        labels_groups = parse_list_groups(self.labels_var.get(), levels, default_from_count=default_labels)

        # probs per level groups (strings)
        probs_groups_str = parse_list_groups(self.probs_var.get(), levels)  # each group is list of strings
        # convert to floats, handle repeating if only one group provided (we already repeated)
        probs_groups = []
        for gi, group in enumerate(probs_groups_str):
            if not group:
                # default: equal probabilities
                cnt = branching[gi]
                probs_groups.append([1.0/cnt]*cnt)
            else:
                try:
                    floats = [safe_float(x) for x in group]
                except:
                    messagebox.showerror("Invalid probabilities", "Could not parse probability values as floats.")
                    return
                # if count doesn't match branching count, attempt to expand or error
                if len(floats) != branching[gi]:
                    # if single float given, distribute equally?
                    if len(floats) == 1:
                        vals = [floats[0]] + [ (1.0 - floats[0])/(branching[gi]-1) if branching[gi]>1 else 0.0 for _ in range(branching[gi]-1)]
                        floats = vals
                    else:
                        messagebox.showerror("Probability length mismatch",
                            f"Level {gi+1} expects {branching[gi]} probabilities but got {len(floats)}. Provide matching counts per level.")
                        return
                # normalize if sums slightly off
                s = sum(floats)
                if s <= 0:
                    messagebox.showerror("Invalid probabilities", f"Sum of probabilities at level {gi+1} must be > 0.")
                    return
                floats = [f/s for f in floats]
                probs_groups.append(floats)

        # build tree
        root_node = TreeNode(level=0, index=0, label="Start")
        self.build_recursive(root_node, 0, levels, branching, labels_groups, probs_groups)
        self.current_tree = root_node

        # layout nodes positions
        self.layout_tree(root_node, levels)

        # draw
        self.draw_tree(root_node)

        # compute outcomes
        outcomes = []
        self.gather_outcomes(root_node, [], 1.0, outcomes)
        self.display_outcomes(outcomes)

    def build_recursive(self, node, level, levels, branching, labels_groups, probs_groups):
        if level >= levels:
            return
        # for this level, branching[level] children
        b = branching[level]
        labels = labels_groups[level] if level < len(labels_groups) else [f"B{i+1}" for i in range(b)]
        probs = probs_groups[level] if level < len(probs_groups) else [1.0/b]*b
        # if labels fewer, fill defaults
        if len(labels) < b:
            labels = labels + [f"B{i+1}" for i in range(len(labels), b)]
        for i in range(b):
            child = TreeNode(level=level+1, index=i, label=labels[i])
            node.children.append((probs[i], labels[i], child))
            self.build_recursive(child, level+1, levels, branching, labels_groups, probs_groups)

    def layout_tree(self, root_node, levels):
        # compute number of leaves to decide spacing
        leaves = []
        def collect_leaves(n):
            if not n.children:
                leaves.append(n)
            else:
                for _, _, c in n.children:
                    collect_leaves(c)
        collect_leaves(root_node)
        leaf_count = max(1, len(leaves))
        # assign x positions to leaves evenly
        left_margin = 60
        right_margin = 60
        width = max(300, self.canvas_width - left_margin - right_margin)
        for idx, leaf in enumerate(leaves):
            leaf.x = left_margin + (idx + 0.5) * (width/leaf_count)
            leaf.y = NODE_RADIUS + (levels) * LEVEL_GAP

        # for internal nodes, x = average of children
        def set_internal_positions(n):
            if n.children:
                for _, _, c in n.children:
                    set_internal_positions(c)
                xs = [c.x for _, _, c in n.children]
                n.x = sum(xs)/len(xs)
                n.y = NODE_RADIUS + n.level * LEVEL_GAP
            else:
                # leaf already set; level may vary, but use node.level for y
                n.y = NODE_RADIUS + n.level * LEVEL_GAP
        set_internal_positions(root_node)
        # root x if not set (single leaf case)
        if root_node.x == 0:
            root_node.x = self.canvas_width/2
            root_node.y = NODE_RADIUS

    def draw_tree(self, root_node):
        self.canvas.delete("all")
        # recursively draw edges then nodes
        def draw_edges(n):
            for prob, label, c in n.children:
                # draw line
                x1, y1 = n.x, n.y
                x2, y2 = c.x, c.y
                self.canvas.create_line(x1, y1+NODE_RADIUS, x2, y2-NODE_RADIUS, width=2)
                # edge label (probability) at midpoint, slightly offset
                mx = (x1 + x2)/2
                my = (y1 + y2)/2
                prob_text = f"{prob:.3f}"
                # compute offset perpendicular
                dx = x2 - x1
                dy = y2 - y1
                L = max(1.0, math.hypot(dx, dy))
                ux, uy = -dy/L, dx/L
                ox, oy = ux * 12, uy * 8
                self.canvas.create_text(mx+ox, my+oy, text=prob_text, font=("Arial", 10, "italic"))
                # also label the branch (optional)
                self.canvas.create_text((x1+x2)/2, (y1+y2)/2 + 12, text=label, font=("Arial", 10))
                draw_edges(c)
        def draw_nodes(n):
            # circle
            x, y = n.x, n.y
            self.canvas.create_oval(x-NODE_RADIUS, y-NODE_RADIUS, x+NODE_RADIUS, y+NODE_RADIUS, fill="#F0F8FF", outline="#1f4f82")
            # label
            lbl = n.label if n.label is not None else f"Lv{n.level}"
            self.canvas.create_text(x, y, text=lbl, font=("Arial", 10, "bold"))
            for _, _, c in n.children:
                draw_nodes(c)

        draw_edges(root_node)
        draw_nodes(root_node)
        # title
        self.canvas.create_text(self.canvas_width/2, 18, text="Probability Tree", font=("Arial", 14, "bold"))

    def gather_outcomes(self, node, path_labels, path_prob, outcomes):
        if not node.children:
            # leaf
            outcomes.append( (" -> ".join(path_labels[1:]) if path_labels else node.label, path_prob) )
        else:
            for prob, label, c in node.children:
                self.gather_outcomes(c, path_labels + [label], path_prob * prob, outcomes)

    def display_outcomes(self, outcomes):
        # sort descending by probability
        outcomes_sorted = sorted(outcomes, key=lambda x: -x[1])
        self.outcomes_text.delete(1.0, tk.END)
        total = 0.0
        for path, p in outcomes_sorted:
            self.outcomes_text.insert(tk.END, f"{path}  →  {p:.6f}\n")
            total += p
        self.outcomes_text.insert(tk.END, "\nTotal probability (should be 1.0): {:.6f}".format(total))

    def export_canvas(self):
        # Use PostScript export (tkinter canvas supports postscript)
        file = filedialog.asksaveasfilename(defaultextension=".ps", filetypes=[("PostScript","*.ps")], title="Save Canvas as PostScript")
        if not file:
            return
        try:
            # temporarily set scrollregion to bbox
            self.canvas.update()
            self.canvas.postscript(file=file, colormode='color')
            messagebox.showinfo("Exported", f"Canvas exported to {file} (PostScript). Convert to PNG with external tools if desired.")
        except Exception as e:
            messagebox.showerror("Export Error", f"Could not export canvas: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ProbabilityTreeApp(root)
    root.mainloop()

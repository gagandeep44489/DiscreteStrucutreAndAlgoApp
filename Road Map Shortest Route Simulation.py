"""
Road Map Shortest Route Simulation
Single-file Python desktop app (Tkinter) you can run in Visual Studio Code.

Features:
- Click to add nodes (toggle Add Node mode)
- Connect nodes to create weighted edges (Add Edge mode; click two nodes)
- Set Start and Goal nodes (Set Start / Set Goal mode)
- Run Dijkstra's algorithm to compute shortest path
- Step through the algorithm visually (Step button)
- Clear / Reset / Random sample graph

How to run:
1. Save this file as `road_map_shortest_route_simulation.py` in VS Code.
2. Run: `python road_map_shortest_route_simulation.py` (requires Python 3.x)

No external libraries required.
"""

import tkinter as tk
from tkinter import simpledialog, messagebox
import heapq
import math
import random

NODE_RADIUS = 12

class Node:
    def __init__(self, nid, x, y):
        self.id = nid
        self.x = x
        self.y = y

class Edge:
    def __init__(self, a, b, w=1.0):
        self.a = a
        self.b = b
        self.w = w

class RoadMapApp:
    def __init__(self, root):
        self.root = root
        root.title('Road Map Shortest Route Simulation')

        self.canvas = tk.Canvas(root, width=900, height=600, bg='white')
        self.canvas.grid(row=0, column=0, rowspan=20)

        # Controls
        self.mode = tk.StringVar(value='add_node')
        modes = [('Add Node', 'add_node'), ('Add Edge', 'add_edge'),
                 ('Set Start', 'set_start'), ('Set Goal', 'set_goal'), ('Move', 'move')]

        r = 0
        for (text, val) in modes:
            b = tk.Radiobutton(root, text=text, variable=self.mode, value=val)
            b.grid(row=r, column=1, sticky='w', padx=8)
            r += 1

        tk.Button(root, text='Set Weight for Edge', command=self.set_weight_for_edge).grid(row=r, column=1, sticky='we', padx=8)
        r += 1
        tk.Button(root, text='Run Dijkstra', command=self.run_dijkstra).grid(row=r, column=1, sticky='we', padx=8)
        r += 1
        tk.Button(root, text='Step', command=self.step_dijkstra).grid(row=r, column=1, sticky='we', padx=8)
        r += 1
        tk.Button(root, text='Reset Algorithm', command=self.reset_algorithm).grid(row=r, column=1, sticky='we', padx=8)
        r += 1
        tk.Button(root, text='Clear All', command=self.clear_all).grid(row=r, column=1, sticky='we', padx=8)
        r += 1
        tk.Button(root, text='Random Sample Graph', command=self.random_graph).grid(row=r, column=1, sticky='we', padx=8)
        r += 1
        tk.Button(root, text='Help / Instructions', command=self.show_help).grid(row=r, column=1, sticky='we', padx=8)

        # Data
        self.nodes = {}   # id -> Node
        self.edges = []   # list of Edge
        self.node_counter = 0

        # UI handles for items
        self.node_items = {}  # node id -> (oval_id, text_id)
        self.edge_items = []  # list of (line_id, text_id, edge)

        # For edge creation
        self.edge_first = None

        # For moving nodes
        self.moving_node = None

        # Start / Goal
        self.start = None
        self.goal = None

        # Dijkstra state
        self.dijkstra_gen = None
        self.dijkstra_result = None  # (distances, prev)

        # Bind events
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<B1-Motion>', self.on_canvas_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_canvas_release)

        self.draw_instructions()

    # ---------- UI helper functions ----------
    def draw_instructions(self):
        self.canvas.delete('header')
        text = 'Modes: Add Node | Add Edge | Set Start | Set Goal | Move   •  Click canvas to act according to mode.'
        self.canvas.create_text(450, 12, text=text, tag='header', font=('Arial', 10), fill='gray')

    def show_help(self):
        help_text = (
            'Instructions:\n'
            '- Add Node: click anywhere to add a node.\n'
            '- Add Edge: click two nodes to connect them; you will be prompted for weight.\n'
            "- Set Start / Set Goal: choose mode and click a node.\n"
            '- Move: drag a node to reposition it.\n'
            '- Run Dijkstra: compute shortest path from Start to Goal.\n'
            '- Step: step through Dijkstra visualization.\n'
            '- Reset Algorithm: clears Dijkstra highlights but keeps graph.\n'
            '- Random Sample Graph: populates a sample graph for testing.\n'
        )
        messagebox.showinfo('Help / Instructions', help_text)

    def clear_all(self):
        self.nodes.clear()
        self.edges.clear()
        self.node_items.clear()
        for item in self.edge_items:
            self.canvas.delete(item[0])
            self.canvas.delete(item[1])
        self.edge_items.clear()
        self.canvas.delete('node')
        self.canvas.delete('edge')
        self.node_counter = 0
        self.edge_first = None
        self.start = None
        self.goal = None
        self.reset_algorithm()

    def random_graph(self):
        self.clear_all()
        n = 8
        margin = 60
        for i in range(n):
            x = random.randint(margin, 900 - margin)
            y = random.randint(50 + margin, 600 - margin)
            self.add_node_at(x, y)
        # connect randomly
        ids = list(self.nodes.keys())
        for i in range(n):
            a = ids[i]
            for j in range(i+1, n):
                if random.random() < 0.35:
                    b = ids[j]
                    w = round(math.dist((self.nodes[a].x, self.nodes[a].y), (self.nodes[b].x, self.nodes[b].y)) / 50, 2)
                    self.add_edge(a, b, w)
        # set random start/goal
        if ids:
            self.start = ids[0]
            self.goal = ids[-1]
            self.update_node_colors()

    # ---------- Node / Edge manipulation ----------
    def add_node_at(self, x, y):
        nid = self.node_counter
        self.node_counter += 1
        node = Node(nid, x, y)
        self.nodes[nid] = node
        oval = self.canvas.create_oval(x - NODE_RADIUS, y - NODE_RADIUS, x + NODE_RADIUS, y + NODE_RADIUS, fill='lightgray', tags=('node',))
        text = self.canvas.create_text(x, y, text=str(nid), tags=('node',))
        self.node_items[nid] = (oval, text)
        self.canvas.tag_bind(oval, '<Button-1>', lambda e, nid=nid: self.on_node_click(nid))
        self.canvas.tag_bind(text, '<Button-1>', lambda e, nid=nid: self.on_node_click(nid))
        self.update_node_colors()
        return nid

    def find_node_at(self, x, y):
        for nid, node in self.nodes.items():
            if (x - node.x) ** 2 + (y - node.y) ** 2 <= NODE_RADIUS ** 2:
                return nid
        return None

    def on_node_click(self, nid):
        mode = self.mode.get()
        if mode == 'add_edge':
            if self.edge_first is None:
                self.edge_first = nid
                self.highlight_node(nid, outline='blue')
            else:
                if self.edge_first != nid:
                    w = simpledialog.askfloat('Edge weight', 'Enter weight (positive number):', minvalue=0.0)
                    if w is None:
                        # cancel
                        self.unhighlight_node(self.edge_first)
                        self.edge_first = None
                        return
                    self.add_edge(self.edge_first, nid, w)
                self.unhighlight_node(self.edge_first)
                self.edge_first = None
        elif mode == 'set_start':
            self.start = nid
            self.update_node_colors()
        elif mode == 'set_goal':
            self.goal = nid
            self.update_node_colors()
        elif mode == 'move':
            self.moving_node = nid
        elif mode == 'add_node':
            # add node near clicked location
            node = self.nodes[nid]
            self.add_node_at(node.x + 20, node.y + 20)

    def on_canvas_click(self, event):
        mode = self.mode.get()
        x, y = event.x, event.y
        if mode == 'add_node':
            self.add_node_at(x, y)
        elif mode == 'move':
            nid = self.find_node_at(x, y)
            if nid is not None:
                self.moving_node = nid
        else:
            # maybe clicked empty space; clear edge_first selection
            if self.edge_first is not None:
                self.unhighlight_node(self.edge_first)
                self.edge_first = None

    def on_canvas_drag(self, event):
        if self.moving_node is not None:
            self.move_node_to(self.moving_node, event.x, event.y)

    def on_canvas_release(self, event):
        self.moving_node = None

    def move_node_to(self, nid, x, y):
        node = self.nodes[nid]
        node.x = x
        node.y = y
        oval, text = self.node_items[nid]
        self.canvas.coords(oval, x - NODE_RADIUS, y - NODE_RADIUS, x + NODE_RADIUS, y + NODE_RADIUS)
        self.canvas.coords(text, x, y)
        self.redraw_edges()

    def add_edge(self, a, b, w=1.0):
        # avoid duplicate
        if a == b:
            return
        for e in self.edges:
            if (e.a == a and e.b == b) or (e.a == b and e.b == a):
                # update weight
                e.w = w
                self.redraw_edges()
                return
        edge = Edge(a, b, w)
        self.edges.append(edge)
        self.redraw_edges()

    def set_weight_for_edge(self):
        if not self.edges:
            messagebox.showinfo('Info', 'No edges to set weight for.')
            return
        choices = ['{} - {} (w={})'.format(e.a, e.b, e.w) for e in self.edges]
        choice = simpledialog.askinteger('Choose edge index', 'Enter edge index (0 - {}):'.format(len(self.edges)-1), minvalue=0, maxvalue=len(self.edges)-1)
        if choice is None:
            return
        e = self.edges[choice]
        w = simpledialog.askfloat('Edge weight', 'Enter new weight:', minvalue=0.0)
        if w is None:
            return
        e.w = w
        self.redraw_edges()

    # ---------- Drawing edges / nodes ----------
    def redraw_edges(self):
        # clear existing edge items
        for line_id, text_id, _ in self.edge_items:
            self.canvas.delete(line_id)
            self.canvas.delete(text_id)
        self.edge_items.clear()

        for idx, e in enumerate(self.edges):
            a = self.nodes[e.a]
            b = self.nodes[e.b]
            line = self.canvas.create_line(a.x, a.y, b.x, b.y, width=2, tags=('edge',))
            # weight label midpoint
            mx = (a.x + b.x) / 2
            my = (a.y + b.y) / 2
            txt = self.canvas.create_text(mx, my - 10, text=str(e.w), tags=('edge',))
            self.edge_items.append((line, txt, e))
        self.update_node_colors()

    def update_node_colors(self):
        for nid, (oval, text) in self.node_items.items():
            fill = 'lightgray'
            outline = 'black'
            if nid == self.start:
                fill = 'orange'
            if nid == self.goal:
                fill = 'lightgreen'
            self.canvas.itemconfig(oval, fill=fill, outline=outline)

    def highlight_node(self, nid, outline='blue'):
        if nid in self.node_items:
            oval, _ = self.node_items[nid]
            self.canvas.itemconfig(oval, outline=outline, width=3)

    def unhighlight_node(self, nid):
        if nid in self.node_items:
            oval, _ = self.node_items[nid]
            self.canvas.itemconfig(oval, outline='black', width=1)

    # ---------- Dijkstra algorithm & visualization ----------
    def reset_algorithm(self):
        # Clear visualization highlights
        for line_id, text_id, edge in self.edge_items:
            self.canvas.itemconfig(line_id, fill='black', width=2)
        for nid, (oval, text) in self.node_items.items():
            self.canvas.itemconfig(oval, fill=('orange' if nid == self.start else ('lightgreen' if nid == self.goal else 'lightgray')))
        self.dijkstra_gen = None
        self.dijkstra_result = None

    def run_dijkstra(self):
        if self.start is None or self.goal is None:
            messagebox.showwarning('Missing nodes', 'Please set both Start and Goal nodes before running.')
            return
        self.dijkstra_gen = None
        dist, prev = self.dijkstra(self.start)
        self.dijkstra_result = (dist, prev)
        if dist.get(self.goal, math.inf) == math.inf:
            messagebox.showinfo('Result', 'No path found from {} to {}'.format(self.start, self.goal))
            return
        path = self.reconstruct_path(prev, self.goal)
        self.animate_final_path(path)

    def step_dijkstra(self):
        # initialize generator if needed
        if self.dijkstra_gen is None:
            if self.start is None or self.goal is None:
                messagebox.showwarning('Missing nodes', 'Please set both Start and Goal nodes before stepping.')
                return
            self.dijkstra_gen = self.dijkstra_step(self.start)
        try:
            info = next(self.dijkstra_gen)
            self.visualize_step(info)
        except StopIteration as e:
            # finished; maybe show path
            if self.dijkstra_result is None:
                # if result wasn't set, compute final result quickly
                dist, prev = self.dijkstra(self.start)
                self.dijkstra_result = (dist, prev)
            dist, prev = self.dijkstra_result
            if dist.get(self.goal, math.inf) == math.inf:
                messagebox.showinfo('Result', 'No path found from {} to {}'.format(self.start, self.goal))
            else:
                path = self.reconstruct_path(prev, self.goal)
                self.animate_final_path(path)

    def visualize_step(self, info):
        # info contains: visited_set, frontier_heap (as list), current_node, distances, prev
        visited, frontier, current, distances, prev = info
        # color visited nodes
        for nid in self.nodes.keys():
            oval, _ = self.node_items[nid]
            if nid in visited:
                self.canvas.itemconfig(oval, fill='skyblue')
            else:
                self.canvas.itemconfig(oval, fill=('orange' if nid == self.start else ('lightgreen' if nid == self.goal else 'lightgray')))
        # highlight frontier nodes
        for nid in self.nodes.keys():
            if nid in [item[1] for item in frontier]:
                oval, _ = self.node_items[nid]
                self.canvas.itemconfig(oval, fill='yellow')
        # highlight current
        if current is not None:
            if current in self.node_items:
                oval, _ = self.node_items[current]
                self.canvas.itemconfig(oval, fill='red')
        # update distances on edges / nodes
        for nid in self.nodes.keys():
            # update node text to include distance if known
            oval, text = self.node_items[nid]
            d = distances.get(nid, math.inf)
            display = str(nid) + (('\n{:.1f}'.format(d)) if d < math.inf else '')
            self.canvas.itemconfig(text, text=display)
        # color edges that are relaxed (part of prev tree)
        for line_id, text_id, edge in self.edge_items:
            self.canvas.itemconfig(line_id, fill='black', width=2)
        for nid, p in prev.items():
            if p is not None:
                # find edge connecting nid and p
                for line_id, text_id, edge in self.edge_items:
                    if (edge.a == nid and edge.b == p) or (edge.b == nid and edge.a == p):
                        self.canvas.itemconfig(line_id, fill='purple', width=3)
                        break

    def animate_final_path(self, path):
        # reset nodes then highlight path
        for nid, (oval, text) in self.node_items.items():
            self.canvas.itemconfig(oval, fill=('orange' if nid == self.start else ('lightgreen' if nid == self.goal else 'lightgray')))
            self.canvas.itemconfig(text, text=str(nid))
        # color edges along path
        for line_id, text_id, edge in self.edge_items:
            self.canvas.itemconfig(line_id, fill='black', width=2)
        for i in range(len(path)-1):
            a = path[i]
            b = path[i+1]
            for line_id, text_id, edge in self.edge_items:
                if (edge.a == a and edge.b == b) or (edge.a == b and edge.b == a):
                    self.canvas.itemconfig(line_id, fill='green', width=4)
                    break
        # highlight path nodes
        for nid in path:
            if nid in self.node_items:
                oval, _ = self.node_items[nid]
                self.canvas.itemconfig(oval, fill='green')

    def reconstruct_path(self, prev, goal):
        path = []
        cur = goal
        while cur is not None:
            path.append(cur)
            cur = prev.get(cur, None)
        path.reverse()
        return path

    def dijkstra(self, start):
        # Standard Dijkstra returning distances and predecessor map
        dist = {nid: math.inf for nid in self.nodes}
        prev = {nid: None for nid in self.nodes}
        dist[start] = 0
        heap = [(0, start)]
        adj = self.build_adj()
        visited = set()
        while heap:
            d, u = heapq.heappop(heap)
            if u in visited:
                continue
            visited.add(u)
            for v, w in adj.get(u, []):
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(heap, (nd, v))
        self.dijkstra_result = (dist, prev)
        return dist, prev

    def dijkstra_step(self, start):
        # Generator that yields intermediate states for visualization
        dist = {nid: math.inf for nid in self.nodes}
        prev = {nid: None for nid in self.nodes}
        dist[start] = 0
        heap = [(0, start)]
        adj = self.build_adj()
        visited = set()
        while heap:
            d, u = heapq.heappop(heap)
            if u in visited:
                yield (visited.copy(), list(heap), None, dict(dist), dict(prev))
                continue
            # yield state before processing u
            yield (visited.copy(), list(heap), u, dict(dist), dict(prev))
            visited.add(u)
            for v, w in adj.get(u, []):
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(heap, (nd, v))
                    # yield after relaxation
                    yield (visited.copy(), list(heap), u, dict(dist), dict(prev))
        # final yield
        self.dijkstra_result = (dist, prev)
        yield (visited.copy(), list(heap), None, dict(dist), dict(prev))

    def build_adj(self):
        adj = {nid: [] for nid in self.nodes}
        for e in self.edges:
            if e.a in adj and e.b in adj:
                adj[e.a].append((e.b, e.w))
                adj[e.b].append((e.a, e.w))
        return adj


if __name__ == '__main__':
    root = tk.Tk()
    app = RoadMapApp(root)
    root.mainloop()

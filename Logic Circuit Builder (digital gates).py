"""
Logic Circuit Builder — Python (tkinter)

Single-file desktop application to build simple digital logic circuits visually.

Features:
- Palette with components: INPUT, OUTPUT, AND, OR, NOT, NAND, NOR, XOR
- Drag-and-drop placement on canvas
- Connect wires: click a gate's output pin, then click a gate's input pin
- Toggle INPUT nodes (0/1)
- Evaluate circuit: compute gate outputs by topological evaluation
- Export / Import circuit as JSON
- Generate truth table for up to 6 input variables

Limitations / Notes:
- This is a learning/demo tool and does not include advanced layout or timing.
- Avoid creating cycles (feedback loops) — evaluation expects a directed acyclic graph.

Run: python "Logic Circuit Builder — Python (tkinter).py"
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import itertools

# --------------------- Core circuit model ---------------------

class Gate:
    UID_COUNTER = 1

    def __init__(self, kind, x, y):
        self.id = f"G{Gate.UID_COUNTER}"
        Gate.UID_COUNTER += 1
        self.kind = kind  # 'INPUT', 'OUTPUT', 'AND', 'OR', 'NOT', 'NAND', 'NOR', 'XOR'
        self.x = x
        self.y = y
        self.width = 100
        self.height = 50
        self.inputs = []  # list of (gate_id, pin_index) sources feeding this gate
        self.input_values = []  # temporary during evaluation
        self.output_value = False
        # for INPUT gates: store explicit logic value
        if kind == 'INPUT':
            self.output_value = False
        # number of input pins
        self.num_inputs = 1 if kind == 'NOT' or kind == 'OUTPUT' else (2 if kind not in ('INPUT',) else 0)

    def to_dict(self):
        return {
            'id': self.id,
            'kind': self.kind,
            'x': self.x,
            'y': self.y,
            'inputs': self.inputs,
            'value': self.output_value if self.kind == 'INPUT' else None
        }

    @staticmethod
    def from_dict(d):
        g = Gate(d['kind'], d['x'], d['y'])
        g.id = d['id']
        g.inputs = d.get('inputs', [])
        if g.kind == 'INPUT' and d.get('value') is not None:
            g.output_value = bool(d.get('value'))
        return g

    def evaluate(self, input_values):
        # input_values: list of booleans feeding this gate (length matches num_inputs)
        k = self.kind
        if k == 'INPUT':
            return bool(self.output_value)
        if k == 'OUTPUT':
            # output gate simply forwards its single input
            return bool(input_values[0]) if input_values else False
        # unary NOT
        if k == 'NOT':
            return not bool(input_values[0])
        # binary gates (AND, OR, XOR, NAND, NOR)
        a, b = bool(input_values[0]), bool(input_values[1])
        if k == 'AND':
            return a and b
        if k == 'OR':
            return a or b
        if k == 'XOR':
            return (a and not b) or (not a and b)
        if k == 'NAND':
            return not (a and b)
        if k == 'NOR':
            return not (a or b)
        # fallback
        return False

# --------------------- GUI / Controller ---------------------

class CircuitApp(tk.Tk):
    PALETTE = ['INPUT', 'OUTPUT', 'AND', 'OR', 'NOT', 'NAND', 'NOR', 'XOR']

    def __init__(self):
        super().__init__()
        self.title('Logic Circuit Builder')
        self.geometry('1100x700')

        # Model
        self.gates = {}  # id -> Gate
        self.wires = []  # list of {'from': (gate_id), 'to': (gate_id, pin_index)}

        # UI state
        self.selected_tool = tk.StringVar(value=self.PALETTE[0])
        self.selected_gate_id = None
        self.drag_offset = (0, 0)
        self.connecting_from = None  # gate id for output being connected

        self._build_ui()

    def _build_ui(self):
        # Left palette
        left = ttk.Frame(self, width=180, padding=8)
        left.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(left, text='Palette', font=('Segoe UI', 12, 'bold')).pack(pady=(0,8))
        for kind in self.PALETTE:
            b = ttk.Button(left, text=kind, width=16, command=lambda k=kind: self.select_tool(k))
            b.pack(pady=4)
        ttk.Separator(left, orient='horizontal').pack(fill=tk.X, pady=8)

        ttk.Button(left, text='Generate Truth Table', command=self.on_truth_table).pack(fill=tk.X, pady=6)
        ttk.Button(left, text='Evaluate', command=self.evaluate_circuit).pack(fill=tk.X, pady=6)
        ttk.Button(left, text='Clear', command=self.clear_canvas).pack(fill=tk.X, pady=6)
        ttk.Separator(left, orient='horizontal').pack(fill=tk.X, pady=8)
        ttk.Button(left, text='Export JSON', command=self.export_json).pack(fill=tk.X, pady=4)
        ttk.Button(left, text='Import JSON', command=self.import_json).pack(fill=tk.X, pady=4)

        # Top toolbar
        top = ttk.Frame(self, padding=8)
        top.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(top, text='Selected tool:').pack(side=tk.LEFT)
        ttk.Label(top, textvariable=self.selected_tool, font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=6)

        # Main canvas
        self.canvas = tk.Canvas(self, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<B1-Motion>', self.on_canvas_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_canvas_release)
        self.canvas.bind('<Double-Button-1>', self.on_double_click)

        # Internal maps for visuals
        self.canvas_items = {}  # gate_id -> dict with shapes

    # ----------------- UI actions -----------------

    def select_tool(self, kind):
        self.selected_tool.set(kind)
        self.connecting_from = None

    def on_canvas_click(self, event):
        x, y = event.x, event.y
        tool = self.selected_tool.get()
        # if a tool is selected that places gates
        if tool:
            # If click on an existing gate, select / start drag / start connect
            gid = self._find_gate_at(x, y)
            if gid:
                self.selected_gate_id = gid
                gx, gy = self.gates[gid].x, self.gates[gid].y
                self.drag_offset = (x - gx, y - gy)
                # check if clicked on output pin area (right side)
                if self._is_on_output_pin(gid, x, y):
                    # start connecting
                    self.connecting_from = gid
                # check if clicked on input pin to complete connection
                elif self.connecting_from and self._is_on_input_pin(gid, x, y):
                    pin_index = self._input_pin_index_at(gid, x, y)
                    # create connection from connecting_from -> (gid, pin_index)
                    self._add_wire(self.connecting_from, gid, pin_index)
                    self.connecting_from = None
                    self.redraw()
                else:
                    # start moving
                    pass
            else:
                # Click on empty canvas: place a new gate of tool type
                self._place_gate(tool, x, y)
        else:
            # no tool: nothing
            pass

    def on_double_click(self, event):
        # toggle input values if clicked on an INPUT gate
        x, y = event.x, event.y
        gid = self._find_gate_at(x, y)
        if gid and self.gates[gid].kind == 'INPUT':
            self.gates[gid].output_value = not self.gates[gid].output_value
            self.redraw()

    def on_canvas_drag(self, event):
        if self.selected_gate_id:
            gid = self.selected_gate_id
            gx = event.x - self.drag_offset[0]
            gy = event.y - self.drag_offset[1]
            self.gates[gid].x = gx
            self.gates[gid].y = gy
            self.redraw()

    def on_canvas_release(self, event):
        self.selected_gate_id = None

    # ----------------- Model operations -----------------

    def _place_gate(self, kind, x, y):
        g = Gate(kind, x, y)
        # ensure proper num_inputs for OUTPUT
        if kind == 'OUTPUT':
            g.num_inputs = 1
        if kind == 'INPUT':
            g.num_inputs = 0
        self.gates[g.id] = g
        self.canvas_items[g.id] = {}
        self.redraw()

    def _find_gate_at(self, x, y):
        for gid, g in self.gates.items():
            if (g.x - 10) <= x <= (g.x + g.width + 10) and (g.y - 10) <= y <= (g.y + g.height + 10):
                return gid
        return None

    def _is_on_output_pin(self, gid, x, y):
        g = self.gates[gid]
        px = g.x + g.width
        py = g.y + g.height // 2
        return abs(x - px) <= 10 and abs(y - py) <= 12

    def _is_on_input_pin(self, gid, x, y):
        g = self.gates[gid]
        # inputs arranged on left side
        # if unary: center; if binary: top and bottom
        if g.num_inputs == 1:
            px = g.x
            py = g.y + g.height // 2
            return abs(x - px) <= 10 and abs(y - py) <= 12
        else:
            px = g.x
            py1 = g.y + g.height // 3
            py2 = g.y + 2 * g.height // 3
            return (abs(x - px) <= 10 and abs(y - py1) <= 12) or (abs(x - px) <= 10 and abs(y - py2) <= 12)

    def _input_pin_index_at(self, gid, x, y):
        g = self.gates[gid]
        if g.num_inputs == 1:
            return 0
        py1 = g.y + g.height // 3
        py2 = g.y + 2 * g.height // 3
        if abs(y - py1) < abs(y - py2):
            return 0
        else:
            return 1

    def _add_wire(self, from_gid, to_gid, to_pin_index):
        # avoid duplicate or self-connections
        if from_gid == to_gid:
            messagebox.showwarning('Invalid connection', 'Cannot connect a gate to itself.')
            return
        # remove existing wire to that input if present
        self.wires = [w for w in self.wires if not (w['to'][0] == to_gid and w['to'][1] == to_pin_index)]
        self.wires.append({'from': from_gid, 'to': (to_gid, to_pin_index)})
        # store in gate inputs structure for serialization
        self.gates[to_gid].inputs = [(w['from'], w['to'][1]) for w in self.wires if w['to'][0] == to_gid]

    def clear_canvas(self):
        if messagebox.askyesno('Confirm', 'Clear all gates and wires?'):
            self.gates.clear()
            self.wires.clear()
            self.canvas_items.clear()
            Gate.UID_COUNTER = 1
            self.redraw()

    # ----------------- Evaluation -----------------

    def evaluate_circuit(self):
        try:
            order = self._topological_order()
        except ValueError as e:
            messagebox.showerror('Evaluation error', str(e))
            return
        # evaluate in order
        for gid in order:
            g = self.gates[gid]
            # gather input values
            in_vals = []
            if g.num_inputs > 0:
                # find wires connecting to this gate in correct pin index order
                # build list sized num_inputs
                vals = [False] * g.num_inputs
                for w in self.wires:
                    if w['to'][0] == gid:
                        src = w['from']
                        pin = w['to'][1]
                        vals[pin] = self.gates[src].output_value
                in_vals = vals
            val = g.evaluate(in_vals)
            g.output_value = val
        self.redraw()
        messagebox.showinfo('Evaluation complete', 'Circuit evaluated and outputs updated.')

    def _topological_order(self):
        # Kahn's algorithm on directed graph where edges from source->target
        # nodes are gates. We consider dependencies: a node depends on its inputs' sources.
        deps = {gid: set() for gid in self.gates}
        rev = {gid: set() for gid in self.gates}
        for w in self.wires:
            src = w['from']
            dst = w['to'][0]
            deps[dst].add(src)
            rev[src].add(dst)
        # nodes with no deps
        L = []
        S = [n for n, d in deps.items() if len(d) == 0]
        while S:
            n = S.pop()
            L.append(n)
            for m in list(rev[n]):
                deps[m].remove(n)
                rev[n].remove(m)
                if len(deps[m]) == 0:
                    S.append(m)
        # if any node still has deps, cycle exists
        if any(len(d) > 0 for d in deps.values()):
            raise ValueError('Cycle detected in circuit. Remove feedback loops before evaluation.')
        return L

    # ----------------- Truth table generation -----------------

    def on_truth_table(self):
        # find input gates
        inputs = [g for g in self.gates.values() if g.kind == 'INPUT']
        if not inputs:
            messagebox.showwarning('No inputs', 'At least one INPUT gate is required for truth table generation.')
            return
        if len(inputs) > 6:
            if not messagebox.askyesno('Large truth table', f'{len(inputs)} inputs will generate {2**len(inputs)} rows. Continue?'):
                return
        # order inputs by id for deterministic table
        inputs = sorted(inputs, key=lambda g: g.id)
        var_names = [g.id for g in inputs]
        rows = []
        for bits in itertools.product([0,1], repeat=len(inputs)):
            # set input values
            for g, b in zip(inputs, bits):
                g.output_value = bool(b)
            # evaluate
            try:
                self.evaluate_circuit()
            except Exception as e:
                messagebox.showerror('Error', f'Could not evaluate circuit: {e}')
                return
            # read outputs (all OUTPUT gates)
            outputs = [g for g in self.gates.values() if g.kind == 'OUTPUT']
            outputs = sorted(outputs, key=lambda g: g.id)
            outvals = [1 if o.output_value else 0 for o in outputs]
            rows.append((list(bits), outvals))
        # display in simple window
        self._show_truth_table_window(var_names, rows)

    def _show_truth_table_window(self, var_names, rows):
        w = tk.Toplevel(self)
        w.title('Truth Table')
        txt = tk.Text(w, width=100, height=30)
        txt.pack(fill=tk.BOTH, expand=True)
        # headers
        outputs = [g.id for g in sorted([g for g in self.gates.values() if g.kind == 'OUTPUT'], key=lambda g: g.id)]
        header = ' | '.join(var_names) + ' || ' + ' | '.join(outputs) + '\n'
        txt.insert(tk.END, header)
        txt.insert(tk.END, '-'*len(header) + '\n')
        for bits, outvals in rows:
            line = ' | '.join(str(b) for b in bits) + ' || ' + ' | '.join(str(o) for o in outvals) + '\n'
            txt.insert(tk.END, line)
        txt.config(state=tk.DISABLED)

    # ----------------- Serialization -----------------

    def export_json(self):
        path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON', '*.json')])
        if not path:
            return
        data = {
            'gates': [g.to_dict() for g in self.gates.values()],
            'wires': self.wires
        }
        try:
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo('Saved', f'Circuit exported to {path}')
        except Exception as e:
            messagebox.showerror('Save error', f'Could not save file: {e}')

    def import_json(self):
        path = filedialog.askopenfilename(filetypes=[('JSON', '*.json')])
        if not path:
            return
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            self.gates.clear()
            self.wires.clear()
            for gd in data.get('gates', []):
                g = Gate.from_dict(gd)
                self.gates[g.id] = g
            self.wires = data.get('wires', [])
            # re-sync inputs list in gates
            for gid in self.gates:
                self.gates[gid].inputs = [(w['from'], w['to'][1]) for w in self.wires if w['to'][0] == gid]
            self.redraw()
            messagebox.showinfo('Loaded', f'Circuit loaded from {path}')
        except Exception as e:
            messagebox.showerror('Load error', f'Could not load file: {e}')

    # ----------------- Drawing -----------------

    def redraw(self):
        self.canvas.delete('all')
        # draw wires first
        for w in self.wires:
            src = self.gates.get(w['from'])
            dst = self.gates.get(w['to'][0])
            if not src or not dst:
                continue
            sx = src.x + src.width
            sy = src.y + src.height // 2
            # destination pin coords by index
            pin_index = w['to'][1]
            if dst.num_inputs == 1:
                dx = dst.x
                dy = dst.y + dst.height // 2
            else:
                dx = dst.x
                if pin_index == 0:
                    dy = dst.y + dst.height // 3
                else:
                    dy = dst.y + 2 * dst.height // 3
            self.canvas.create_line(sx, sy, dx, dy, width=2, arrow=tk.LAST)

        # draw gates
        for gid, g in self.gates.items():
            x0, y0 = g.x, g.y
            x1, y1 = x0 + g.width, y0 + g.height
            rect = self.canvas.create_rectangle(x0, y0, x1, y1, fill='#f0f0f0', outline='black')
            txt = self.canvas.create_text(x0 + g.width/2, y0 + g.height/2, text=f"{g.kind}\n{g.id}")
            self.canvas_items[gid] = {'rect': rect, 'text': txt}
            # draw output pin on right
            ox = x1
            oy = y0 + g.height//2
            oval = self.canvas.create_oval(ox-6, oy-6, ox+6, oy+6, fill='green' if g.output_value else 'red')
            # draw input pins
            if g.num_inputs == 1:
                ix = x0
                iy = y0 + g.height//2
                self.canvas.create_oval(ix-6, iy-6, ix+6, iy+6, fill='blue')
            elif g.num_inputs == 2:
                ix = x0
                iy1 = y0 + g.height//3
                iy2 = y0 + 2*g.height//3
                self.canvas.create_oval(ix-6, iy1-6, ix+6, iy1+6, fill='blue')
                self.canvas.create_oval(ix-6, iy2-6, ix+6, iy2+6, fill='blue')

    # ----------------- Main loop -----------------


def main():
    app = CircuitApp()
    app.mainloop()

if __name__ == '__main__':
    main()

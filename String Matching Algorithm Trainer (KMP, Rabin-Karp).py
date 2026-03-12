#!/usr/bin/env python3
"""
String Matching Algorithm Trainer (KMP, Rabin-Karp)

A desktop Tkinter app to learn and compare KMP and Rabin-Karp string matching.
- Enter text + pattern
- Choose one algorithm or run both
- Inspect step-by-step trace
- See KMP LPS table and Rabin-Karp rolling-hash details
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class MatchResult:
    algorithm: str
    matches: List[int]
    steps: List[str]
    extras: List[str]


def build_lps(pattern: str) -> Tuple[List[int], List[str]]:
    """Build LPS array for KMP and return detailed construction steps."""
    lps = [0] * len(pattern)
    steps: List[str] = ["LPS construction start"]

    length = 0
    i = 1
    while i < len(pattern):
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            steps.append(
                f"i={i}: pattern[i]='{pattern[i]}' matches pattern[length-1], set lps[{i}]={length}"
            )
            i += 1
        else:
            if length != 0:
                steps.append(
                    f"i={i}: mismatch ('{pattern[i]}' != '{pattern[length]}'), fallback length from {length} to lps[{length - 1}]={lps[length - 1]}"
                )
                length = lps[length - 1]
            else:
                lps[i] = 0
                steps.append(
                    f"i={i}: mismatch with length=0, set lps[{i}]=0"
                )
                i += 1

    steps.append("LPS construction done")
    return lps, steps


def run_kmp(text: str, pattern: str) -> MatchResult:
    if not pattern:
        return MatchResult("KMP", [], ["Pattern is empty."], [])

    lps, lps_steps = build_lps(pattern)
    steps: List[str] = []
    matches: List[int] = []

    i = 0  # text index
    j = 0  # pattern index

    while i < len(text):
        if text[i] == pattern[j]:
            steps.append(
                f"text[{i}]='{text[i]}' matches pattern[{j}]='{pattern[j]}': advance i,j"
            )
            i += 1
            j += 1

            if j == len(pattern):
                start = i - j
                matches.append(start)
                steps.append(
                    f"Full match ending at text index {i-1}. Start = {start}. Next j = lps[{j-1}]={lps[j-1]}"
                )
                j = lps[j - 1]
        else:
            if j != 0:
                steps.append(
                    f"Mismatch text[{i}]='{text[i]}' vs pattern[{j}]='{pattern[j]}': fallback j -> lps[{j-1}]={lps[j-1]}"
                )
                j = lps[j - 1]
            else:
                steps.append(
                    f"Mismatch text[{i}]='{text[i]}' vs pattern[0]='{pattern[0]}': j=0, move i"
                )
                i += 1

    extras = [f"LPS: {lps}"] + lps_steps
    return MatchResult("KMP", matches, steps, extras)


def run_rabin_karp(text: str, pattern: str, base: int = 256, mod: int = 101) -> MatchResult:
    if not pattern:
        return MatchResult("Rabin-Karp", [], ["Pattern is empty."], [])

    n = len(text)
    m = len(pattern)
    if m > n:
        return MatchResult("Rabin-Karp", [], ["Pattern longer than text."], [f"base={base}, mod={mod}"])

    h = pow(base, m - 1, mod)

    p_hash = 0
    t_hash = 0
    for i in range(m):
        p_hash = (base * p_hash + ord(pattern[i])) % mod
        t_hash = (base * t_hash + ord(text[i])) % mod

    matches: List[int] = []
    steps: List[str] = [
        f"Initial hashes: pattern_hash={p_hash}, text_window_hash={t_hash}, h={h}"
    ]

    for s in range(n - m + 1):
        if p_hash == t_hash:
            window = text[s:s + m]
            steps.append(
                f"Shift {s}: hash match ({p_hash}). Verifying window '{window}' with pattern '{pattern}'"
            )
            if window == pattern:
                matches.append(s)
                steps.append(f"Shift {s}: verification success -> match")
            else:
                steps.append(f"Shift {s}: verification failed (spurious hit)")
        else:
            steps.append(
                f"Shift {s}: hash mismatch pattern_hash={p_hash}, window_hash={t_hash}"
            )

        if s < n - m:
            outgoing = ord(text[s])
            incoming = ord(text[s + m])
            t_hash = (base * (t_hash - outgoing * h) + incoming) % mod
            t_hash = (t_hash + mod) % mod
            steps.append(
                f"Roll hash to shift {s+1}: remove '{text[s]}'({outgoing}), add '{text[s+m]}'({incoming}) -> {t_hash}"
            )

    extras = [
        f"Parameters: base={base}, mod={mod}",
        f"Pattern hash: {p_hash}",
    ]
    return MatchResult("Rabin-Karp", matches, steps, extras)


class StringMatchingTrainer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("String Matching Algorithm Trainer (KMP, Rabin-Karp)")
        self.geometry("1100x760")
        self._build_ui()

    def _build_ui(self):
        outer = ttk.Frame(self, padding=10)
        outer.pack(fill="both", expand=True)

        top = ttk.LabelFrame(outer, text="Input", padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Text:").grid(row=0, column=0, sticky="nw")
        self.text_input = tk.Text(top, height=6, wrap="word")
        self.text_input.grid(row=0, column=1, columnspan=5, sticky="ew", padx=6)

        ttk.Label(top, text="Pattern:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.pattern_var = tk.StringVar(value="aba")
        ttk.Entry(top, textvariable=self.pattern_var, width=40).grid(
            row=1, column=1, sticky="w", padx=6, pady=(8, 0)
        )

        ttk.Label(top, text="Algorithm:").grid(row=1, column=2, sticky="e", pady=(8, 0))
        self.algorithm_var = tk.StringVar(value="Both")
        ttk.Combobox(
            top,
            textvariable=self.algorithm_var,
            values=["KMP", "Rabin-Karp", "Both"],
            state="readonly",
            width=15,
        ).grid(row=1, column=3, sticky="w", padx=6, pady=(8, 0))

        self.case_sensitive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            top,
            text="Case Sensitive",
            variable=self.case_sensitive_var,
        ).grid(row=1, column=4, sticky="w", padx=6, pady=(8, 0))

        btn_row = ttk.Frame(top)
        btn_row.grid(row=1, column=5, sticky="e", pady=(8, 0))
        ttk.Button(btn_row, text="Run", command=self.run_algorithms).pack(side="left", padx=4)
        ttk.Button(btn_row, text="Use Example", command=self.load_example).pack(side="left", padx=4)
        ttk.Button(btn_row, text="Clear", command=self.clear_output).pack(side="left", padx=4)

        top.columnconfigure(1, weight=1)

        middle = ttk.PanedWindow(outer, orient="horizontal")
        middle.pack(fill="both", expand=True, pady=10)

        result_frame = ttk.LabelFrame(middle, text="Results", padding=10)
        trace_frame = ttk.LabelFrame(middle, text="Trace", padding=10)
        middle.add(result_frame, weight=2)
        middle.add(trace_frame, weight=3)

        self.result_text = tk.Text(result_frame, height=18, wrap="word", state="disabled")
        self.result_text.pack(fill="both", expand=True)

        self.trace_text = tk.Text(trace_frame, height=18, wrap="none", state="disabled")
        self.trace_text.pack(side="left", fill="both", expand=True)

        y_scroll = ttk.Scrollbar(trace_frame, orient="vertical", command=self.trace_text.yview)
        y_scroll.pack(side="right", fill="y")
        self.trace_text.configure(yscrollcommand=y_scroll.set)

        bottom = ttk.LabelFrame(outer, text="Notes", padding=10)
        bottom.pack(fill="x")
        notes = (
            "KMP avoids re-checking characters by using the LPS table.\n"
            "Rabin-Karp uses rolling hash to skip many direct character comparisons.\n"
            "Tip: Try repetitive text (like 'aaaaaa...') to compare algorithm behavior."
        )
        ttk.Label(bottom, text=notes, justify="left").pack(anchor="w")

        self.load_example()

    def load_example(self):
        self.text_input.delete("1.0", "end")
        self.text_input.insert("1.0", "ababcabcabababd")
        self.pattern_var.set("ababd")
        self.algorithm_var.set("Both")
        self.case_sensitive_var.set(True)
        self.clear_output()

    def clear_output(self):
        for widget in (self.result_text, self.trace_text):
            widget.configure(state="normal")
            widget.delete("1.0", "end")
            widget.configure(state="disabled")

    def _append(self, widget: tk.Text, line: str = ""):
        widget.configure(state="normal")
        widget.insert("end", line + "\n")
        widget.configure(state="disabled")

    def run_algorithms(self):
        text = self.text_input.get("1.0", "end").rstrip("\n")
        pattern = self.pattern_var.get()

        if not text:
            messagebox.showerror("Input Error", "Text cannot be empty.")
            return
        if pattern == "":
            messagebox.showerror("Input Error", "Pattern cannot be empty.")
            return

        if not self.case_sensitive_var.get():
            text_cmp = text.lower()
            pattern_cmp = pattern.lower()
        else:
            text_cmp = text
            pattern_cmp = pattern

        selected = self.algorithm_var.get()

        results: List[MatchResult] = []
        if selected in ("KMP", "Both"):
            results.append(run_kmp(text_cmp, pattern_cmp))
        if selected in ("Rabin-Karp", "Both"):
            results.append(run_rabin_karp(text_cmp, pattern_cmp))

        self.clear_output()
        for res in results:
            self._append(self.result_text, f"=== {res.algorithm} ===")
            self._append(self.result_text, f"Matches at indices: {res.matches if res.matches else 'None'}")
            if res.extras:
                for extra in res.extras:
                    self._append(self.result_text, f"- {extra}")
            self._append(self.result_text)

            self._append(self.trace_text, f"=== {res.algorithm} Trace ===")
            for idx, step in enumerate(res.steps, start=1):
                self._append(self.trace_text, f"{idx:03d}. {step}")
            self._append(self.trace_text)


if __name__ == "__main__":
    app = StringMatchingTrainer()
    app.mainloop()
# Filename: graph_centrality_analyzer.py

import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt

# Function to calculate centrality
def calculate_centrality():
    try:
        nodes = int(nodes_entry.get())
        edges_input = edges_text.get("1.0", tk.END).strip().split("\n")
        
        G = nx.Graph()
        G.add_nodes_from(range(1, nodes+1))
        
        for edge in edges_input:
            u, v = map(int, edge.strip().split(','))
            G.add_edge(u, v)
        
        degree_centrality = nx.degree_centrality(G)
        closeness_centrality = nx.closeness_centrality(G)
        betweenness_centrality = nx.betweenness_centrality(G)
        eigenvector_centrality = nx.eigenvector_centrality(G, max_iter=500)
        
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, "Degree Centrality:\n")
        result_text.insert(tk.END, f"{degree_centrality}\n\n")
        result_text.insert(tk.END, "Closeness Centrality:\n")
        result_text.insert(tk.END, f"{closeness_centrality}\n\n")
        result_text.insert(tk.END, "Betweenness Centrality:\n")
        result_text.insert(tk.END, f"{betweenness_centrality}\n\n")
        result_text.insert(tk.END, "Eigenvector Centrality:\n")
        result_text.insert(tk.END, f"{eigenvector_centrality}\n\n")
        
        # Draw Graph
        plt.figure(figsize=(6,5))
        nx.draw(G, with_labels=True, node_color='lightblue', edge_color='gray', node_size=800)
        plt.show()
        
    except Exception as e:
        messagebox.showerror("Error", f"Invalid input! Details:\n{e}")

# Tkinter window
root = tk.Tk()
root.title("Graph Centrality Analyzer")
root.geometry("600x700")

# Number of nodes input
tk.Label(root, text="Number of Nodes:").pack(pady=5)
nodes_entry = tk.Entry(root)
nodes_entry.pack(pady=5)

# Edges input
tk.Label(root, text="Edges (one per line, format: u,v):").pack(pady=5)
edges_text = tk.Text(root, height=10)
edges_text.pack(pady=5)

# Calculate button
calc_btn = tk.Button(root, text="Calculate Centrality", command=calculate_centrality)
calc_btn.pack(pady=10)

# Result display
tk.Label(root, text="Centrality Results:").pack(pady=5)
result_text = tk.Text(root, height=20)
result_text.pack(pady=5)

root.mainloop()

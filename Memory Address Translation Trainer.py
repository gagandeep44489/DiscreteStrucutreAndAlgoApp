import tkinter as tk
from tkinter import messagebox

class MemoryTranslationTrainer:
    def __init__(self, root):
        self.root = root
        self.root.title("Memory Address Translation Trainer")
        self.root.geometry("850x600")

        # Sample Page Table (VPN -> PFN)
        self.page_table = {0: 5, 1: 8, 2: 12, 3: 15, 4: 3, 5: 9}

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Enter Virtual Address:", font=("Arial", 12)).pack(pady=5)
        self.virtual_entry = tk.Entry(self.root, width=30)
        self.virtual_entry.pack(pady=5)

        tk.Label(self.root, text="Enter Page Size:", font=("Arial", 12)).pack(pady=5)
        self.page_size_entry = tk.Entry(self.root, width=30)
        self.page_size_entry.insert(0, "16")
        self.page_size_entry.pack(pady=5)

        tk.Button(self.root, text="Translate Address", command=self.translate_address).pack(pady=10)
        tk.Button(self.root, text="Clear", command=self.clear_output).pack(pady=5)

        self.output_text = tk.Text(self.root, height=18, width=100)
        self.output_text.pack(pady=10)

        tk.Label(self.root, text="Page Table (VPN → PFN)", font=("Arial", 12, "bold")).pack(pady=5)

        self.page_table_list = tk.Listbox(self.root, width=40, height=8)
        self.page_table_list.pack(pady=5)

        for vpn, pfn in self.page_table.items():
            self.page_table_list.insert(tk.END, f"{vpn} → {pfn}")

    def translate_address(self):
        try:
            virtual_address = int(self.virtual_entry.get())
            page_size = int(self.page_size_entry.get())
        except:
            messagebox.showerror("Error", "Please enter valid integers.")
            return

        vpn = virtual_address // page_size
        offset = virtual_address % page_size

        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"Virtual Address: {virtual_address}\n")
        self.output_text.insert(tk.END, f"Page Size: {page_size}\n\n")

        self.output_text.insert(tk.END, f"Step 1: Extract VPN and Offset\n")
        self.output_text.insert(tk.END, f"VPN = {virtual_address} // {page_size} = {vpn}\n")
        self.output_text.insert(tk.END, f"Offset = {virtual_address} % {page_size} = {offset}\n\n")

        self.output_text.insert(tk.END, "Step 2: Page Table Lookup\n")

        if vpn not in self.page_table:
            self.output_text.insert(tk.END, "Page Fault! VPN not found in page table.\n")
            return

        pfn = self.page_table[vpn]
        self.output_text.insert(tk.END, f"PFN found: {pfn}\n\n")

        self.output_text.insert(tk.END, "Step 3: Calculate Physical Address\n")
        physical_address = (pfn * page_size) + offset
        self.output_text.insert(tk.END,
                                f"Physical Address = ({pfn} × {page_size}) + {offset} = {physical_address}\n")

    def clear_output(self):
        self.virtual_entry.delete(0, tk.END)
        self.output_text.delete(1.0, tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = MemoryTranslationTrainer(root)
    root.mainloop()
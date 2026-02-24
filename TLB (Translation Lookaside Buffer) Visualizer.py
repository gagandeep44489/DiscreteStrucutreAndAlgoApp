import tkinter as tk
from tkinter import messagebox

PAGE_SIZE = 16
TLB_SIZE = 4

class TLBVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("TLB (Translation Lookaside Buffer) Visualizer")
        self.root.geometry("800x600")

        self.tlb = []  # Stores (VPN, PFN)
        self.page_table = {i: i + 5 for i in range(32)}  # Simple mapping
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Enter Virtual Address:").pack(pady=5)

        self.address_entry = tk.Entry(self.root, width=30)
        self.address_entry.pack(pady=5)

        tk.Button(self.root, text="Translate Address", command=self.translate).pack(pady=10)

        self.output_text = tk.Text(self.root, height=10, width=90)
        self.output_text.pack(pady=10)

        tk.Label(self.root, text="Current TLB Entries (FIFO):").pack(pady=5)

        self.tlb_listbox = tk.Listbox(self.root, width=50, height=6)
        self.tlb_listbox.pack(pady=5)

    def update_tlb_display(self):
        self.tlb_listbox.delete(0, tk.END)
        for vpn, pfn in self.tlb:
            self.tlb_listbox.insert(tk.END, f"VPN: {vpn} → PFN: {pfn}")

    def translate(self):
        try:
            virtual_address = int(self.address_entry.get())
        except:
            messagebox.showerror("Error", "Enter a valid integer virtual address.")
            return

        vpn = virtual_address // PAGE_SIZE
        offset = virtual_address % PAGE_SIZE

        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"Virtual Address: {virtual_address}\n")
        self.output_text.insert(tk.END, f"VPN: {vpn}, Offset: {offset}\n")

        # TLB Lookup
        for entry in self.tlb:
            if entry[0] == vpn:
                pfn = entry[1]
                physical_address = pfn * PAGE_SIZE + offset
                self.output_text.insert(tk.END, "TLB HIT!\n")
                self.output_text.insert(tk.END, f"Physical Address: {physical_address}\n")
                return

        # TLB Miss
        self.output_text.insert(tk.END, "TLB MISS!\n")

        if vpn not in self.page_table:
            self.output_text.insert(tk.END, "Page Fault! VPN not in page table.\n")
            return

        pfn = self.page_table[vpn]

        # FIFO Replacement
        if len(self.tlb) >= TLB_SIZE:
            self.tlb.pop(0)

        self.tlb.append((vpn, pfn))
        self.update_tlb_display()

        physical_address = pfn * PAGE_SIZE + offset
        self.output_text.insert(tk.END, f"Loaded into TLB: VPN {vpn} → PFN {pfn}\n")
        self.output_text.insert(tk.END, f"Physical Address: {physical_address}\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = TLBVisualizer(root)
    root.mainloop()
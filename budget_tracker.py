import tkinter as tk 
from tkinter import ttk, messagebox, filedialog # GUI tools
from datetime import datetime # for working with dates 
import json # saving/loading data
import csv # exporting a csv
from pathlib import Path # for file paths 
from collections import defaultdict # for counting totals

#!/usr/bin/env python3
"""
Friendly Budget Tracker - single-file Tkinter app
Features:
- Add Income/Expense with date, category, description, amount
- List of entries with delete
- Running totals and balance
- Save/load to JSON (~/.budget_tracker.json)
- Export CSV
- Optional pie chart (requires matplotlib)
"""

# default location for saving user data
DATA_FILE = Path.home() / ".budget_tracker.json"

# formats function as currency ex $12.34
def fmt_currency(v):
    return f"${v:,.2f}"

# App
class BudgetApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Friendly Budget Tracker")
        self.geometry("800x520") # window size
        self.style = ttk.Style(self) # styling for widgets
        self.style.theme_use("clam") # use clam theme
        self.style.configure("Treeview", rowheight=24)
        self.data = [] # list to hold budget entries
        self._build_ui() # build the user interface
        self.load_data() # load saved data

    def _build_ui(self):
        """
        Create all the UI elements:
        - Input fields for date, type, category, amount, description
        - Buttons to add/delete entries
        - Treeview table to show entries
        - Summary labels for income, expense, balance
        - Buttons for saving/loading/exporting data
        """
        # top input frame
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="x")
        # labels for input fields
        ttk.Label(frm, text="Date").grid(row=0, column=0, sticky="w")
        ttk.Label(frm, text="Type").grid(row=0, column=1, sticky="w")
        ttk.Label(frm, text="Category").grid(row=0, column=2, sticky="w")
        ttk.Label(frm, text="Amount").grid(row=0, column=3, sticky="w")
        ttk.Label(frm, text="Description").grid(row=0, column=4, sticky="w")

        # input field variables
        self.date_var = tk.StringVar(value=datetime.now().date().isoformat())
        self.type_var = tk.StringVar(value="Expense")
        self.cat_var = tk.StringVar(value="General")
        self.amt_var = tk.StringVar()
        self.desc_var = tk.StringVar()

        # entry widgets for input fields
        self.date_entry = ttk.Entry(frm, textvariable=self.date_var, width=12)
        self.date_entry.grid(row=1, column=0, padx=4)
        self.type_cb = ttk.Combobox(frm, textvariable=self.type_var, values=["Expense", "Income"], width=10, state="readonly")
        self.type_cb.grid(row=1, column=1, padx=4)
        self.cat_cb = ttk.Combobox(frm, textvariable=self.cat_var, values=["General", "Food", "Rent", "Transport", "Utilities", "Entertainment", "Religious"], width=16)
        self.cat_cb.grid(row=1, column=2, padx=4)
        self.amt_entry = ttk.Entry(frm, textvariable=self.amt_var, width=12)
        self.amt_entry.grid(row=1, column=3, padx=4)
        self.desc_entry = ttk.Entry(frm, textvariable=self.desc_var, width=30)
        self.desc_entry.grid(row=1, column=4, padx=4)

        # buttons to add/delete entries
        add_btn = ttk.Button(frm, text="Add Entry", command=self.add_entry)
        add_btn.grid(row=1, column=5, padx=6)
        del_btn = ttk.Button(frm, text="Delete Selected", command=self.delete_selected)
        del_btn.grid(row=1, column=6, padx=6)

        # Treeview
        cols = ("date", "type", "category", "description", "amount")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", selectmode="browse")
        self.tree.heading("date", text="Date")
        self.tree.heading("type", text="Type")
        self.tree.heading("category", text="Category")
        self.tree.heading("description", text="Description")
        self.tree.heading("amount", text="Amount")
        self.tree.column("date", width=90, anchor="center")
        self.tree.column("type", width=80, anchor="center")
        self.tree.column("category", width=110, anchor="w")
        self.tree.column("description", width=300, anchor="w")
        self.tree.column("amount", width=100, anchor="e")
        self.tree.pack(fill="both", expand=True, padx=10, pady=8)

        # Summary and actions
        bottom = ttk.Frame(self, padding=10)
        bottom.pack(fill="x")
        self.income_var = tk.StringVar(value=fmt_currency(0))
        self.expense_var = tk.StringVar(value=fmt_currency(0))
        self.balance_var = tk.StringVar(value=fmt_currency(0))

        # summary labels
        ttk.Label(bottom, text="Total Income:").grid(row=0, column=0, sticky="w")
        ttk.Label(bottom, textvariable=self.income_var, foreground="green").grid(row=0, column=1, sticky="w")
        ttk.Label(bottom, text="Total Expense:").grid(row=0, column=2, sticky="w", padx=(20,0))
        ttk.Label(bottom, textvariable=self.expense_var, foreground="red").grid(row=0, column=3, sticky="w")
        ttk.Label(bottom, text="Balance:").grid(row=0, column=4, sticky="w", padx=(20,0))
        ttk.Label(bottom, textvariable=self.balance_var, font=("TkDefaultFont", 10, "bold")).grid(row=0, column=5, sticky="w")

        # action buttons
        save_btn = ttk.Button(bottom, text="Save Now", command=self.save_data)
        save_btn.grid(row=0, column=6, padx=8)
        load_btn = ttk.Button(bottom, text="Load...", command=self.open_file)
        load_btn.grid(row=0, column=7, padx=8)
        export_btn = ttk.Button(bottom, text="Export CSV...", command=self.export_csv)
        export_btn.grid(row=0, column=8, padx=8)
        chart_btn = ttk.Button(bottom, text="Show Expense Pie", command=self.show_pie)
        chart_btn.grid(row=0, column=9, padx=8)

        # Bind double-click to edit
        self.tree.bind("<Double-1>", self.on_edit)

        # Save on close
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def add_entry(self):
        """Add a new income/expense entry from input fields"""
        date_s = self.date_var.get().strip()
        typ = self.type_var.get()
        cat = self.cat_var.get().strip() or "General"
        desc = self.desc_var.get().strip()
        amt_s = self.amt_var.get().strip()
        try:
            amt = float(amt_s)
        except ValueError:
            messagebox.showerror("Invalid amount", "Please enter a valid number for amount.")
            return
        if typ == "Expense" and amt > 0:
            amt = -amt  # expenses stored as negative
        # validate date
        try:
            # allow YYYY-MM-DD
            d = datetime.fromisoformat(date_s).date()
            date_s = d.isoformat()
        except Exception:
            messagebox.showerror("Invalid date", "Date must be YYYY-MM-DD.")
            return
        entry = {"date": date_s, "type": typ, "category": cat, "description": desc, "amount": amt}
        self.data.append(entry)
        self._insert_tree(entry)
        self._update_summary()
        # Add category to combobox suggestions
        if cat not in self.cat_cb['values']:
            vals = list(self.cat_cb['values']) + [cat]
            self.cat_cb['values'] = vals
        # clear amount and desc
        self.amt_var.set("")
        self.desc_var.set("")

    def _insert_tree(self, entry):
        """Insert a row into the Treeview table"""
        amt_str = fmt_currency(entry["amount"])  # keep negative numbers directly
        iid = self.tree.insert("", "end",
                            values=(entry["date"], entry["type"], entry["category"], entry["description"], amt_str))
        return iid

    def delete_selected(self):
        """Delete selected row and update totals"""
        sel = self.tree.selection()
        if not sel:
            return
        if not messagebox.askyesno("Delete", "Delete selected entry?"):
            return

        iid = sel[0]
        vals = self.tree.item(iid, "values")
        date, typ, cat, desc, amt_str = vals

        # Convert amount back to float (handles negative automatically)
        amt = float(amt_str.replace("$","").replace(",",""))

        # Find matching entry in self.data
        for i, entry in enumerate(self.data):
            if (entry["date"] == date and entry["type"] == typ and 
                entry["category"] == cat and entry["description"] == desc and 
                abs(entry["amount"] - amt) < 0.0001):
                del self.data[i]
                break

        # Delete row from Treeview
        self.tree.delete(iid)

        # Always update summary totals
        self._update_summary()

    def _update_summary(self):
        """Recalculate totals and balance"""
        
        income = sum(e["amount"] for e in self.data if e["amount"] > 0)
        expense = -sum(e["amount"] for e in self.data if e["amount"] < 0)
        balance = income - expense
        self.income_var.set(fmt_currency(income))
        self.expense_var.set(fmt_currency(expense))
        self.balance_var.set(fmt_currency(balance))

    def save_data(self):
        """Save data to JSON file"""
        
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Saved", f"Saved to {DATA_FILE}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def load_data(self):
        """Load data from JSON file and update table"""
        
        if DATA_FILE.exists():
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = []
        else:
            self.data = []
        # Populate tree
        for row in self.tree.get_children():
            self.tree.delete(row)
        for e in self.data:
            self._insert_tree(e)
        self._update_summary()

    def open_file(self):
        """Open data from a user-selected JSON file"""

        path = filedialog.askopenfilename(title="Open JSON data", filetypes=[("JSON files","*.json"),("All files","*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            # refresh
            for row in self.tree.get_children():
                self.tree.delete(row)
            for e in self.data:
                self._insert_tree(e)
            self._update_summary()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load: {e}")

    def export_csv(self):
        """Export data to CSV file"""
        
        path = filedialog.asksaveasfilename(title="Export CSV", defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["date", "type", "category", "description", "amount"])
                for e in self.data:
                    writer.writerow([e["date"], e["type"], e["category"], e["description"], e["amount"]])
            messagebox.showinfo("Exported", f"Exported to {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {e}")

    def show_pie(self):
        """Generate expense by category pie chart (requires matplotlib)"""
        
        try:
            import matplotlib.pyplot as plt
        except Exception:
            messagebox.showerror("Missing dependency", "matplotlib is required for charts. Install via 'pip install matplotlib'.")
            return
        d = defaultdict(float)
        for e in self.data:
            if e["amount"] < 0:
                d[e["category"]] += -e["amount"]
        if not d:
            messagebox.showinfo("No expenses", "There are no expense entries to chart.")
            return
        labels = list(d.keys())
        sizes = list(d.values())
        plt.figure(figsize=(6,6))
        plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140)
        plt.title("Expenses by Category")
        plt.tight_layout()
        plt.show()

    def on_edit(self, event):
        """Populate input fields from selected row for quick update"""
        
        sel = self.tree.selection()
        if not sel:
            return
        iid = sel[0]
        vals = self.tree.item(iid, "values")
        date, typ, cat, desc, amt_str = vals
        amt = amt_str.replace("$", "").replace(",", "")
        # handle negative
        if amt_str.strip().startswith("-"):
            amt = "-" + amt.lstrip("-").strip()
        self.date_var.set(date)
        self.type_var.set(typ)
        self.cat_var.set(cat)
        # convert amount back to absolute for input
        try:
            amt_f = float(amt)
            # if expense, show positive number
            if typ == "Expense":
                amt_f = abs(amt_f)
            self.amt_var.set(str(amt_f))
        except Exception:
            self.amt_var.set("")
        self.desc_var.set(desc)

    def on_close(self):
        """Save data automatically when closing window"""
        
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
        self.destroy()

# run the application
if __name__ == "__main__":
    app = BudgetApp()
    app.mainloop()
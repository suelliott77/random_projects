import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os

#!/usr/bin/env python3
# grade_gpa_calculator.py
# Simple grade & GPA calculator GUI using tkinter.
# Letter mapping: A=4.0, B=3.0, C=2.0, D=1.0 (F=0.0 included)


GRADE_VALUES = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "F": 0.0}

class GradeGPAApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Grade & GPA Calculator")
        self.resizable(False, False)
        self.current_gpa = 0.0
        self.current_credits = 0.0
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        frm = ttk.Frame(self, padding=10)
        frm.grid(row=0, column=0, sticky="nsew")

        # Input row
        ttk.Label(frm, text="Course:").grid(row=0, column=0, padx=2, pady=2, sticky="w")
        self.course_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.course_var, width=20).grid(row=0, column=1, padx=2, pady=2)

        ttk.Label(frm, text="Grade:").grid(row=0, column=2, padx=2, pady=2, sticky="w")
        self.grade_var = tk.StringVar(value="A")
        grade_box = ttk.Combobox(frm, textvariable=self.grade_var, values=list(GRADE_VALUES.keys()), state="readonly", width=3)
        grade_box.grid(row=0, column=3, padx=2, pady=2)

        ttk.Label(frm, text="Credits:").grid(row=0, column=4, padx=2, pady=2, sticky="w")
        self.credits_var = tk.StringVar(value="3")
        ttk.Entry(frm, textvariable=self.credits_var, width=6).grid(row=0, column=5, padx=2, pady=2)

        ttk.Button(frm, text="Add Course", command=self.add_course).grid(row=0, column=6, padx=6)

        # Courses list
        cols = ("course", "grade", "credits")
        self.tree = ttk.Treeview(frm, columns=cols, show="headings", height=8)
        self.tree.grid(row=1, column=0, columnspan=7, pady=(8,0))
        for c, heading in zip(cols, ("Course", "Grade", "Credits")):
            self.tree.heading(c, text=heading)
            self.tree.column(c, anchor="center", width=120 if c=="course" else 70)

        # Buttons
        ttk.Button(frm, text="Remove Selected", command=self.remove_selected).grid(row=2, column=0, columnspan=2, pady=8, sticky="w")
        ttk.Button(frm, text="Calculate GPA", command=self.calculate_gpa).grid(row=2, column=2, columnspan=2, pady=8)
        ttk.Button(frm, text="Add Current GPA", command=self.add_current_gpa).grid(row=2, column=4, columnspan=2, pady=8)

        # Results
        self.total_credits_var = tk.StringVar(value="0")
        self.gpa_var = tk.StringVar(value="0.000")
        ttk.Label(frm, text="Total Credits:").grid(row=2, column=6, sticky="e")
        ttk.Label(frm, textvariable=self.total_credits_var, width=8).grid(row=2, column=7, sticky="w")
        ttk.Label(frm, text="GPA:").grid(row=3, column=6, sticky="e")
        ttk.Label(frm, textvariable=self.gpa_var, width=8).grid(row=3, column=7, sticky="w")

        # Save/Load buttons
        ttk.Button(frm, text="Save", command=self.save_data).grid(row=3, column=0, columnspan=2, pady=8, sticky="w")
        ttk.Button(frm, text="Load", command=self.load_file).grid(row=3, column=2, columnspan=2, pady=8)

        # Double-click to edit a row
        self.tree.bind("<Double-1>", self._on_edit)

    def add_course(self):
        course = self.course_var.get().strip() or "Untitled"
        grade = self.grade_var.get().strip().upper()
        credits_text = self.credits_var.get().strip()
        try:
            credits = float(credits_text)
            if credits <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Credits", "Credits must be a positive number (e.g., 3 or 0.5).")
            return
        if grade not in GRADE_VALUES:
            messagebox.showerror("Invalid Grade", "Select a valid grade (A, B, C, D, F).")
            return
        self.tree.insert("", "end", values=(course, grade, f"{credits:.2f}"))
        self.course_var.set("")
        self.credits_var.set("3")

    def remove_selected(self):
        for sel in self.tree.selection():
            self.tree.delete(sel)
        self.calculate_gpa()

    def calculate_gpa(self):
        total_credits = 0.0
        total_points = 0.0
        for iid in self.tree.get_children():
            course, grade, credits_text = self.tree.item(iid, "values")
            try:
                credits = float(credits_text)
            except ValueError:
                credits = 0.0
            value = GRADE_VALUES.get(grade.upper(), 0.0)
            total_credits += credits
            total_points += value * credits
        
        # Include current GPA in calculation
        if self.current_credits > 0:
            total_credits += self.current_credits
            total_points += self.current_gpa * self.current_credits
        
        gpa = (total_points / total_credits) if total_credits > 0 else 0.0
        self.total_credits_var.set(f"{total_credits:.2f}")
        self.gpa_var.set(f"{gpa:.3f}")

    def _on_edit(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return
        values = self.tree.item(item, "values")
        edit = EditDialog(self, values)
        self.wait_window(edit)
        if edit.result:
            course, grade, credits = edit.result
            self.tree.item(item, values=(course, grade, f"{float(credits):.2f}"))
            self.calculate_gpa()

    def add_current_gpa(self):
        dialog = CurrentGPADialog(self)
        self.wait_window(dialog)
        if dialog.result:
            self.current_gpa, self.current_credits = dialog.result
            self.calculate_gpa()

    def save_data(self):
        courses = []
        for iid in self.tree.get_children():
            course, grade, credits = self.tree.item(iid, "values")
            courses.append({"course": course, "grade": grade, "credits": float(credits)})
        
        data = {
            "courses": courses,
            "current_gpa": self.current_gpa,
            "current_credits": self.current_credits
        }
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="grade_calculator.json"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
                messagebox.showinfo("Success", f"Data saved to {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save data: {e}")

    def load_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Clear existing courses
                for iid in self.tree.get_children():
                    self.tree.delete(iid)
                
                # Load courses
                for course_data in data.get("courses", []):
                    self.tree.insert("", "end", values=(
                        course_data["course"],
                        course_data["grade"],
                        f"{float(course_data['credits']):.2f}"
                    ))
                
                # Load current GPA
                self.current_gpa = data.get("current_gpa", 0.0)
                self.current_credits = data.get("current_credits", 0.0)
                
                self.calculate_gpa()
                messagebox.showinfo("Success", f"Data loaded from {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load data: {e}")

    def load_data(self):
        default_file = "grade_calculator.json"
        if os.path.exists(default_file):
            try:
                with open(default_file, 'r') as f:
                    data = json.load(f)
                
                for course_data in data.get("courses", []):
                    self.tree.insert("", "end", values=(
                        course_data["course"],
                        course_data["grade"],
                        f"{float(course_data['credits']):.2f}"
                    ))
                
                self.current_gpa = data.get("current_gpa", 0.0)
                self.current_credits = data.get("current_credits", 0.0)
                self.calculate_gpa()
            except Exception:
                pass

class EditDialog(tk.Toplevel):
    def __init__(self, parent, values):
        super().__init__(parent)
        self.title("Edit Course")
        self.resizable(False, False)
        self.result = None
        ttk.Label(self, text="Course:").grid(row=0, column=0, padx=6, pady=6)
        self.course_var = tk.StringVar(value=values[0])
        ttk.Entry(self, textvariable=self.course_var, width=25).grid(row=0, column=1, padx=6, pady=6)

        ttk.Label(self, text="Grade:").grid(row=1, column=0, padx=6, pady=6)
        self.grade_var = tk.StringVar(value=values[1])
        ttk.Combobox(self, textvariable=self.grade_var, values=list(GRADE_VALUES.keys()), state="readonly", width=4).grid(row=1, column=1, padx=6, pady=6, sticky="w")

        ttk.Label(self, text="Credits:").grid(row=2, column=0, padx=6, pady=6)
        self.credits_var = tk.StringVar(value=values[2])
        ttk.Entry(self, textvariable=self.credits_var, width=10).grid(row=2, column=1, padx=6, pady=6, sticky="w")

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=8)
        ttk.Button(btn_frame, text="OK", command=self._on_ok).grid(row=0, column=0, padx=6)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).grid(row=0, column=1, padx=6)

    def _on_ok(self):
        course = self.course_var.get().strip() or "Untitled"
        grade = self.grade_var.get().strip().upper()
        credits_text = self.credits_var.get().strip()
        try:
            credits = float(credits_text)
            if credits <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Credits", "Credits must be a positive number.")
            return
        if grade not in GRADE_VALUES:
            messagebox.showerror("Invalid Grade", "Choose A, B, C, D or F.")
            return
        self.result = (course, grade, f"{credits:.2f}")
        self.destroy()

class CurrentGPADialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add Current GPA")
        self.resizable(False, False)
        self.result = None
        
        ttk.Label(self, text="Current GPA:").grid(row=0, column=0, padx=6, pady=6)
        self.gpa_var = tk.StringVar(value="0.0")
        ttk.Entry(self, textvariable=self.gpa_var, width=10).grid(row=0, column=1, padx=6, pady=6)
        
        ttk.Label(self, text="Credits Completed:").grid(row=1, column=0, padx=6, pady=6)
        self.credits_var = tk.StringVar(value="0")
        ttk.Entry(self, textvariable=self.credits_var, width=10).grid(row=1, column=1, padx=6, pady=6)
        
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=8)
        ttk.Button(btn_frame, text="OK", command=self._on_ok).grid(row=0, column=0, padx=6)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).grid(row=0, column=1, padx=6)
    
    def _on_ok(self):
        try:
            gpa = float(self.gpa_var.get().strip())
            credits = float(self.credits_var.get().strip())
            if gpa < 0 or gpa > 4.0:
                raise ValueError
            if credits < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "GPA must be between 0.0-4.0 and credits must be non-negative.")
            return
        self.result = (gpa, credits)
        self.destroy()

if __name__ == "__main__":
    app = GradeGPAApp()
    app.mainloop()
import tkinter as tk
from tkinter import font, ttk
import math

class TI84Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("TI-84 Calculator")
        self.root.geometry("420x540")
        self.root.resizable(False, False)
        
        self.display_var = tk.StringVar(value="0")
        self.memory = 0
        
        self.create_widgets()
    
    def create_widgets(self):
        # Styling and top frame
        default_font = ("Segoe UI", 14)
        display_font = ("Segoe UI", 28)

        # ttk theme for native look where available
        try:
            style = ttk.Style()
            style.theme_use('clam')
        except Exception:
            pass

        top = ttk.Frame(self.root, padding=(10,8))
        top.pack(fill="x")

        # memory indicator
        self.mem_label = ttk.Label(top, text="", anchor="w", font=("Segoe UI", 9))
        self.mem_label.pack(fill="x")

        # Display
        # Keep display as tk.Entry for easier color control
        display = tk.Entry(top, textvariable=self.display_var, font=display_font,
                   justify="right", bd=0, bg="#0b1020", fg="#ffffff", insertbackground="#ffffff")
        display.pack(fill="both", pady=(6,0), ipady=14)

        # Button layout (grid)
        buttons = [
            ["M+", "M-", "MR", "MC", "C"],
            ["7", "8", "9", "/", "sqrt"],
            ["4", "5", "6", "*", "^2"],
            ["1", "2", "3", "-", "1/x"],
            ["0", ".", "=", "+", "sin"],
            ["cos", "tan", "log", "ln", "π"]
        ]

        button_frame = ttk.Frame(self.root, padding=(10,10))
        button_frame.pack(fill="both", expand=True)

        # Colors for groups
        op_bg = "#ffb74d"
        func_bg = "#90caf9"
        eq_bg = "#81c784"

        # Define button groups for styling
        operators = {"/", "*", "-", "+", "=", "sqrt", "^2", "1/x"}
        functions = {"sin", "cos", "tan", "log", "ln"}

        for r, row in enumerate(buttons):
            for c, btn_text in enumerate(row):
                # Use colored tk.Button for operators/functions for clearer visuals
                if btn_text in operators:
                    btn = tk.Button(button_frame, text=btn_text, font=default_font,
                                    bg=op_bg, activebackground=op_bg, relief="raised",
                                    command=lambda x=btn_text: self.on_button_click(x))
                elif btn_text in functions or btn_text in {"π", "sqrt", "^2", "1/x"}:
                    btn = tk.Button(button_frame, text=btn_text, font=default_font,
                                    bg=func_bg, activebackground=func_bg,
                                    command=lambda x=btn_text: self.on_button_click(x))
                elif btn_text == "=":
                    btn = tk.Button(button_frame, text=btn_text, font=default_font,
                                    bg=eq_bg, activebackground=eq_bg,
                                    command=lambda x=btn_text: self.on_button_click(x))
                else:
                    btn = ttk.Button(button_frame, text=btn_text, command=lambda x=btn_text: self.on_button_click(x))

                btn.grid(row=r, column=c, sticky="nsew", padx=6, pady=6)

        # Configure grid to make buttons uniform size
        rows = len(buttons)
        cols = len(buttons[0])
        for r in range(rows):
            button_frame.rowconfigure(r, weight=1)
        for c in range(cols):
            button_frame.columnconfigure(c, weight=1)

        # Keyboard bindings
        self.root.bind('<Key>', self.on_key_press)
        self.root.bind('<Return>', lambda e: self.on_button_click('='))
        self.root.bind('<BackSpace>', lambda e: self.on_button_click('←'))
        self.root.bind('<Escape>', lambda e: self.on_button_click('C'))
    
    def on_button_click(self, char):
        current = self.display_var.get()

        # If previous evaluation produced an error, start fresh on next input
        if current == "Error" and char not in {"C", "MR", "MC"}:
            current = "0"

        # Clear
        if char == "C":
            self.display_var.set("0")
            return

        # Equals
        if char == "=":
            self.calculate()
            return

        # Memory operations
        if char == "M+":
            try:
                self.memory += float(current)
            except Exception:
                pass
            self.update_memory_label()
            return
        if char == "M-":
            try:
                self.memory -= float(current)
            except Exception:
                pass
            self.update_memory_label()
            return
        if char == "MR":
            self.display_var.set(str(self.memory))
            return
        if char == "MC":
            self.memory = 0
            self.update_memory_label()
            return

        # Immediate unary operations (apply to current displayed value)
        if char == "sqrt":
            try:
                self.display_var.set(str(math.sqrt(float(current))))
            except Exception:
                self.display_var.set("Error")
            return
        if char == "^2":
            try:
                self.display_var.set(str(float(current) ** 2))
            except Exception:
                self.display_var.set("Error")
            return
        if char == "1/x":
            try:
                self.display_var.set(str(1 / float(current)))
            except Exception:
                self.display_var.set("Error")
            return
        if char in {"sin", "cos", "tan", "log", "ln"}:
            try:
                val = float(current)
                if char == "sin":
                    self.display_var.set(str(math.sin(math.radians(val))))
                elif char == "cos":
                    self.display_var.set(str(math.cos(math.radians(val))))
                elif char == "tan":
                    self.display_var.set(str(math.tan(math.radians(val))))
                elif char == "log":
                    self.display_var.set(str(math.log10(val)))
                elif char == "ln":
                    self.display_var.set(str(math.log(val)))
            except Exception:
                self.display_var.set("Error")
            return

        # Pi
        if char == "π":
            self.display_var.set(str(math.pi))
            return

        # Backspace
        if char == '←':
            if current and current != "0":
                new = current[:-1]
                if new == "" or new == "-":
                    new = "0"
                self.display_var.set(new)
            return

        # Default: append character (numbers, operators, parentheses, dot)
        if current == "0":
            self.display_var.set(char)
        else:
            self.display_var.set(current + char)
    
    def calculate(self):
        try:
            expr = self.display_var.get()
            # replace unicode pi char if present
            expr = expr.replace('π', str(math.pi))
            # Evaluate - note: eval is used here; ensure only trusted input or extend parser
            result = eval(expr)
            self.display_var.set(str(result))
        except Exception:
            self.display_var.set("Error")

    def update_memory_label(self):
        if self.memory != 0:
            # Shorten display for label
            self.mem_label.config(text=f"M: {self.memory}")
        else:
            self.mem_label.config(text="")

    def on_key_press(self, event):
        # Map keys to actions
        key = event.char
        if not key:
            return
        if key.isdigit() or key in '.()+-*/':
            self.on_button_click(key)
        elif key == '\r' or key == '\n':
            self.on_button_click('=')
        elif key == '\x08':
            self.on_button_click('←')
        elif key.lower() == 'c':
            self.on_button_click('C')

if __name__ == "__main__":
    root = tk.Tk()
    calc = TI84Calculator(root)
    root.mainloop()
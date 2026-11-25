import tkinter as tk
from tkinter import messagebox


class SmartCPUSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart CPU Architecture Simulator V3.0")
        self.root.geometry("1250x850")
        self.root.configure(bg="#101827")

        self.program = []
        self.pc = 0
        self.registers = {f"R{i}": 0 for i in range(4)}
        self.memory = [0] * 8
        self.cycles = 0
        self.halted = False
        self.busy = False
        self.auto_run = False
        self.after_id = None
        self.current_instruction = ""

        self.create_ui()
        self.update_display()
        self.log("V3.0 Ready. Load your program.")

    def create_ui(self):
        tk.Label(
            self.root,
            text="SMART CPU ARCHITECTURE SIMULATOR",
            font=("Arial", 21, "bold"),
            bg="#101827", fg="#38bdf8"
        ).pack(pady=10)

        tk.Label(
            self.root,
            text="V3.0 | Animated Data Bus | CPU Datapath",
            font=("Arial", 11),
            bg="#101827", fg="white"
        ).pack()

        main = tk.Frame(self.root, bg="#101827")
        main.pack(fill="both", expand=True, padx=10, pady=10)

        left = tk.Frame(main, bg="#1e293b", width=280)
        left.pack(side="left", fill="y", padx=5)
        left.pack_propagate(False)

        tk.Label(
            left, text="PROGRAM EDITOR",
            font=("Arial", 13, "bold"),
            bg="#1e293b", fg="#38bdf8"
        ).pack(pady=8)

        self.editor = tk.Text(
            left, height=16,
            font=("Consolas", 12),
            bg="#0f172a", fg="white",
            insertbackground="white"
        )
        self.editor.pack(fill="x", padx=8)

        self.editor.insert(
            "1.0",
            "MOV R0, 10\n"
            "MOV R1, 5\n"
            "ADD R0, R1\n"
            "SUB R0, 2\n"
            "STORE R0, 0\n"
            "LOAD R2, 0\n"
            "HALT"
        )

        self.make_button(left, "START / RESET",
                         self.start, "#2563eb")
        self.make_button(left, "NEXT INSTRUCTION",
                         self.step, "#0891b2")
        self.make_button(left, "RUN ALL",
                         self.run_all, "#16a34a")
        self.make_button(left, "STOP RUN",
                         self.stop_run, "#dc2626")

        tk.Label(
            left,
            text="SUPPORTED INSTRUCTIONS\n\n"
                 "MOV R0, 10\n"
                 "ADD R0, R1\n"
                 "SUB R0, 2\n"
                 "LOAD R2, 0\n"
                 "STORE R0, 0\n"
                 "HALT",
            font=("Consolas", 10),
            bg="#1e293b", fg="white",
            justify="left"
        ).pack(anchor="w", padx=12, pady=12)

        right = tk.Frame(main, bg="#101827")
        right.pack(side="left", fill="both", expand=True, padx=5)

        # CPU DATAPATH
        cpu_box = tk.LabelFrame(
            right,
            text="CPU DATAPATH - ANIMATED DATA BUS",
            font=("Arial", 12, "bold"),
            bg="#1e293b", fg="#38bdf8"
        )
        cpu_box.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            cpu_box,
            height=330,
            bg="#0f172a",
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True, padx=5, pady=5)

        self.draw_datapath()

        # STATUS
        status_box = tk.Frame(right, bg="#1e293b")
        status_box.pack(fill="x", pady=5)

        self.phase = tk.StringVar(value="CPU STATUS: READY")
        tk.Label(
            status_box, textvariable=self.phase,
            font=("Arial", 13, "bold"),
            bg="#1e293b", fg="#facc15"
        ).pack(pady=5)

        self.info = tk.StringVar(value="Waiting for instruction")
        tk.Label(
            status_box, textvariable=self.info,
            font=("Arial", 10),
            bg="#1e293b", fg="white"
        ).pack(pady=4)

        # REGISTER AND MEMORY
        data = tk.Frame(right, bg="#101827")
        data.pack(fill="x", pady=5)

        reg_box = tk.LabelFrame(
            data, text="REGISTER BANK",
            bg="#1e293b", fg="#38bdf8"
        )
        reg_box.pack(side="left", fill="both", expand=True, padx=3)

        self.reg_text = tk.StringVar()
        tk.Label(
            reg_box, textvariable=self.reg_text,
            font=("Consolas", 12, "bold"),
            bg="#1e293b", fg="#4ade80",
            justify="left"
        ).pack(padx=15, pady=10)

        mem_box = tk.LabelFrame(
            data, text="MEMORY UNIT",
            bg="#1e293b", fg="#38bdf8"
        )
        mem_box.pack(side="left", fill="both", expand=True, padx=3)

        self.mem_text = tk.StringVar()
        tk.Label(
            mem_box, textvariable=self.mem_text,
            font=("Consolas", 10),
            bg="#1e293b", fg="#facc15",
            justify="left"
        ).pack(padx=10, pady=10)

        # ALU
        alu_box = tk.LabelFrame(
            right, text="ALU - ARITHMETIC LOGIC UNIT",
            bg="#1e293b", fg="#38bdf8"
        )
        alu_box.pack(fill="x", pady=5)

        self.alu_text = tk.StringVar(value="ALU: Waiting")
        tk.Label(
            alu_box, textvariable=self.alu_text,
            font=("Consolas", 12, "bold"),
            bg="#1e293b", fg="#fb923c"
        ).pack(pady=8)

        # TRACE
        trace_box = tk.LabelFrame(
            right, text="EXECUTION TRACE",
            bg="#1e293b", fg="#38bdf8"
        )
        trace_box.pack(fill="both", expand=True, pady=5)

        self.trace = tk.Text(
            trace_box, height=7,
            state="disabled",
            bg="#020617", fg="#4ade80",
            font=("Consolas", 10)
        )
        self.trace.pack(fill="both", expand=True, padx=5, pady=5)

    def make_button(self, parent, text, command, color):
        tk.Button(
            parent, text=text,
            command=command,
            bg=color, fg="white",
            font=("Arial", 10, "bold"),
            relief="flat", cursor="hand2"
        ).pack(fill="x", padx=10, pady=5, ipady=6)

    # DATAPATH DESIGN
    def draw_datapath(self):
        self.canvas.delete("all")

        positions = {
            "PC": (25, 45, 140, 105),
            "MEMORY": (195, 45, 335, 105),
            "IR": (390, 45, 510, 105),
            "CONTROL": (575, 45, 720, 105),
            "REG": (25, 205, 180, 270),
            "ALU": (275, 205, 425, 270),
            "OUTPUT": (525, 205, 665, 270)
        }

        labels = {
            "PC": "PROGRAM\nCOUNTER",
            "MEMORY": "MEMORY UNIT",
            "IR": "INSTRUCTION\nREGISTER",
            "CONTROL": "CONTROL UNIT",
            "REG": "REGISTER BANK",
            "ALU": "ALU",
            "OUTPUT": "OUTPUT"
        }

        self.blocks = {}

        for name, (x1, y1, x2, y2) in positions.items():
            rect = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill="#334155",
                outline="#64748b",
                width=2
            )

            self.canvas.create_text(
                (x1 + x2) / 2,
                (y1 + y2) / 2,
                text=labels[name],
                fill="white",
                font=("Arial", 10, "bold"),
                justify="center"
            )

            self.blocks[name] = rect

        arrows = [
            (140, 75, 195, 75),
            (335, 75, 390, 75),
            (510, 75, 575, 75),
            (265, 105, 265, 155),
            (265, 155, 100, 205),
            (265, 155, 350, 205),
            (180, 237, 275, 237),
            (425, 237, 525, 237)
        ]

        for x1, y1, x2, y2 in arrows:
            self.canvas.create_line(
                x1, y1, x2, y2,
                fill="#94a3b8",
                width=2,
                arrow=tk.LAST
            )

        self.canvas.create_text(
            360, 305,
            text="MOVING DATA BUS",
            fill="#38bdf8",
            font=("Arial", 11, "bold")
        )

        # Moving data particle
        self.dot = self.canvas.create_oval(
            0, 0, 14, 14,
            fill="#facc15",
            outline="white",
            width=2,
            state="hidden"
        )

    def highlight(self, name):
        for key, rect in self.blocks.items():
            self.canvas.itemconfig(
                rect, fill="#334155",
                outline="#64748b", width=2
            )

        if name in self.blocks:
            self.canvas.itemconfig(
                self.blocks[name],
                fill="#075985",
                outline="#38bdf8",
                width=3
            )

    # DATA BUS ANIMATION
    def animate_path(self, points, callback):
        self.canvas.itemconfig(self.dot, state="normal")
        self.move_segment(points, 0, 0, callback)

    def move_segment(self, points, segment, frame, callback):
        if segment >= len(points) - 1:
            self.canvas.itemconfig(self.dot, state="hidden")
            callback()
            return

        x1, y1 = points[segment]
        x2, y2 = points[segment + 1]

        total_frames = 14
        t = frame / total_frames

        x = x1 + (x2 - x1) * t
        y = y1 + (y2 - y1) * t

        self.canvas.coords(
            self.dot,
            x - 7, y - 7,
            x + 7, y + 7
        )

        if frame < total_frames:
            self.after_id = self.root.after(
                20,
                lambda: self.move_segment(
                    points, segment, frame + 1, callback
                )
            )
        else:
            self.after_id = self.root.after(
                20,
                lambda: self.move_segment(
                    points, segment + 1, 0, callback
                )
            )

    def get_path(self, stage):
        op = self.current_instruction.split()[0].upper()

        paths = {
            "FETCH": [
                (85, 75), (265, 75)
            ],
            "DECODE": [
                (265, 75), (450, 75), (650, 75)
            ]
        }

        if stage in paths:
            return paths[stage]

        if op in ("ADD", "SUB"):
            return [(100, 237), (350, 237), (595, 237)]

        if op == "LOAD":
            return [
                (265, 105), (265, 155), (100, 237)
            ]

        if op == "STORE":
            return [
                (100, 237), (265, 155), (265, 105)
            ]

        if op == "MOV":
            return [
                (650, 105), (650, 155), (100, 237)
            ]

        return [(650, 75), (595, 237)]

    # PROGRAM CONTROL
    def log(self, message):
        self.trace.config(state="normal")
        self.trace.insert("end", message + "\n")
        self.trace.see("end")
        self.trace.config(state="disabled")

    def start(self):
        self.stop_run()

        lines = self.editor.get("1.0", "end").splitlines()

        self.program = [
            line.split("#")[0].strip()
            for line in lines
            if line.split("#")[0].strip()
        ]

        if not self.program:
            messagebox.showwarning("Program", "Enter instructions.")
            return

        self.pc = 0
        self.registers = {f"R{i}": 0 for i in range(4)}
        self.memory = [0] * 8
        self.cycles = 0
        self.halted = False

        self.trace.config(state="normal")
        self.trace.delete("1.0", "end")
        self.trace.config(state="disabled")

        self.alu_text.set("ALU: Waiting")
        self.phase.set("CPU STATUS: READY")
        self.info.set("Program loaded successfully")

        self.highlight("PC")
        self.update_display()
        self.log("Program loaded successfully.")

    def value(self, operand):
        operand = operand.upper()

        if operand in self.registers:
            return self.registers[operand]

        return int(operand)

    def execute_instruction(self, instruction):
        parts = instruction.replace(",", " ").split()
        op = parts[0].upper()

        if op == "HALT" and len(parts) == 1:
            self.halted = True
            self.cycles += 1
            self.log("EXECUTE: CPU stopped.")
            return

        elif op == "MOV" and len(parts) == 3:
            dest = parts[1].upper()

            if dest not in self.registers:
                raise ValueError("Invalid register")

            self.registers[dest] = self.value(parts[2])

            self.log(f"MOV: {dest} = {self.registers[dest]}")

        elif op in ("ADD", "SUB") and len(parts) == 3:
            dest = parts[1].upper()

            if dest not in self.registers:
                raise ValueError("Invalid register")

            a = self.registers[dest]
            b = self.value(parts[2])

            result = a + b if op == "ADD" else a - b

            self.registers[dest] = result

            self.alu_text.set(
                f"ALU: {a} {op} {b} = {result}"
            )

            self.log(f"ALU RESULT: {result}")

        elif op == "STORE" and len(parts) == 3:
            source = parts[1].upper()
            address = int(parts[2])

            if source not in self.registers:
                raise ValueError("Invalid register")

            if not 0 <= address < 8:
                raise ValueError("Address must be 0-7")

            self.memory[address] = self.registers[source]

            self.log(
                f"MEMORY WRITE: M[{address}] = "
                f"{self.memory[address]}"
            )

        elif op == "LOAD" and len(parts) == 3:
            dest = parts[1].upper()
            address = int(parts[2])

            if dest not in self.registers:
                raise ValueError("Invalid register")

            if not 0 <= address < 8:
                raise ValueError("Address must be 0-7")

            self.registers[dest] = self.memory[address]

            self.log(
                f"MEMORY READ: {dest} = M[{address}]"
            )

        else:
            raise ValueError(
                f"Invalid instruction: {instruction}"
            )

        self.cycles += 1

    # FETCH DECODE EXECUTE
    def step(self):
        self.auto_run = False
        self.begin_instruction()

    def begin_instruction(self):
        if not self.program:
            messagebox.showinfo("Notice", "Click START / RESET first.")
            return

        if self.busy:
            return

        if self.halted or self.pc >= len(self.program):
            self.phase.set("CPU STATUS: COMPLETED")
            self.info.set("Program has finished.")
            self.auto_run = False
            return

        self.current_instruction = self.program[self.pc]
        self.busy = True

        self.log(f"\nPC {self.pc}: {self.current_instruction}")

        self.animate_stage(0)

    def animate_stage(self, stage):
        stages = ["FETCH", "DECODE", "EXECUTE"]

        if stage >= len(stages):
            self.finish_instruction()
            return

        name = stages[stage]

        self.phase.set(f"CPU STATUS: {name}")
        self.info.set(
            f"{name}: {self.current_instruction}"
        )

        if name == "FETCH":
            self.highlight("PC")
        elif name == "DECODE":
            self.highlight("IR")
        else:
            op = self.current_instruction.split()[0].upper()

            if op in ("ADD", "SUB"):
                self.highlight("ALU")
            elif op in ("LOAD", "STORE"):
                self.highlight("MEMORY")
            else:
                self.highlight("CONTROL")

        self.log(f"{name}: {self.current_instruction}")

        path = self.get_path(name)

        self.animate_path(
            path,
            lambda: self.animate_stage(stage + 1)
        )

    def finish_instruction(self):
        try:
            self.execute_instruction(self.current_instruction)

            self.pc += 1
            self.update_display()

            self.busy = False
            self.highlight("OUTPUT")

            if self.halted:
                self.phase.set("CPU STATUS: HALTED")
                self.info.set("Program completed successfully")
                self.log("PROGRAM COMPLETED.")
                self.auto_run = False

            else:
                self.phase.set("CPU STATUS: INSTRUCTION COMPLETED")
                self.info.set(f"Next PC = {self.pc}")

                if self.auto_run:
                    self.after_id = self.root.after(
                        350, self.begin_instruction
                    )

        except (ValueError, IndexError) as error:
            self.busy = False
            self.halted = True
            self.auto_run = False

            self.phase.set("CPU STATUS: ERROR")
            self.info.set(str(error))
            self.log(f"ERROR: {error}")

            messagebox.showerror("Execution Error", str(error))

    def run_all(self):
        if not self.program:
            self.start()

        if self.program and not self.halted and not self.busy:
            self.auto_run = True
            self.begin_instruction()

    def stop_run(self):
        self.auto_run = False

        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.busy = False

        if hasattr(self, "dot"):
            self.canvas.itemconfig(self.dot, state="hidden")

        if hasattr(self, "phase"):
            self.phase.set("CPU STATUS: STOPPED")

    def update_display(self):
        self.reg_text.set(
            "\n".join(
                f"{name} = {value}"
                for name, value in self.registers.items()
            )
            + f"\nPC = {self.pc}"
            + f"\nCycles = {self.cycles}"
        )

        self.mem_text.set(
            "\n".join(
                f"M[{i}] = {value}"
                for i, value in enumerate(self.memory)
            )
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = SmartCPUSimulator(root)
    root.mainloop()
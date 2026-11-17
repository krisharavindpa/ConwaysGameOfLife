import tkinter as tk
from tkinter import messagebox

class GameOfLife:
    def __init__(self, root):
        self.root = root
        self.root.title("Conway's Game of Life - Custom Rules")
        self.running = False
        self.cell_size = 8  # Smaller cell size to fit 100x100 on screen
        self.tick_count = 0

        # --- Top UI Controls ---
        # Added fill=tk.X so the frame spans the whole width, allowing right-alignment
        control_frame = tk.Frame(root)
        control_frame.pack(pady=5, fill=tk.X, padx=10)

        tk.Label(control_frame, text="Rule (B/S):").pack(side=tk.LEFT)
        self.rule_entry = tk.Entry(control_frame, width=8)
        self.rule_entry.insert(0, "B3/S23")
        self.rule_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(control_frame, text="Rows:").pack(side=tk.LEFT)
        self.row_entry = tk.Entry(control_frame, width=5)
        self.row_entry.insert(0, "100")
        self.row_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(control_frame, text="Cols:").pack(side=tk.LEFT)
        self.col_entry = tk.Entry(control_frame, width=5)
        self.col_entry.insert(0, "100")
        self.col_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(control_frame, text="Apply & Reset", command=self.apply_and_reset, bg="lightyellow").pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Play", command=self.play, bg="lightgreen").pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Stop", command=self.stop, bg="lightcoral").pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Clear", command=self.clear).pack(side=tk.LEFT, padx=5)

        # Tick Counter (Aligned to the right)
        self.tick_var = tk.StringVar(value="Ticks: 0")
        tk.Label(control_frame, textvariable=self.tick_var, font=("Arial", 10, "bold"), fg="blue").pack(side=tk.RIGHT, padx=10)

        # Container for the canvas so we can destroy and recreate it on resize
        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(pady=10)
        self.canvas = None

        # Initialize the first 100x100 grid
        self.apply_and_reset()

    def parse_rules(self):
        """Extracts the Born and Survive numbers from the B/S string."""
        rule_str = self.rule_entry.get().upper().strip()
        born, survive = set(), set()
        
        try:
            parts = rule_str.split('/')
            for p in parts:
                if p.startswith('B'):
                    born = {int(char) for char in p[1:]}
                elif p.startswith('S'):
                    survive = {int(char) for char in p[1:]}
            return born, survive
        except Exception:
            messagebox.showwarning("Rule Error", "Invalid rule format. Using default B3/S23.")
            return {3}, {2, 3}

    def apply_and_reset(self):
        """Reads settings, resizes the grid, applies rules, and spawns the Glider Gun."""
        self.running = False
        self.tick_count = 0
        self.tick_var.set(f"Ticks: {self.tick_count}")
        self.born_rules, self.survive_rules = self.parse_rules()

        try:
            self.rows = int(self.row_entry.get())
            self.cols = int(self.col_entry.get())
        except ValueError:
            self.rows, self.cols = 100, 100

        # Destroy old canvas if it exists
        if self.canvas:
            self.canvas.destroy()

        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.rects = [[None for _ in range(self.cols)] for _ in range(self.rows)]

        self.canvas = tk.Canvas(self.canvas_frame, width=self.cols * self.cell_size, height=self.rows * self.cell_size, bg="white")
        self.canvas.pack()
        
        # Bind clicking AND dragging to draw cells easily
        self.canvas.bind("<Button-1>", self.draw_cell)
        self.canvas.bind("<B1-Motion>", self.draw_cell)

        self.draw_initial_grid()
        self.spawn_glider_gun()
        self.update_visuals()

    def draw_initial_grid(self):
        """Draws the initial grid lines and rectangles."""
        for r in range(self.rows):
            for c in range(self.cols):
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="#e0e0e0")
                self.rects[r][c] = rect_id

    def spawn_glider_gun(self):
        """Spawns the famous Gosper Glider Gun near the top left."""
        gun_coords = [
            (5, 1), (5, 2), (6, 1), (6, 2), 
            (5, 11), (6, 11), (7, 11), (4, 12), (8, 12), (3, 13), (9, 13), 
            (3, 14), (9, 14), (6, 15), (4, 16), (8, 16), (5, 17), (6, 17), (7, 17), (6, 18), 
            (3, 21), (4, 21), (5, 21), (3, 22), (4, 22), (5, 22), (2, 23), (6, 23), 
            (1, 25), (2, 25), (6, 25), (7, 25), 
            (3, 35), (4, 35), (3, 36), (4, 36)
        ]
        
        row_offset = 5
        col_offset = 5

        for r, c in gun_coords:
            tr = r + row_offset
            tc = c + col_offset
            if 0 <= tr < self.rows and 0 <= tc < self.cols:
                self.grid[tr][tc] = 1

    def draw_cell(self, event):
        """Allows user to click or drag to turn cells alive."""
        c = event.x // self.cell_size
        r = event.y // self.cell_size
        if 0 <= r < self.rows and 0 <= c < self.cols:
            self.grid[r][c] = 1
            self.canvas.itemconfig(self.rects[r][c], fill="black")

    def play(self):
        if not self.running:
            self.running = True
            self.run_simulation()

    def stop(self):
        self.running = False

    def clear(self):
        """Empties the grid completely and resets tick counter."""
        self.running = False
        self.tick_count = 0
        self.tick_var.set(f"Ticks: {self.tick_count}")
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.update_visuals()

    def run_simulation(self):
        if self.running:
            self.next_generation()
            self.root.after(100, self.run_simulation)

    def next_generation(self):
        """Calculates the next grid state and increments the tick counter."""
        new_grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

        for r in range(self.rows):
            for c in range(self.cols):
                neighbors = self.count_neighbors(r, c)

                if self.grid[r][c] == 1:
                    new_grid[r][c] = 1 if neighbors in self.survive_rules else 0
                else:
                    new_grid[r][c] = 1 if neighbors in self.born_rules else 0

        self.grid = new_grid
        self.update_visuals()
        
        # Increment and update tick counter
        self.tick_count += 1
        self.tick_var.set(f"Ticks: {self.tick_count}")

    def count_neighbors(self, r, c):
        count = 0
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if i == 0 and j == 0:
                    continue
                nr, nc = r + i, c + j
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    count += self.grid[nr][nc]
        return count

    def update_visuals(self):
        for r in range(self.rows):
            for c in range(self.cols):
                color = "black" if self.grid[r][c] == 1 else "white"
                self.canvas.itemconfig(self.rects[r][c], fill=color)

if __name__ == "__main__":
    root = tk.Tk()
    app = GameOfLife(root)
    root.mainloop()
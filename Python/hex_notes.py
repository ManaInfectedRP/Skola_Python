
# pip install pyinstaller
# pyinstaller --onefile --windowed hex_notes.py

import sqlite3
import tkinter as tk
from tkinter import Toplevel, Label, Entry, Button, Text, Scrollbar, colorchooser, messagebox
from datetime import datetime
import math

# --- Database Setup ---
DB_FILE = "hex_notes.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hex_data (
            q INTEGER,
            r INTEGER,
            title TEXT,
            date TEXT,
            text TEXT,
            color TEXT,
            PRIMARY KEY (q, r)
        )
    ''')
    conn.commit()
    conn.close()

# --- Hex Grid Utilities ---
HEX_SIZE = 40
WIDTH = 800
HEIGHT = 600

def hex_to_pixel(q, r):
    x = HEX_SIZE * 3/2 * q
    y = HEX_SIZE * math.sqrt(3) * (r + q / 2)
    return x, y

def polygon_corners(x, y):
    corners = []
    for i in range(6):
        angle = math.radians(60 * i)
        cx = x + HEX_SIZE * math.cos(angle)
        cy = y + HEX_SIZE * math.sin(angle)
        corners.append((cx, cy))
    return corners

def axial_range(radius):
    for q in range(-radius, radius + 1):
        r1 = max(-radius, -q - radius)
        r2 = min(radius, -q + radius)
        for r in range(r1, r2 + 1):
            yield (q, r)

def shorten_text(text, max_length=12):
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

class HexApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hex Notes")
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="white")
        self.canvas.pack()

        self.offset_x = 0
        self.offset_y = 0
        self.dragging = False
        self.last_drag_x = 0
        self.last_drag_y = 0

        self.zoom = 1.0

        self.hexes = {}
        self.labels = {}
        self.tooltips = {}
        self.data = {}

        self.load_data()
        self.draw_grid()

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<ButtonPress-2>", self.start_pan)
        self.canvas.bind("<B2-Motion>", self.do_pan)
        self.canvas.bind("<ButtonRelease-2>", self.end_pan)
        self.canvas.bind("<Shift-ButtonPress-1>", self.start_pan)
        self.canvas.bind("<Shift-B1-Motion>", self.do_pan)
        self.canvas.bind("<Shift-ButtonRelease-1>", self.end_pan)
        self.canvas.bind("<MouseWheel>", self.on_zoom)
        self.canvas.bind("<Motion>", self.on_hover)

        clear_btn = Button(root, text="Töm hela databasen", command=self.clear_database)
        clear_btn.pack(pady=5)
    
    def draw_grid(self):
        self.canvas.delete("all")
        self.hexes.clear()
        self.labels.clear()
        self.tooltips.clear()

        for q, r in axial_range(15):
            px, py = hex_to_pixel(q, r)
            x = px * self.zoom + WIDTH // 2 + self.offset_x
            y = py * self.zoom + HEIGHT // 2 + self.offset_y
            corners = polygon_corners(x, y)
            flat_corners = [coord for corner in corners for coord in corner]
            color = self.data.get((q, r), {}).get("color", "#ffffff")
            hex_id = self.canvas.create_polygon(flat_corners, fill=color, outline="black")
            self.hexes[(q, r)] = hex_id

            title = self.data.get((q, r), {}).get("title", "")
            date = self.data.get((q, r), {}).get("date", "")
            if title:
                display_title = shorten_text(title, max_length=12)
                text_id = self.canvas.create_text(x, y - 8, text=display_title, font=("Helvetica", 10, "bold"))
                self.labels[(q, r)] = text_id
                self.tooltips[text_id] = title
            if date:
                self.canvas.create_text(x, y + 8, text=date, font=("Helvetica", 8), fill="gray")

    def on_hover(self, event):
        x, y = event.x, event.y
        for text_id, full_text in self.tooltips.items():
            bbox = self.canvas.bbox(text_id)
            if bbox and bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]:
                self.canvas.itemconfig(text_id, text=full_text)
            else:
                self.canvas.itemconfig(text_id, text=shorten_text(full_text))

    def on_zoom(self, event):
        if event.delta > 0:
            self.zoom *= 1.1
        else:
            self.zoom /= 1.1
        self.draw_grid()

    def on_click(self, event):
        q, r = self.pixel_to_axial(event.x, event.y)
        if (q, r) in self.hexes:
            self.open_editor(q, r)

    def pixel_to_axial(self, x, y):
        px = (x - WIDTH // 2 - self.offset_x) / self.zoom
        py = (y - HEIGHT // 2 - self.offset_y) / self.zoom

        q = (2/3 * px) / HEX_SIZE
        r = (-1/3 * px + math.sqrt(3)/3 * py) / HEX_SIZE

        return self.hex_round(q, r)

    def hex_round(self, q, r):
        x = q
        z = r
        y = -x - z

        rx = round(x)
        ry = round(y)
        rz = round(z)

        x_diff = abs(rx - x)
        y_diff = abs(ry - y)
        z_diff = abs(rz - z)

        if x_diff > y_diff and x_diff > z_diff:
            rx = -ry - rz
        elif y_diff > z_diff:
            ry = -rx - rz
        else:
            rz = -rx - ry

        return int(rx), int(rz)

    def start_pan(self, event):
        self.dragging = True
        self.last_drag_x = event.x
        self.last_drag_y = event.y

    def do_pan(self, event):
        if self.dragging:
            dx = event.x - self.last_drag_x
            dy = event.y - self.last_drag_y
            self.offset_x += dx
            self.offset_y += dy
            self.last_drag_x = event.x
            self.last_drag_y = event.y
            self.draw_grid()

    def end_pan(self, event):
        self.dragging = False

    def open_editor(self, q, r):
        existing = self.data.get((q, r), {})
        default_date = datetime.now().strftime("%Y-%m-%d")

        editor = Toplevel(self.root)
        editor.title(f"Edit Hex ({q}, {r})")
        editor.geometry("400x300")
        editor.minsize(300, 200)

        editor.grid_rowconfigure(2, weight=1)
        editor.grid_columnconfigure(1, weight=1)

        Label(editor, text="Title:").grid(row=0, column=0, sticky="e")
        title_entry = Entry(editor)
        title_entry.insert(0, existing.get("title", ""))
        title_entry.grid(row=0, column=1, sticky="ew")

        Label(editor, text="Date:").grid(row=1, column=0, sticky="e")
        date_entry = Entry(editor)
        date_entry.insert(0, existing.get("date", default_date))
        date_entry.grid(row=1, column=1, sticky="ew")

        Label(editor, text="Text:").grid(row=2, column=0, sticky="ne")
        text_frame = tk.Frame(editor)
        text_frame.grid(row=2, column=1, sticky="nsew")
        text_box = Text(text_frame, wrap="word")
        text_box.insert("1.0", existing.get("text", ""))
        scrollbar = Scrollbar(text_frame, command=text_box.yview)
        text_box.configure(yscrollcommand=scrollbar.set)
        text_box.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        initial_color = existing.get("color", "#ffffff")
        color_btn = Button(editor, text="Choose Color", bg=initial_color)
        color_btn.grid(row=3, column=1, sticky="w", pady=5)

        def choose_color():
            color = colorchooser.askcolor(title="Choose color", initialcolor=color_btn["bg"])[1]
            if color:
                color_btn.config(bg=color)
        color_btn.config(command=choose_color)

        def clear():
            if (q, r) in self.data:
                del self.data[(q, r)]
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM hex_data WHERE q=? AND r=?", (q, r))
            conn.commit()
            conn.close()
            self.draw_grid()
            editor.destroy()

        clear_btn = Button(editor, text="Töm ruta", command=clear)
        clear_btn.grid(row=4, column=0, sticky="w", pady=5, padx=5)

        def save():
            title = title_entry.get()
            date = date_entry.get()
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Fel", "Datumformatet ska vara YYYY-MM-DD")
                return

            text = text_box.get("1.0", "end-1c")
            color = color_btn["bg"] or "#ffffff"

            self.data[(q, r)] = {
                "title": title,
                "date": date,
                "text": text,
                "color": color
            }
            self.save_data(q, r)
            self.draw_grid()
            editor.destroy()

        Button(editor, text="Save", command=save).grid(row=4, column=1, sticky="e", pady=5)

    def save_data(self, q, r):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        d = self.data[(q, r)]
        cursor.execute('''
            INSERT INTO hex_data (q, r, title, date, text, color)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(q, r) DO UPDATE SET
                title=excluded.title,
                date=excluded.date,
                text=excluded.text,
                color=excluded.color
        ''', (q, r, d["title"], d["date"], d["text"], d["color"]))
        conn.commit()
        conn.close()

    def load_data(self):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT q, r, title, date, text, color FROM hex_data")
        for q, r, title, date, text, color in cursor.fetchall():
            self.data[(q, r)] = {
                "title": title,
                "date": date,
                "text": text,
                "color": color
            }
        conn.close()

    def clear_database(self):
        if tk.messagebox.askyesno("Bekräfta", "Vill du verkligen tömma hela databasen?"):
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM hex_data")
            conn.commit()
            conn.close()
            self.data.clear()
            self.draw_grid()

# --- Main ---
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = HexApp(root)
    root.mainloop()

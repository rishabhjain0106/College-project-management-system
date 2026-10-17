# cyberpunk_theme.py
import tkinter as tk
from tkinter import ttk

CYBER_BG = "#000b18"
NEON_PINK = "#ff2eea"
NEON_CYAN = "#29ffff"
NEON_GREEN = "#39ff14"
NEON_YELLOW = "#faff00"
NEON_ORANGE = "#ff9d00"

def apply_cyberpunk_style(root):
    style = ttk.Style()
    root.configure(bg=CYBER_BG)

    style.configure("Cyber.TFrame", background=CYBER_BG)
    style.configure("Cyber.TLabel", background=CYBER_BG, foreground=NEON_CYAN, font=("Consolas", 12))
    style.configure("CyberTitle.TLabel", background=CYBER_BG, foreground=NEON_PINK, font=("Consolas", 20, "bold"))
    style.configure("CyberButton.TButton",
                    font=("Consolas", 12, "bold"),
                    padding=6,
                    foreground=NEON_GREEN,
                    borderwidth=2)

def neon_label(parent, text, color=NEON_CYAN, size=12):
    return tk.Label(parent, text=text, fg=color, bg=CYBER_BG, font=("Consolas", size))

def neon_entry(parent, width=30):
    entry = tk.Entry(parent, bg="#001124", fg=NEON_GREEN,
                     insertbackground=NEON_GREEN, width=width,
                     highlightbackground=NEON_PINK,
                     highlightcolor=NEON_PINK,
                     highlightthickness=2,
                     font=("Consolas", 12))
    return entry

def neon_button(parent, text, cmd):
    return tk.Button(parent, text=text, command=cmd,
                     bg="#001f33", fg=NEON_YELLOW,
                     activeforeground=NEON_ORANGE,
                     activebackground="#002f44",
                     highlightthickness=2,
                     highlightcolor=NEON_PINK,
                     font=("Consolas", 12, "bold"))

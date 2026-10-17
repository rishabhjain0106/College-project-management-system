# screens/login_screen.py
import tkinter as tk
from cyberpunk_theme import *
from auth import authenticate
from screens.team_screen import TeamScreen
from screens.mentor_screen import MentorScreen
from screens.evaluator_screen import EvaluatorScreen

class LoginScreen:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(root, bg=CYBER_BG)
        self.frame.pack(fill="both", expand=True)

        neon_label(self.frame, "CPMS // CYBERPUNK LOGIN", NEON_PINK, 22).pack(pady=20)

        neon_label(self.frame, "Select Role:", NEON_CYAN).pack(pady=5)
        self.role_var = tk.StringVar(value="team")
        tk.OptionMenu(self.frame, self.role_var, "team", "mentor", "evaluator").pack()

        neon_label(self.frame, "User ID:", NEON_CYAN).pack(pady=10)
        self.entry_id = neon_entry(self.frame); self.entry_id.pack()

        neon_label(self.frame, "Password:", NEON_CYAN).pack(pady=10)
        self.entry_pw = neon_entry(self.frame); self.entry_pw.pack()
        self.entry_pw.config(show="●")

        neon_button(self.frame, "LOGIN", self.try_login).pack(pady=20)

        self.message = neon_label(self.frame, "", NEON_ORANGE)
        self.message.pack(pady=5)

    def try_login(self):
        uid = self.entry_id.get().strip()
        pw = self.entry_pw.get().strip()
        role = self.role_var.get()

        ok, name = authenticate(uid, pw, role)

        if not ok:
            self.message.config(text="Invalid ID or Password!", fg=NEON_ORANGE)
            return

        self.frame.destroy()

        if role == "team":
            TeamScreen(self.root, uid)
        elif role == "mentor":
            MentorScreen(self.root, name)
        elif role == "evaluator":
            EvaluatorScreen(self.root, uid)

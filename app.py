# app.py
import tkinter as tk
from cyberpunk_theme import apply_cyberpunk_style
from screens.login_screen import LoginScreen

def main():
    root = tk.Tk()
    root.title("CPMS - Cyberpunk Edition")
    root.geometry("900x600")

    apply_cyberpunk_style(root)

    LoginScreen(root)

    root.mainloop()

if __name__ == "__main__":
    main()

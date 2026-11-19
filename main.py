import customtkinter as ctk
from ui import AplicacioDuplicatsUI

def main():
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = AplicacioDuplicatsUI()
    app.mainloop()

if __name__ == "__main__":
    main()

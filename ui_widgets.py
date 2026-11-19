import os
import customtkinter as ctk
from PIL import Image, ImageOps
from config import MIDA_MINIATURA
from file_manager import formatar_mida

class TargetaImatge(ctk.CTkFrame):
    def __init__(self, parent, titol, color_vora, color_text):
        super().__init__(parent, corner_radius=10, border_width=2, border_color=color_vora)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._imatge_actual = None

        ctk.CTkLabel(
            self, text=titol, text_color=color_text,
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, pady=(8, 2))

        self.lbl_img = ctk.CTkLabel(self, text="Sense imatge")
        self.lbl_img.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        self.lbl_info = ctk.CTkLabel(self, text="-", justify="left", font=ctk.CTkFont(size=12))
        self.lbl_info.grid(row=2, column=0, padx=12, pady=(2, 10), sticky="w")

    def actualitzar(self, info_fitxer):
        ruta = info_fitxer['ruta']
        try:
            img_oberta = Image.open(ruta)
            img = ImageOps.exif_transpose(img_oberta).copy()
            img_oberta.close()

            img.thumbnail(MIDA_MINIATURA, Image.Resampling.LANCZOS)
            self._imatge_actual = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            self.lbl_img.configure(image=self._imatge_actual, text="")
        except Exception:
            self._imatge_actual = None
            self.lbl_img.configure(image="", text="Error carregant vista prèvia")

        text_info = (
            f"Fitxer: {info_fitxer['nom']}\n"
            f"Resolució: {info_fitxer['res']}  |  Pes: {formatar_mida(info_fitxer['pes'])}\n"
            f"Carpeta: {os.path.dirname(ruta)}"
        )
        self.lbl_info.configure(text=text_info)

    def netejar(self, missatge="Completat"):
        self._imatge_actual = None
        self.lbl_img.configure(image="", text=missatge)
        self.lbl_info.configure(text="-")

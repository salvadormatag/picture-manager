import os
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
from config import LLINDAR_PER_DEFECTE

class PanellConfiguracio(ctk.CTkFrame):
    def __init__(self, parent, on_escanejar):
        super().__init__(parent, corner_radius=12)
        self.grid_columnconfigure((0, 1), weight=1)
        self.carpetes_origen = []
        self.carpeta_desti = tk.StringVar()
        self.detectar_similars = tk.BooleanVar(value=True)
        self.llindar_similitud = tk.IntVar(value=LLINDAR_PER_DEFECTE)

        # Esquerra: Directoris origen
        f_orig = ctk.CTkFrame(self, fg_color="transparent")
        f_orig.grid(row=0, column=0, padx=12, pady=10, sticky="nsew")
        ctk.CTkLabel(f_orig, text="Directoris a revisar:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w")

        self.caixa = ctk.CTkTextbox(f_orig, height=65, corner_radius=8, state="disabled")
        self.caixa.pack(fill="x", pady=5)

        b_orig = ctk.CTkFrame(f_orig, fg_color="transparent")
        b_orig.pack(fill="x")
        ctk.CTkButton(b_orig, text="+ Afegir carpeta", width=130, height=28, command=self._afegir).pack(side="left", padx=(0, 5))
        ctk.CTkButton(b_orig, text="Netejar llista", width=100, height=28, fg_color="#555555", command=self._netejar).pack(side="left")

        # Dreta: Destí i paràmetres
        f_dest = ctk.CTkFrame(self, fg_color="transparent")
        f_dest.grid(row=0, column=1, padx=12, pady=10, sticky="nsew")
        ctk.CTkLabel(f_dest, text="Carpeta de destinació per als duplicats:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w")

        fila_d = ctk.CTkFrame(f_dest, fg_color="transparent")
        fila_d.pack(fill="x", pady=(5, 8))
        ctk.CTkEntry(fila_d, textvariable=self.carpeta_desti, placeholder_text="Selecciona on moure els repetits...").pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(fila_d, text="Triar...", width=75, command=self._triar_desti).pack(side="right")

        fila_o = ctk.CTkFrame(f_dest, fg_color="transparent")
        fila_o.pack(fill="x", pady=(2, 5))
        ctk.CTkCheckBox(fila_o, text="Detectar similars (WhatsApp/redimensionades)", variable=self.detectar_similars).pack(side="left")
        ctk.CTkLabel(fila_o, text="Tolerància:").pack(side="left", padx=(15, 5))
        ctk.CTkSlider(fila_o, from_=0, to=10, number_of_steps=10, width=90, variable=self.llindar_similitud,
                      command=lambda v: self.lbl_tol.configure(text=str(int(v)))).pack(side="left")
        self.lbl_tol = ctk.CTkLabel(fila_o, text=str(LLINDAR_PER_DEFECTE), width=20)
        self.lbl_tol.pack(side="left", padx=3)

        self.btn_escanejar = ctk.CTkButton(f_dest, text="INICIAR ESCANEIG", height=34, font=ctk.CTkFont(size=13, weight="bold"), command=on_escanejar)
        self.btn_escanejar.pack(fill="x", pady=(4, 0))

    def _afegir(self):
        ruta = filedialog.askdirectory(title="Selecciona una carpeta amb imatges")
        if ruta and ruta not in self.carpetes_origen:
            self.carpetes_origen.append(ruta)
            self._refrescar()
            if not self.carpeta_desti.get():
                self.carpeta_desti.set(os.path.join(ruta, "_DUPLICATS_REVISAR"))

    def _netejar(self):
        self.carpetes_origen.clear()
        self._refrescar()

    def _refrescar(self):
        self.caixa.configure(state="normal")
        self.caixa.delete("1.0", "end")
        for c in self.carpetes_origen:
            self.caixa.insert("end", f"- {c}\n")
        self.caixa.configure(state="disabled")

    def _triar_desti(self):
        ruta = filedialog.askdirectory(title="Selecciona on moure els duplicats")
        if ruta:
            self.carpeta_desti.set(ruta)


class PanellAccions(ctk.CTkFrame):
    def __init__(self, parent, on_decidir, on_desfer, on_moure_tots):
        super().__init__(parent, corner_radius=12)
        self.btn_dreta = ctk.CTkButton(self, text="Moure el duplicat [Dreta]", fg_color="#d32f2f", hover_color="#b71c1c", height=38, font=ctk.CTkFont(weight="bold"), state="disabled", command=lambda: on_decidir("dreta"))
        self.btn_dreta.pack(side="left", padx=(12, 6), pady=10)

        self.btn_esq = ctk.CTkButton(self, text="Moure l'original [Esq]", fg_color="#ed6c02", hover_color="#e65100", height=38, state="disabled", command=lambda: on_decidir("esquerra"))
        self.btn_esq.pack(side="left", padx=6, pady=10)

        self.btn_ignorar = ctk.CTkButton(self, text="Ignorar [Espai]", fg_color="#555555", height=38, state="disabled", command=lambda: on_decidir("ignorar"))
        self.btn_ignorar.pack(side="left", padx=6, pady=10)

        self.btn_desfer = ctk.CTkButton(self, text="↩ Desfer [Ctrl+Z]", fg_color="#0288d1", hover_color="#01579b", height=38, state="disabled", command=on_desfer)
        self.btn_desfer.pack(side="left", padx=6, pady=10)

        self.btn_auto = ctk.CTkButton(self, text="Moure TOTS els restants", fg_color="#2e7d32", hover_color="#1b5e20", height=38, font=ctk.CTkFont(weight="bold"), state="disabled", command=on_moure_tots)
        self.btn_auto.pack(side="right", padx=12, pady=10)

    def activar(self, actiu):
        estat = "normal" if actiu else "disabled"
        for btn in (self.btn_dreta, self.btn_esq, self.btn_ignorar, self.btn_auto):
            btn.configure(state=estat)

    def activar_desfer(self, actiu):
        self.btn_desfer.configure(state="normal" if actiu else "disabled")

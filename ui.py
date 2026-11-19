import threading
import queue
import traceback
from tkinter import messagebox
import customtkinter as ctk

from file_manager import formatar_mida, moure_fitxer_segur
from scanner import buscar_duplicats
from history import HistorialAccions
from ui_widgets import TargetaImatge
from ui_panels import PanellConfiguracio, PanellAccions

class AplicacioDuplicatsUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PhotoDeduper Pro — Gestor Visual de Duplicats")
        self.geometry("1180x780")
        self.minsize(1020, 680)

        self.historial = HistorialAccions()
        self.parelles_pendents = []
        self.index_actual = 0
        self.moguts_comptador = 0
        self.espai_estalviat = 0
        self.cua_fil = queue.Queue()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.panell_sup = PanellConfiguracio(self, self._iniciar_escaneig)
        self.panell_sup.grid(row=0, column=0, padx=15, pady=(15, 8), sticky="ew")

        visor = ctk.CTkFrame(self, corner_radius=12)
        visor.grid(row=1, column=0, padx=15, pady=5, sticky="nsew")
        visor.grid_columnconfigure((0, 1), weight=1)
        visor.grid_rowconfigure(1, weight=1)

        barra = ctk.CTkFrame(visor, fg_color="transparent")
        barra.grid(row=0, column=0, columnspan=2, padx=15, pady=(10, 5), sticky="ew")
        self.lbl_estat = ctk.CTkLabel(barra, text="Afegeix almenys una carpeta i prem 'Iniciar Escaneig'.", font=ctk.CTkFont(size=13))
        self.lbl_estat.pack(side="left")
        self.progres = ctk.CTkProgressBar(barra, width=250)
        self.progres.pack(side="right")
        self.progres.set(0)

        self.card_esq = TargetaImatge(visor, "ORIGINAL RECOMANAT (CONSERVAR)", "#2e7d32", "#4caf50")
        self.card_esq.grid(row=1, column=0, padx=(12, 6), pady=10, sticky="nsew")
        self.card_dreta = TargetaImatge(visor, "DUPLICAT DETECTAT (MOURE)", "#c62828", "#ef5350")
        self.card_dreta.grid(row=1, column=1, padx=(6, 12), pady=10, sticky="nsew")

        self.panell_inf = PanellAccions(self, self._decidir, self._desfer_accio, self._moure_tots)
        self.panell_inf.grid(row=2, column=0, padx=15, pady=(5, 15), sticky="ew")

        self.bind("<Right>", lambda e: self._decidir("dreta") if self.panell_inf.btn_dreta.cget("state") == "normal" else None)
        self.bind("<Left>", lambda e: self._decidir("esquerra") if self.panell_inf.btn_esq.cget("state") == "normal" else None)
        self.bind("<space>", lambda e: self._decidir("ignorar") if self.panell_inf.btn_ignorar.cget("state") == "normal" else None)
        self.bind("<Control-z>", lambda e: self._desfer_accio() if self.historial.te_accions() else None)
        self.bind("<Control-Z>", lambda e: self._desfer_accio() if self.historial.te_accions() else None)

    def _iniciar_escaneig(self):
        if not self.panell_sup.carpetes_origen or not self.panell_sup.carpeta_desti.get():
            messagebox.showwarning("Atenció", "Selecciona almenys una carpeta d'origen i una de destinació.")
            return

        self.panell_sup.btn_escanejar.configure(state="disabled")
        self.panell_inf.activar(False)
        self.panell_inf.activar_desfer(False)
        self.historial = HistorialAccions()
        self.parelles_pendents, self.index_actual, self.moguts_comptador, self.espai_estalviat = [], 0, 0, 0
        self.progres.set(0)
        self.lbl_estat.configure(text="Analitzant imatges... Això pot trigar uns segons.")

        carpetes = list(self.panell_sup.carpetes_origen)
        desti = self.panell_sup.carpeta_desti.get()
        similars = self.panell_sup.detectar_similars.get()
        llindar = int(self.panell_sup.llindar_similitud.get())

        threading.Thread(
            target=self._fil_escaneig,
            args=(carpetes, desti, similars, llindar),
            daemon=True
        ).start()
        self.after(100, self._comprovar_cua)

    def _fil_escaneig(self, carpetes, desti, similars, llindar):
        try:
            resultats = buscar_duplicats(
                carpetes, desti, similars, llindar,
                callback_progres=lambda v: self.cua_fil.put(("progres", v))
            )
            self.cua_fil.put(("fet", resultats))
        except Exception:
            self.cua_fil.put(("error", traceback.format_exc()))

    def _comprovar_cua(self):
        try:
            while True:
                tipus, dades = self.cua_fil.get_nowait()
                if tipus == "progres":
                    self.progres.set(dades)
                elif tipus == "fet":
                    self.parelles_pendents = dades
                    self._finalitzar_escaneig()
                    return
                elif tipus == "error":
                    self.panell_sup.btn_escanejar.configure(state="normal")
                    self.lbl_estat.configure(text="Error durant l'escaneig.")
                    messagebox.showerror("Error d'escaneig", dades)
                    return
        except queue.Empty:
            pass
        self.after(100, self._comprovar_cua)

    def _finalitzar_escaneig(self):
        self.panell_sup.btn_escanejar.configure(state="normal")
        if not self.parelles_pendents:
            self.lbl_estat.configure(text="Escaneig finalitzat: Cap imatge duplicada trobada.")
            messagebox.showinfo("Resultat", "No s'han trobat duplicats.")
            return
        self.panell_inf.activar(True)
        self._mostrar_parella()

    def _mostrar_parella(self):
        self.panell_inf.activar_desfer(self.historial.te_accions())
        if self.index_actual >= len(self.parelles_pendents):
            self.panell_inf.activar(False)
            self.card_esq.netejar()
            self.card_dreta.netejar()
            resum = f"Neteja completada! {self.moguts_comptador} fitxers moguts ({formatar_mida(self.espai_estalviat)} recuperats)."
            self.lbl_estat.configure(text=resum)
            messagebox.showinfo("Completat", resum)
            return

        self.panell_inf.activar(True)
        orig, dup, tipus = self.parelles_pendents[self.index_actual]
        self.lbl_estat.configure(text=f"Parella {self.index_actual + 1} de {len(self.parelles_pendents)} | {tipus} | Estalviat: {formatar_mida(self.espai_estalviat)}")
        self.card_esq.actualitzar(orig)
        self.card_dreta.actualitzar(dup)

    def _executar_moviment(self, info_fitxer):
        exit_mov, ruta_desti = moure_fitxer_segur(info_fitxer['ruta'], self.panell_sup.carpeta_desti.get())
        if exit_mov:
            self.historial.registrar(self.index_actual, info_fitxer['ruta'], ruta_desti, info_fitxer['pes'])
            self.moguts_comptador += 1
            self.espai_estalviat += info_fitxer['pes']
        else:
            messagebox.showerror("Error", f"No s'ha pogut moure {info_fitxer['nom']}:\n{ruta_desti}")

    def _decidir(self, opcio):
        orig, dup, _ = self.parelles_pendents[self.index_actual]
        if opcio == "dreta":
            self._executar_moviment(dup)
        elif opcio == "esquerra":
            self._executar_moviment(orig)
        self.index_actual += 1
        self._mostrar_parella()

    def _desfer_accio(self):
        exit_undo, msg, dades = self.historial.desfer_ultima()
        if exit_undo:
            self.moguts_comptador -= 1
            self.espai_estalviat -= dades['pes']
            self.index_actual = dades['index']
            self._mostrar_parella()
        else:
            messagebox.showwarning("Desfer", msg)

    def _moure_tots(self):
        restants = len(self.parelles_pendents) - self.index_actual
        if messagebox.askyesno("Confirmar", f"Vols moure automàticament els {restants} duplicats restants?"):
            while self.index_actual < len(self.parelles_pendents):
                _, dup, _ = self.parelles_pendents[self.index_actual]
                self._executar_moviment(dup)
                self.index_actual += 1
            self._mostrar_parella()

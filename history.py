import os
import shutil

class HistorialAccions:
    def __init__(self):
        self.pila = []

    def registrar(self, index_parella, origen_original, ruta_desti_actual, pes_bytes):
        self.pila.append({
            'index': index_parella,
            'origen': origen_original,
            'desti': ruta_desti_actual,
            'pes': pes_bytes
        })

    def te_accions(self):
        return len(self.pila) > 0

    def desfer_ultima(self):
        """Retorna el fitxer al seu lloc original i retorna les dades per restaurar la UI."""
        if not self.pila:
            return False, "No hi ha cap acció per desfer.", None

        ultima = self.pila.pop()
        if not os.path.exists(ultima['desti']):
            return False, "El fitxer mogut ja no es troba a la carpeta de duplicats.", None

        try:
            os.makedirs(os.path.dirname(ultima['origen']), exist_ok=True)
            shutil.move(ultima['desti'], ultima['origen'])
            return True, "Acció desfeta correctament.", ultima
        except Exception as e:
            self.pila.append(ultima)
            return False, str(e), None

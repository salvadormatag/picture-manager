import os
import shutil

def formatar_mida(bytes_val):
    for unitat in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unitat}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} TB"

def moure_fitxer_segur(ruta_origen, carpeta_desti):
    """Mou un fitxer al destí afegint un sufix si ja existeix un nom igual."""
    if not os.path.exists(ruta_origen):
        return False, "El fitxer d'origen no existeix."

    os.makedirs(carpeta_desti, exist_ok=True)
    nom = os.path.basename(ruta_origen)
    ruta_final = os.path.join(carpeta_desti, nom)

    if os.path.exists(ruta_final):
        base, ext = os.path.splitext(nom)
        comptador = 1
        while os.path.exists(os.path.join(carpeta_desti, f"{base}_dup{comptador}{ext}")):
            comptador += 1
        ruta_final = os.path.join(carpeta_desti, f"{base}_dup{comptador}{ext}")

    try:
        shutil.move(ruta_origen, ruta_final)
        return True, ruta_final
    except Exception as e:
        return False, str(e)

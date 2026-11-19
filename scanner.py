import os
import hashlib
from collections import defaultdict
from PIL import Image, ImageOps
import imagehash
from config import EXTENSIONS_VALIDES

def obtenir_metadades(ruta):
    try:
        pes = os.path.getsize(ruta)
        data = os.path.getmtime(ruta)
        with Image.open(ruta) as img:
            img = ImageOps.exif_transpose(img)
            w, h = img.size
            return {
                'ruta': ruta,
                'nom': os.path.basename(ruta),
                'pes': pes,
                'pixels': w * h,
                'res': f"{w}x{h}",
                'data': data
            }
    except Exception:
        return None

def calcular_sha256(ruta):
    hasher = hashlib.sha256()
    with open(ruta, 'rb') as f:
        for bloc in iter(lambda: f.read(65536), b""):
            hasher.update(bloc)
    return hasher.hexdigest()

def triar_millor_copia(grup):
    """Retorna (millor_original, llista_duplicats)."""
    ordenat = sorted(grup, key=lambda x: (-x['pixels'], -x['pes'], x['data'], len(x['nom'])))
    return ordenat[0], ordenat[1:]

def buscar_duplicats(carpetes_origen, carpeta_desti, detectar_similars=True, llindar=5, callback_progres=None):
    ruta_abs_desti = os.path.abspath(carpeta_desti)
    rutes_uniques = set()
    fitxers = []

    for carpeta in carpetes_origen:
        for arrel, _, noms in os.walk(carpeta):
            if os.path.abspath(arrel).startswith(ruta_abs_desti):
                continue
            for nom in noms:
                if nom.lower().endswith(EXTENSIONS_VALIDES):
                    ruta_completa = os.path.abspath(os.path.join(arrel, nom))
                    if ruta_completa not in rutes_uniques:
                        rutes_uniques.add(ruta_completa)
                        meta = obtenir_metadades(ruta_completa)
                        if meta:
                            fitxers.append(meta)

    if not fitxers:
        return []

    ja_aparellats = set()
    parelles = []

    # Fase 1: Exactes (SHA-256)
    per_mida = defaultdict(list)
    for f in fitxers:
        per_mida[f['pes']].append(f)

    hashes = defaultdict(list)
    for pes, grup in per_mida.items():
        if len(grup) > 1:
            for f in grup:
                hashes[calcular_sha256(f['ruta'])].append(f)

    for _, grup in hashes.items():
        if len(grup) > 1:
            orig, dups = triar_millor_copia(grup)
            for d in dups:
                parelles.append((orig, d, "Còpia Exacta (100%)"))
                ja_aparellats.add(d['ruta'])

    if callback_progres:
        callback_progres(0.4)

    # Fase 2: Similars (pHash)
    if detectar_similars:
        pendents = [f for f in fitxers if f['ruta'] not in ja_aparellats]
        phashes = []
        for idx, f in enumerate(pendents):
            try:
                with Image.open(f['ruta']) as img:
                    img = ImageOps.exif_transpose(img)
                    f['phash'] = imagehash.phash(img)
                    phashes.append(f)
            except Exception:
                pass
            if callback_progres and idx % 15 == 0 and len(pendents) > 0:
                callback_progres(0.4 + 0.55 * (idx / len(pendents)))

        visitats = set()
        for i in range(len(phashes)):
            if phashes[i]['ruta'] in visitats:
                continue
            grup = [phashes[i]]
            visitats.add(phashes[i]['ruta'])
            for j in range(i + 1, len(phashes)):
                if phashes[j]['ruta'] not in visitats:
                    if (phashes[i]['phash'] - phashes[j]['phash']) <= llindar:
                        grup.append(phashes[j])
                        visitats.add(phashes[j]['ruta'])
            if len(grup) > 1:
                orig, dups = triar_millor_copia(grup)
                for d in dups:
                    parelles.append((orig, d, "Similar Visualment"))

    if callback_progres:
        callback_progres(1.0)

    return parelles

"""Clasifica documentos empresariales: factura, cotizacion, contrato u otro."""
import sys

from comun import llm

CATEGORIAS = ("factura", "cotizacion", "contrato", "otro")
INSTRUCCION = (
    "Clasifica el documento en una de estas categorías: factura, cotizacion, contrato, otro. "
    'Devuelve {"categoria": "...", "confianza": 0-1}.'
)
PALABRAS = {
    "factura": ("factura", "nit", "iva", "cufe", "total a pagar"),
    "cotizacion": ("cotización", "cotizacion", "propuesta económica", "validez de la oferta"),
    "contrato": ("contrato", "cláusula", "clausula", "las partes", "contratante", "vigencia"),
}


def clasificar_reglas(texto: str) -> dict:
    t = texto.lower()
    puntajes = {c: sum(p in t for p in ps) for c, ps in PALABRAS.items()}
    mejor = max(puntajes, key=puntajes.get)
    if puntajes[mejor] == 0:
        return {"categoria": "otro", "confianza": 0.3}
    total = sum(puntajes.values())
    return {"categoria": mejor, "confianza": round(puntajes[mejor] / total, 2)}


def clasificar(texto: str) -> dict:
    r = llm.preguntar_json(INSTRUCCION, texto)
    if r and r.get("categoria") in CATEGORIAS:
        r["metodo"] = "ia"
        return r
    r = clasificar_reglas(texto)
    r["metodo"] = "reglas"
    return r


if __name__ == "__main__":
    import json
    import pathlib

    for ruta in sys.argv[1:]:
        r = clasificar(pathlib.Path(ruta).read_text(encoding="utf-8"))
        print(ruta, json.dumps(r, ensure_ascii=False))

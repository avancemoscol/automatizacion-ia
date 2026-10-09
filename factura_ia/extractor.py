"""Extrae los campos clave de una factura a partir de su texto."""
import re
import sys

from comun import llm

INSTRUCCION = (
    "Extrae de la factura colombiana los campos: numero, fecha (AAAA-MM-DD), nit_emisor, "
    "emisor, subtotal, iva, total (números sin símbolos). Usa null si un campo no aparece."
)


def _numero(txt: str) -> float:
    txt = txt.strip().replace("$", "").replace(" ", "")
    if "," in txt and "." in txt:
        txt = txt.replace(".", "").replace(",", ".") if txt.rfind(",") > txt.rfind(".") else txt.replace(",", "")
    elif "," in txt:
        txt = txt.replace(",", ".") if len(txt.split(",")[-1]) <= 2 else txt.replace(",", "")
    elif txt.count(".") > 1 or (txt.count(".") == 1 and len(txt.split(".")[-1]) == 3):
        txt = txt.replace(".", "")
    return float(txt)


def _buscar(patron: str, texto: str):
    m = re.search(patron, texto, re.IGNORECASE)
    return m.group(1).strip() if m else None


def extraer_reglas(texto: str) -> dict:
    fecha = _buscar(r"fecha[^\d]*(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})", texto)
    if fecha and "/" in fecha:
        d, m, a = fecha.split("/")
        fecha = f"{a}-{m}-{d}"
    campos = {
        "numero": _buscar(r"factura[^\n]*?(?:n[o°º]\.?|número|numero)?\s*[:#]?\s*([A-Z]{1,5}-?\d+)", texto),
        "fecha": fecha,
        "nit_emisor": _buscar(r"nit[^\d]*([\d.]+-?\d?)", texto),
        "emisor": _buscar(r"^(.+?)\n", texto.strip() + "\n"),
        "subtotal": _buscar(r"subtotal[^\d]*([\d.,]+)", texto),
        "iva": _buscar(r"iva[^\d\n]*(?:\d+(?:[.,]\d+)?\s*%[^\d\n]*)?([\d.,]+)", texto),
        "total": _buscar(r"\btotal(?:\s+a\s+pagar)?[^\d\n]*([\d.,]+)\s*$", texto.replace("\r", "")) or _buscar(r"\btotal[^\d\n]*([\d.,]+)", texto),
    }
    for k in ("subtotal", "iva", "total"):
        campos[k] = _numero(campos[k]) if campos[k] else None
    return campos


def extraer(texto: str) -> dict:
    resultado = llm.preguntar_json(INSTRUCCION, texto)
    if resultado:
        resultado["metodo"] = "ia"
        return resultado
    resultado = extraer_reglas(texto)
    resultado["metodo"] = "reglas"
    return resultado


def validar(campos: dict) -> list[str]:
    """Revisa coherencia contable: subtotal + IVA debe ser igual al total."""
    s, i, t = (campos.get(k) for k in ("subtotal", "iva", "total"))
    if None in (s, i, t):
        return ["Faltan montos para validar"]
    return [] if abs(s + i - t) < 1 else [f"Inconsistencia: {s} + {i} != {t}"]


if __name__ == "__main__":
    import json

    texto = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else sys.stdin.read()
    datos = extraer(texto)
    datos["alertas"] = validar(datos)
    print(json.dumps(datos, ensure_ascii=False, indent=2))

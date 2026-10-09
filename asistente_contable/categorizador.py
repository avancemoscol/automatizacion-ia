"""Sugiere la cuenta contable (PUC colombiano) para un movimiento bancario."""
import csv
import sys

from comun import llm

CUENTAS = {
    "513550": "Gastos - Servicios públicos",
    "512010": "Gastos - Arrendamientos",
    "510506": "Gastos - Nómina y sueldos",
    "513525": "Gastos - Transporte y combustibles",
    "519530": "Gastos - Útiles y papelería",
    "413595": "Ingresos - Venta de servicios",
    "530505": "Gastos financieros - Comisiones bancarias",
}
REGLAS = {
    "513550": ("energía", "energia", "acueducto", "internet", "claro", "tigo", "gas natural"),
    "512010": ("arriendo", "arrendamiento"),
    "510506": ("nómina", "nomina", "salario"),
    "513525": ("gasolina", "combustible", "terpel", "peaje", "uber"),
    "519530": ("papelería", "papeleria", "útiles", "tinta"),
    "413595": ("pago cliente", "abono factura", "consignación cliente"),
    "530505": ("comisión", "comision", "cuota de manejo", "gmf"),
}
INSTRUCCION = "Eres contador colombiano. Elige la cuenta PUC más adecuada de esta lista: " + "; ".join(
    f"{k} {v}" for k, v in CUENTAS.items()
) + '. Devuelve {"cuenta": "codigo", "razon": "breve"}.'


def categorizar_reglas(descripcion: str) -> dict:
    d = descripcion.lower()
    for cuenta, palabras in REGLAS.items():
        if any(p in d for p in palabras):
            return {"cuenta": cuenta, "razon": "coincidencia de palabra clave"}
    return {"cuenta": None, "razon": "requiere revisión manual"}


def categorizar(descripcion: str, monto: float = 0.0) -> dict:
    r = llm.preguntar_json(INSTRUCCION, f"{descripcion} | monto: {monto}")
    if r and r.get("cuenta") in CUENTAS:
        r["metodo"] = "ia"
    else:
        r = categorizar_reglas(descripcion)
        r["metodo"] = "reglas"
    r["nombre"] = CUENTAS.get(r["cuenta"], "Sin clasificar")
    return r


def procesar_csv(ruta: str) -> list[dict]:
    """Lee un CSV con columnas fecha,descripcion,monto y agrega la cuenta sugerida."""
    with open(ruta, newline="", encoding="utf-8") as f:
        return [{**fila, **categorizar(fila["descripcion"], float(fila["monto"]))} for fila in csv.DictReader(f)]


if __name__ == "__main__":
    for fila in procesar_csv(sys.argv[1]):
        print(f'{fila["fecha"]}  {fila["descripcion"][:34]:34} {fila["monto"]:>12}  ->  {fila["cuenta"]} {fila["nombre"]}  [{fila["metodo"]}]')

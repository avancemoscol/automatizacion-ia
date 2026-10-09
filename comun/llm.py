"""Cliente mínimo de LLM (solo librería estándar).

Si existe ANTHROPIC_API_KEY se llama a la API de Anthropic. Si no, devuelve None
y cada proyecto usa su respaldo local basado en reglas.
"""
import json
import os
import urllib.request

MODELO = os.environ.get("MODELO_IA", "claude-haiku-4-5-20251001")


def disponible() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def preguntar_json(instruccion: str, texto: str) -> dict | None:
    """Pide al modelo una respuesta JSON. Devuelve None si no hay clave o falla."""
    if not disponible():
        return None
    cuerpo = {
        "model": MODELO,
        "max_tokens": 600,
        "system": instruccion + " Responde SOLO con un objeto JSON válido, sin texto adicional.",
        "messages": [{"role": "user", "content": texto}],
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(cuerpo).encode(),
        headers={
            "content-type": "application/json",
            "x-api-key": os.environ["ANTHROPIC_API_KEY"],
            "anthropic-version": "2023-06-01",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            salida = json.load(r)["content"][0]["text"]
        inicio, fin = salida.find("{"), salida.rfind("}")
        return json.loads(salida[inicio : fin + 1])
    except Exception:
        return None

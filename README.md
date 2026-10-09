# Automatización con IA

Tres proyectos pequeños de automatización de procesos administrativos y contables en Colombia, escritos en Python (solo librería estándar, sin dependencias).

Cada uno usa un modelo de lenguaje (Claude, vía API de Anthropic) cuando existe la variable `ANTHROPIC_API_KEY`. Si no existe, funciona con reglas locales, así que se puede probar sin costo.

| Proyecto | Qué hace |
|---|---|
| `factura_ia` | Extrae número, fecha, NIT, subtotal, IVA y total de una factura y valida que subtotal + IVA = total. |
| `clasificador_docs` | Clasifica documentos como factura, cotización, contrato u otro. |
| `asistente_contable` | Sugiere la cuenta PUC para cada movimiento de un extracto bancario en CSV. |

## Uso

```bash
python3 -m factura_ia.extractor data/factura_ejemplo.txt
python3 -m clasificador_docs.clasificador data/*.txt
python3 -m asistente_contable.categorizador data/movimientos.csv

# con IA (opcional)
export ANTHROPIC_API_KEY=...
python3 -m factura_ia.extractor data/factura_ejemplo.txt
```

## Pruebas

```bash
python3 -m unittest discover -s tests -t .
```

Las pruebas corren siempre en modo reglas, sin red.

## Estado

Son prototipos de portafolio con datos de ejemplo. El modo IA envía el texto al proveedor, así que no uses documentos reales con datos sensibles sin revisar la política de privacidad correspondiente.

Autor: César Andrés Santana Gereda.

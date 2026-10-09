import os
import unittest

os.environ.pop("ANTHROPIC_API_KEY", None)  # pruebas deterministas, sin red

from asistente_contable.categorizador import categorizar, procesar_csv
from clasificador_docs.clasificador import clasificar
from factura_ia.extractor import extraer, validar

DATA = os.path.join(os.path.dirname(__file__), "..", "data")


def leer(nombre):
    with open(os.path.join(DATA, nombre), encoding="utf-8") as f:
        return f.read()


class Factura(unittest.TestCase):
    def test_extrae_campos(self):
        d = extraer(leer("factura_ejemplo.txt"))
        self.assertEqual(d["numero"], "FV-2041")
        self.assertEqual(d["fecha"], "2026-09-15")
        self.assertEqual(d["subtotal"], 1000000)
        self.assertEqual(d["iva"], 190000)
        self.assertEqual(d["total"], 1190000)
        self.assertEqual(validar(d), [])

    def test_detecta_inconsistencia(self):
        self.assertTrue(validar({"subtotal": 100, "iva": 19, "total": 200}))


class Clasificador(unittest.TestCase):
    def test_categorias(self):
        self.assertEqual(clasificar(leer("factura_ejemplo.txt"))["categoria"], "factura")
        self.assertEqual(clasificar(leer("contrato_ejemplo.txt"))["categoria"], "contrato")
        self.assertEqual(clasificar(leer("cotizacion_ejemplo.txt"))["categoria"], "cotizacion")
        self.assertEqual(clasificar("hola mundo")["categoria"], "otro")


class Contable(unittest.TestCase):
    def test_csv(self):
        filas = procesar_csv(os.path.join(DATA, "movimientos.csv"))
        cuentas = [f["cuenta"] for f in filas]
        self.assertEqual(cuentas, ["512010", "413595", "513525", "530505", "513550", None])

    def test_sin_regla(self):
        self.assertIsNone(categorizar("algo raro")["cuenta"])


if __name__ == "__main__":
    unittest.main()

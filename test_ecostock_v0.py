# TEST SUITE V0  |  pytest – Detecta defectos del estado inicial
# Ejecutar: pytest test_ecostock_v0.py -v
# Resultado esperado: 3 FAILED, 3 PASSED

import pytest
from datetime import datetime, timedelta
from ecostock_v0 import ProductManager


class TestEcoStockV0:

    def setup_method(self):
        self.pm = ProductManager()
        future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        self.pm.registrar_producto_perecedero(
            "P001", "Leche entera", 1200, 10, 0, future
        )

    # ── R01: Validación de fecha ──────────────────────────────

    def test_R01_fecha_pasada_retorna_codigo_especifico(self):
        """
        TC-BN-01 | Fecha anterior a hoy debe retornar ERR_VAL_EXPIRY_PAST.
        FALLA en v0: retorna 'Error en fecha' (mensaje genérico).
        """
        resultado = self.pm.registrar_producto_perecedero(
            "P999", "Yogurt", 400, 5, 0, "2020-05-10"
        )
        assert resultado == "ERR_VAL_EXPIRY_PAST", (
            f"DEFECTO DETECTADO – Retornó '{resultado}' en lugar de 'ERR_VAL_EXPIRY_PAST'"
        )

    def test_R01_fecha_hoy_es_aceptada(self):
        """
        TC-BC-02 | Fecha igual a hoy (valor frontera) debe ser aceptada.
        PASA en v0: la condición expiry_date_str < today_str es False.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        resultado = self.pm.registrar_producto_perecedero(
            "P100", "Queso fresco", 800, 3, 0, today
        )
        assert resultado == "Éxito"

    # ── R02: Cálculo de valor total de stock ──────────────────

    def test_R02_descuento_excesivo_debe_dar_cero(self):
        """
        TC-BN-02 | Descuento 3000 > subtotal 2000: total_value debe ser 0.00.
        FALLA en v0: calcula y almacena -1000.
        """
        future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        self.pm.registrar_producto_perecedero(
            "P002", "Yogurt Frutilla", 400, 5, 3000, future
        )
        valor = self.pm.inventory["P002"]["total_value"]
        assert valor == 0.00, (
            f"DEFECTO DETECTADO – total_value es {valor} (negativo, corrompiendo inventario)"
        )

    def test_R02_calculo_normal_correcto(self):
        """
        TC-BN-02b | Descuento menor al subtotal: (500*4)-100 = 1900.
        PASA en v0: operación sin borde negativo.
        """
        future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        self.pm.registrar_producto_perecedero("P003", "Mantequilla", 500, 4, 100, future)
        assert self.pm.inventory["P003"]["total_value"] == 1900

    # ── R04: Control de acceso por rol ───────────────────────

    def test_R04_rol_exacto_puede_eliminar(self):
        """
        TC-BN-03a | Rol 'Administrador' (capitalización exacta) puede eliminar.
        PASA en v0: la comparación estricta coincide.
        """
        resultado = self.pm.eliminar_registro_producto("P001", "Administrador")
        assert resultado == "Registro eliminado"

    def test_R04_rol_minusculas_debe_ser_reconocido(self):
        """
        TC-BC-01 | Rol 'administrador' (minúsculas) debe ser reconocido como válido.
        FALLA en v0: comparación estricta retorna 'Acceso denegado'.
        """
        resultado = self.pm.eliminar_registro_producto("P001", "administrador")
        assert resultado == "Registro eliminado", (
            f"DEFECTO DETECTADO – '{resultado}' deniega a un administrador legítimo"
        )

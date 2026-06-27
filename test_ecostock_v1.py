# ============================================================
# TEST SUITE V1  |  pytest – Valida las correcciones aplicadas
# Ejecutar: pytest test_ecostock_v1.py -v --tb=short
# Resultado esperado: 8 PASSED
# ============================================================
import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from ecostock_v1 import ProductManager


class TestEcoStockV1:

    def setup_method(self):
        self.pm = ProductManager()
        future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        self.pm.registrar_producto_perecedero(
            "P001", "Leche entera", 1200, 10, 0, future
        )

    # ---- R01: CHG-001 verificado --------------------------------

    def test_R01_fecha_pasada_retorna_codigo_especifico(self):
        """PASA: CHG-001 implementa ERR_VAL_EXPIRY_PAST."""
        resultado = self.pm.registrar_producto_perecedero(
            "P999", "Yogurt", 400, 5, 0, "2020-05-10"
        )
        assert resultado == "ERR_VAL_EXPIRY_PAST"

    def test_R01_formato_invalido_retorna_error_formato(self):
        """PASA: CHG-001 valida formato antes de comparar fechas."""
        resultado = self.pm.registrar_producto_perecedero(
            "P998", "Pan", 200, 2, 0, "31-12-2027"
        )
        assert resultado == "ERR_VAL_FORMAT_DATE"

    def test_R01_fecha_hoy_es_aceptada(self):
        """PASA: valor frontera (hoy) sigue siendo aceptado."""
        today = datetime.now().strftime("%Y-%m-%d")
        resultado = self.pm.registrar_producto_perecedero(
            "P100", "Queso fresco", 800, 3, 0, today
        )
        assert resultado == "Exito"

    # ---- R02: CHG-002 verificado --------------------------------

    def test_R02_descuento_excesivo_da_exactamente_cero(self):
        """PASA: CHG-002 fuerza total_value a 0.00 con max()."""
        future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        self.pm.registrar_producto_perecedero(
            "P002", "Yogurt Frutilla", 400, 5, 3000, future
        )
        assert self.pm.inventory["P002"]["total_value"] == Decimal("0.00")

    def test_R02_calculo_usa_precision_decimal(self):
        """PASA: CHG-002 usa Decimal, no float, evitando imprecision IEEE 754."""
        future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        self.pm.registrar_producto_perecedero("P003", "Mantequilla", 500, 4, 100, future)
        valor = self.pm.inventory["P003"]["total_value"]
        assert isinstance(valor, Decimal), "total_value debe ser Decimal, no float"
        assert valor == Decimal("1900.00")

    # ---- R04: CHG-003 verificado --------------------------------

    def test_R04_rol_minusculas_permite_eliminar(self):
        """PASA: CHG-003 normaliza el string antes de comparar."""
        resultado = self.pm.eliminar_registro_producto("P001", "administrador")
        assert resultado == "Registro eliminado"

    def test_R04_rol_con_espacios_permite_eliminar(self):
        """PASA: CHG-003 tambien elimina espacios laterales (.strip())."""
        resultado = self.pm.eliminar_registro_producto("P001", "  Administrador  ")
        assert resultado == "Registro eliminado"

    def test_R04_rol_vendedor_sigue_denegado(self):
        """PASA: CHG-003 no amplia permisos a roles no administrador."""
        resultado = self.pm.eliminar_registro_producto("P001", "Vendedor")
        assert resultado == "Acceso denegado"

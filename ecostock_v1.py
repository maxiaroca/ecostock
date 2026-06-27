# ============================================================
# ECOSTOCK V1  |  Código corregido tras gestión del cambio
# CHG-001: ERR_VAL_EXPIRY_PAST + validación ISO-8601 (R01)
# CHG-002: Límite inferior en 0.00 + precisión Decimal   (R02)
# CHG-003: Normalización de rol con .strip().lower()     (R04)
# ============================================================
from datetime import datetime
from decimal import Decimal, InvalidOperation


class ProductManager:

    def __init__(self):
        self.inventory = {}

    def registrar_producto_perecedero(
        self, product_id, name, unit_price, quantity, discount, expiry_date_str
    ):
        # CHG-001 │ Validación de formato ISO-8601 antes de comparar
        try:
            expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d")
        except (ValueError, TypeError):
            return "ERR_VAL_FORMAT_DATE"

        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # CHG-001 │ Código de error específico según resolución de R01
        if expiry_date < today:
            return "ERR_VAL_EXPIRY_PAST"

        # CHG-002 │ Aritmética de precisión fija + límite inferior en 0.00
        try:
            subtotal    = Decimal(str(unit_price)) * Decimal(str(quantity))
            desc        = Decimal(str(discount))
            total_value = max(Decimal("0.00"), subtotal - desc)
        except InvalidOperation:
            return "ERR_VAL_NUMERIC"

        self.inventory[product_id] = {
            "name":        name,
            "unit_price":  unit_price,
            "quantity":    quantity,
            "discount":    discount,
            "expiry_date": expiry_date_str,
            "total_value": total_value,
        }
        return "Exito"

    def eliminar_registro_producto(self, product_id, user_role):
        # CHG-003 │ Normalización: elimina espacios y convierte a minúsculas
        if isinstance(user_role, str) and user_role.strip().lower() == "administrador":
            if product_id in self.inventory:
                del self.inventory[product_id]
                return "Registro eliminado"
            return "No encontrado"
        return "Acceso denegado"

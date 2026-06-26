
# ECOSTOCK V0  |  Estado inicial (código EV3 sin modificar)
# Versión con defectos identificados en inspección EV3

from datetime import datetime

class ProductManager:

    def __init__(self):
        self.inventory = {}

    def registrar_producto_perecedero(self, product_id, name, unit_price, quantity, discount, expiry_date_str):
        # R01 – Comparación de strings sin control de formato
        today_str = datetime.now().strftime("%Y-%m-%d")
        if expiry_date_str < today_str:
            return "Error en fecha"   # BUG: mensaje genérico, no ERR_VAL_EXPIRY_PAST

        # R02 – Aritmética flotante sin límite inferior ni precisión decimal
        total_value = (unit_price * quantity) - discount   # BUG: puede resultar negativo

        self.inventory[product_id] = {
            "name": name,
            "unit_price": unit_price,
            "quantity": quantity,
            "discount": discount,
            "expiry_date": expiry_date_str,
            "total_value": total_value
        }
        return "Éxito"

    def eliminar_registro_producto(self, product_id, user_role):
        # R04 – Comparación de rol sensible a capitalización
        if user_role == "Administrador":   # BUG: "administrador" o "ADMINISTRADOR" → Acceso denegado
            if product_id in self.inventory:
                del self.inventory[product_id]
                return "Registro eliminado"
            return "No encontrado"
        return "Acceso denegado"

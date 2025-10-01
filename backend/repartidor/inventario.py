class Inventario:
    def __init__(self):
        self.items = []

    def agregar(self, item):
        self.items.append(item)

    def eliminar(self, item):
        for i, p in enumerate(self.items):
            if p.codigo == item.codigo:
                del self.items[i]
                return
        # If not found, do nothing or raise error
        raise ValueError(f"Paquete with codigo {item.codigo} not found in inventory")

    def obtener_items(self):
        return self.items

    def peso_total(self):
        return sum(getattr(p, 'peso', 0) for p in self.items)

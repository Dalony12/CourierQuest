class Inventario:
    def __init__(self):
        self.items = []

    def agregar(self, item):
        self.items.append(item)

    def eliminar(self, item):
        self.items.remove(item)

    def obtener_items(self):
        return self.items

    def peso_total(self):
        return sum(getattr(p, 'peso', 0) for p in self.items)

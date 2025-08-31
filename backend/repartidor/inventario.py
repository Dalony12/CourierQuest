class Inventario:
    def __init__(self):
        self.items = []

    def agregar_item(self, item):
        self.items.append(item)

    def eliminar_item(self, item):
        self.items.remove(item)

    def obtener_items(self):
        return self.items

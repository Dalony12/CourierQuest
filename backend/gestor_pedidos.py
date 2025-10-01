class GestorPedidos:
    def __init__(self):
        self.pedidos = []  # Lista de objetos Pedido

    def agregar_pedido(self, pedido):
        """Agrega un pedido."""
        self.pedidos.append(pedido)

    def eliminar_pedido(self, pedido):
        """Elimina un pedido de la lista."""
        if pedido in self.pedidos:
            self.pedidos.remove(pedido)

    def _ordenar_por_prioridad(self):
        """Ordena los pedidos por prioridad ascendente."""
        self.pedidos.sort(key=lambda p: p.priority)

    def obtener_disponibles(self, tiempo_actual):
        """Devuelve los pedidos que ya están liberados y aún no se han recogido ni entregado."""
        return [p for p in self.pedidos if tiempo_actual >= p.release_time and not p.recogido and not p.entregado]

    def obtener_activos(self):
        """Pedidos que están en el inventario pero no se han entregado."""
        return [p for p in self.pedidos if p.recogido and not p.entregado]

    def obtener_entregados(self):
        """Pedidos ya entregados."""
        return [p for p in self.pedidos if p.entregado]

    def mostrar_resumen(self):
        """Devuelve un resumen textual de todos los pedidos."""
        return [str(p) for p in self.pedidos]
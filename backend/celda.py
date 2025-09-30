import pygame

TILE_SIZE = 50

class Celda:
    def __init__(self, tipo, x, y, legend):
        
        self.tipo = tipo
        self.x = x
        self.y = y

        # Obtener propiedades de la leyenda
        info = legend.get(tipo, {})
        self.name = info.get("name", "unknown")
        self.blocked = info.get("blocked", False)
        self.surface_weight = info.get("surface_weight", 1)

        # Crear rect para renderizado y colisiones
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)

    def __str__(self):
        return f"Celda({self.tipo}, {self.name}, bloqueada={self.blocked}, pos=({self.x},{self.y}))"

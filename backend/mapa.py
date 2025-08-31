import random
import pygame
from backend.celda import Celda

TILE_SIZE = 50  # Ajuste final para que el ciclista se vea grande

class Mapa:
    def __init__(self, data): 
        self.city_name = None
        self.width = None
        self.height = None
        self.goal = None
        self.max_time = None
        self.tiles_raw = []
        self.legend = {}
        self.sprites = {}  # Sprites para renderizar
        self.celdas = []   # Lista de objetos Celda
        self._cargar(data)
        self._crear_sprites()
        self._crear_celdas()

    def _cargar(self, data):
        try:
            self.city_name = data.get("city_name")
            self.width = data.get("width")
            self.height = data.get("height")
            self.goal = data.get("goal")
            self.max_time = data.get("max_time")

            # Transponer matriz: fila -> columna
            raw_tiles = data.get("tiles", [])
            if raw_tiles:
                self.tiles_raw = [list(col) for col in zip(*raw_tiles)]
            else:
                self.tiles_raw = []

            self.legend = data.get("legend", {})
        except Exception as e:
            print("Excepción al cargar el mapa:", e)

    def _crear_sprites(self):
        """Genera sprites estilizados según el legend."""
        for key in self.legend.keys():
            surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
            surf.fill((0, 0, 0, 0))  # fondo transparente

            if key == "C":   # Calle más oscura sin líneas
                surf.fill((80, 80, 80))

            elif key == "B": # Edificio rojo pálido con ventana central
                surf.fill((255, 255, 255))  # color base del edificio
                ventana_color = (150, 200, 255)  # celeste
                ventana_tam = TILE_SIZE // 2
                x = (TILE_SIZE - ventana_tam) // 2
                y = (TILE_SIZE - ventana_tam) // 2
                pygame.draw.rect(surf, ventana_color, (x, y, ventana_tam, ventana_tam))

            elif key == "P": # Parque verde con textura
                surf.fill((0, 180, 0))
                for _ in range(30):
                    x = random.randint(0, TILE_SIZE-1)
                    y = random.randint(0, TILE_SIZE-1)
                    surf.set_at((x, y), (0, 150, 0))

            else: # Default: celeste
                surf.fill((0, 200, 200))

            self.sprites[key] = surf


    def _crear_celdas(self):
        """Crea objetos Celda para cada tile del mapa."""
        self.celdas = [
            [Celda(self.tiles_raw[col][fila], col, fila, self.legend)
             for fila in range(self.height)]
            for col in range(self.width)
        ]

    def dibujar(self, screen):
        """Dibuja el mapa en la pantalla usando celdas y sprites."""
        for col in range(self.width):
            for fila in range(self.height):
                celda = self.celdas[col][fila]
                sprite = self.sprites.get(celda.tipo)
                if sprite:
                    rect = pygame.Rect(col * TILE_SIZE, fila * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    screen.blit(sprite, rect)

    def __str__(self):
        return f"Mapa: {self.city_name} ({self.width}x{self.height})"

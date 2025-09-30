import random
import pygame
from backend.celda import Celda
from collections import deque

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

            elif key == "B": # Edificio blanco con ventana central
                surf.fill((255, 255, 255))  # color base del edificio
                ventana_color = (150, 200, 255)  # celeste
                ventana_tam = TILE_SIZE // 2
                x = (TILE_SIZE - ventana_tam) // 2
                y = (TILE_SIZE - ventana_tam) // 2
                pygame.draw.rect(surf, ventana_color, (x, y, ventana_tam, ventana_tam))

            elif key == "D": # Puerta
                surf.fill((255, 255, 255))  # fill blanco desde el inicio
                # Base negra pequeña centrada abajo
                base_ancho = TILE_SIZE // 3
                base_alto = TILE_SIZE // 7
                base_x = (TILE_SIZE - base_ancho) // 2
                base_y = TILE_SIZE - base_alto - 4
                pygame.draw.rect(surf, (0,0,0), (base_x, base_y, base_ancho, base_alto))
                # Arco negro semicircular arriba
                arco_ancho = TILE_SIZE // 2
                arco_alto = TILE_SIZE // 2
                arco_x = (TILE_SIZE - arco_ancho) // 2
                arco_y = 4
                arco_rect = pygame.Rect(arco_x, arco_y, arco_ancho, arco_alto)
                pygame.draw.arc(surf, (0,0,0), arco_rect, 3.1416, 0, 2)

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
        """Crea objetos Celda para cada tile del mapa y genera UNA puerta por edificio."""
        tiles_mod = [row[:] for row in self.tiles_raw]

        visitado = [[False for _ in range(self.height)] for _ in range(self.width)]
        edificios = []

        # BFS para agrupar edificios
        for col in range(self.width):
            for fila in range(self.height):
                if tiles_mod[col][fila] == "B" and not visitado[col][fila]:
                    grupo = []
                    queue = [(col, fila)]
                    visitado[col][fila] = True
                    while queue:
                        x, y = queue.pop(0)
                        grupo.append((x, y))
                        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                            nx, ny = x+dx, y+dy
                            if 0 <= nx < self.width and 0 <= ny < self.height:
                                if tiles_mod[nx][ny] == "B" and not visitado[nx][ny]:
                                    visitado[nx][ny] = True
                                    queue.append((nx, ny))
                    edificios.append(grupo)

        # Colocar una sola puerta por edificio
        for grupo in edificios:
            candidatos = []
            for (x, y) in grupo:
                if y+1 < self.height and tiles_mod[x][y+1] == "C":
                    candidatos.append((x, y))
            if candidatos:
                puerta_x, puerta_y = random.choice(candidatos)
                tiles_mod[puerta_x][puerta_y] = "D"

        self.celdas = [
            [Celda(tiles_mod[col][fila], col, fila, self.legend)
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

    def find_path(self, start_x, start_y, end_x, end_y):
        """Encuentra el camino más corto usando BFS."""
        if not (0 <= start_x < self.width and 0 <= start_y < self.height and 0 <= end_x < self.width and 0 <= end_y < self.height):
            return []
        queue = deque([(start_x, start_y, [])])
        visited = set()
        visited.add((start_x, start_y))
        while queue:
            x, y, path = queue.popleft()
            if (x, y) == (end_x, end_y):
                return path + [(x, y)]
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height and (nx, ny) not in visited:
                    tipo = self.celdas[nx][ny].tipo
                    # Permitir movimiento a celdas no bloqueadas
                    if not self.legend.get(tipo, {}).get("blocked", False):
                        visited.add((nx, ny))
                        queue.append((nx, ny, path + [(x, y)]))
        return []

    def __str__(self):
        return f"Mapa: {self.city_name} ({self.width}x{self.height})"

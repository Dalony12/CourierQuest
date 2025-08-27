import pygame

class MapaPygame:
    def __init__(self, mapa, pantalla):
        """
        mapa: instancia de tu clase Mapa con atributos tiles, legend, width, height
        pantalla: superficie de pygame donde se dibuja
        """
        self.mapa = mapa
        self.pantalla = pantalla
        # calcular tamaño de celda para que el mapa quepa en pantalla
        ancho, alto = pantalla.get_size()
        self.tile_size = min(ancho // mapa.width, alto // mapa.height)

        # asignar colores por tipo de celda según la leyenda
        self.colores = {}
        for k, v in mapa.legend.items():
            if v.get("blocked"):
                self.colores[k] = (100, 100, 100)  # gris oscuro
            elif v.get("surface_weight"):
                self.colores[k] = (200, 200, 200)  # gris claro
            else:
                self.colores[k] = (0, 255, 0)      # verde por defecto

        # fuente para textos
        self.fuente = pygame.font.SysFont("Arial", 20)

    def dibujar(self):
        # Dibujar matriz del mapa
        for fila_idx, fila in enumerate(self.mapa.tiles):
            for col_idx, celda in enumerate(fila):
                color = self.colores.get(celda, (255, 255, 255))
                rect = pygame.Rect(
                    col_idx * self.tile_size,
                    fila_idx * self.tile_size,
                    self.tile_size,
                    self.tile_size
                )
                pygame.draw.rect(self.pantalla, color, rect)

        # Dibujar información en esquina
        info = [
            f"Ciudad: {self.mapa.city_name}",
            f"Meta: {self.mapa.goal}",
            f"Tiempo máximo: {self.mapa.max_time}"
        ]
        for i, texto in enumerate(info):
            surface = self.fuente.render(texto, True, (255, 255, 255))
            self.pantalla.blit(surface, (10, 10 + i*25))

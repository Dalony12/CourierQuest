import pygame

class Camara:
    def __init__(self, ancho_pantalla, alto_pantalla, mapa_width, mapa_height, zoom=1.5):
        self.ancho_pantalla = ancho_pantalla
        self.alto_pantalla = alto_pantalla
        self.mapa_width = mapa_width
        self.mapa_height = mapa_height
        self.zoom = zoom
        self.offset_x = 0
        self.offset_y = 0

    def update(self, target_rect):
        # Centrar la cámara según la posición del objetivo
        self.offset_x = target_rect.centerx - self.ancho_pantalla / (2 * self.zoom)
        self.offset_y = target_rect.centery - self.alto_pantalla / (2 * self.zoom)

        # Límites para evitar que la cámara muestre áreas fuera del mapa
        max_x = self.mapa_width - self.ancho_pantalla / self.zoom
        max_y = self.mapa_height - self.alto_pantalla / self.zoom

        # Limitar desplazamiento horizontal
        if self.offset_x < 0:
            self.offset_x = 0
        elif self.offset_x > max_x:
            self.offset_x = max_x

        # Limitar desplazamiento vertical
        if self.offset_y < 0:
            self.offset_y = 0
        elif self.offset_y > max_y:
            self.offset_y = max_y

    def apply_surface(self, surf, rect):
        # Escalar superficie según zoom
        surf_scaled = pygame.transform.scale(
            surf,
            (int(rect.width * self.zoom), int(rect.height * self.zoom))
        )

        # Ajustar la posición en pantalla según el desplazamiento de la cámara
        new_rect = pygame.Rect(
            (rect.x - self.offset_x) * self.zoom,
            (rect.y - self.offset_y) * self.zoom,
            surf_scaled.get_width(),
            surf_scaled.get_height()
        )

        return surf_scaled, new_rect

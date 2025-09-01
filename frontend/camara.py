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
        # Centramos la cámara en el objetivo
        self.offset_x = target_rect.centerx - self.ancho_pantalla / (2 * self.zoom)
        self.offset_y = target_rect.centery - self.alto_pantalla / (2 * self.zoom)

        # Limitar para no mostrar fuera del mapa (cálculo original)
        max_x = self.mapa_width - self.ancho_pantalla / self.zoom
        max_y = self.mapa_height - self.alto_pantalla / self.zoom

        if self.offset_x < 0:
            self.offset_x = 0
        elif self.offset_x > max_x:
            self.offset_x = max_x

        if self.offset_y < 0:
            self.offset_y = 0
        elif self.offset_y > max_y:
            self.offset_y = max_y

    def apply_surface(self, surf, rect):
        # Escalar superficie y devolver rect ajustado
        surf_scaled = pygame.transform.scale(surf, (int(rect.width * self.zoom), int(rect.height * self.zoom)))
        new_rect = pygame.Rect((rect.x - self.offset_x) * self.zoom,
                               (rect.y - self.offset_y) * self.zoom,
                               surf_scaled.get_width(),
                               surf_scaled.get_height())
        return surf_scaled, new_rect

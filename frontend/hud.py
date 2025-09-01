import pygame

import os


class HUD:
    def __init__(self, screen, max_energy=100):
        self.screen = screen
        self.max_energy = max_energy
        self.energy = max_energy
        self.score = 0
        self.font = pygame.font.Font(None, 36)

        # Diccionario para posiciones personalizadas de cada sprite
        # Puedes modificar estos valores desde tu código para ajustar la posición de cada sprite
        self.sprite_positions = {
            'btnAceptar': (77, 200),
            'gps': (50, 300),
        }

        # Ruta a los sprites del HUD
        hud_sprites_path = os.path.join("assets", "sprites", "HUD")
        self.sprites = {}
        # Cargar todos los archivos .png del HUD
        for filename in os.listdir(hud_sprites_path):
            if filename.endswith(".png"):
                key = filename[:-4]  # nombre sin .png
                full_path = os.path.join(hud_sprites_path, filename)
                self.sprites[key] = pygame.image.load(full_path).convert_alpha()

        # Pila para el orden de dibujo de los sprites (de fondo a frente)
        # Agrega aquí los nombres de los sprites en el orden que quieras que se dibujen
        self.draw_stack = [
            'hud',  # El fondo siempre primero si existe
            'btnAceptar',
            'gps',
            # ...agrega aquí otros nombres de sprites en el orden deseado...
        ]

    def update_energy(self, amount):
        self.energy = max(0, min(self.max_energy, self.energy + amount))

    def add_score(self, points):
        self.score += points

    def draw_bar(self, x, y, current, maximum, color, width=200, height=20, surface=None):
        """Dibuja una barra de progreso (vida/energía) en el surface dado o en self.screen."""
        if surface is None:
            surface = self.screen
        pygame.draw.rect(surface, (255, 255, 255), (x, y, width, height), 2)
        fill_width = int((current / maximum) * (width - 4))
        pygame.draw.rect(surface, color, (x + 2, y + 2, fill_width, height - 4))

    def draw(self, surface=None):
        """Dibuja los sprites PNG del HUD en el orden definido por draw_stack (de fondo a frente)."""
        if surface is None:
            surface = self.screen
        # Si la pila está vacía, dibuja todos los sprites como antes
        if not self.draw_stack:
            for key, sprite in self.sprites.items():
                pos = self.sprite_positions.get(key, (0, 0))
                surface.blit(sprite, pos)
        else:
            for key in self.draw_stack:
                sprite = self.sprites.get(key)
                if sprite:
                    pos = self.sprite_positions.get(key, (0, 0))
                    # Escalar el fondo si es 'hud'
                    if key == 'hud':
                        sprite = pygame.transform.scale(sprite, surface.get_size())
                    surface.blit(sprite, pos)

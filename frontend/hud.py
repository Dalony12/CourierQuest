import pygame

class HUD:
    def __init__(self, screen, max_energy=100):
        self.screen = screen
        self.max_energy = max_energy
        self.energy = max_energy
        self.score = 0

        # Fuente para texto
        self.font = pygame.font.Font(None, 36)

    def update_energy(self, amount):
        """Ajusta la energía dentro de los límites."""
        self.energy = max(0, min(self.max_energy, self.energy + amount))

    def add_score(self, points):
        """Suma puntos al marcador."""
        self.score += points

    def draw_bar(self, x, y, current, maximum, color, width=200, height=20):
        """Dibuja una barra de progreso (vida/energía)."""
        # Marco de la barra
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, width, height), 2)

        # Relleno proporcional
        fill_width = int((current / maximum) * (width - 4))
        pygame.draw.rect(self.screen, color, (x + 2, y + 2, fill_width, height - 4))

    def draw(self):
        """Dibuja todos los elementos del HUD."""
        # Barra de energía (azul)
        self.draw_bar(20, 50, self.energy, self.max_energy, (0, 120, 255))

        # Texto de puntaje
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (20, 80))

import sys
import pygame
from pygame.locals import QUIT
from core.config import FPS, TILE_SIZE
from frontend.render import draw_map, draw_repartidor

def game_loop(pantalla, game):
    reloj = pygame.time.Clock()
    running = True

    while running:
        for evento in pygame.event.get():
            if evento.type == QUIT:
                running = False

        # Actualizar lógica
        game.repartidor.mover((game.mapa.width * TILE_SIZE, game.mapa.height * TILE_SIZE))
        game.camara.update(game.repartidor.rect)

        # Actualizar HUD
        game.hud.update_energy(-0.05)
        game.hud.add_score(1)

        # Dibujar
        pantalla.fill((0, 0, 0))
        draw_map(pantalla, game.mapa, game.camara, TILE_SIZE)
        draw_repartidor(pantalla, game.repartidor, game.camara)
        game.hud.draw()

        pygame.display.flip()
        reloj.tick(FPS)

    pygame.quit()
    sys.exit()
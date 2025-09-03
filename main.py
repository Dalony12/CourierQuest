import pygame
from core.config import ANCHO, ALTO, FPS, TILE_SIZE
from core.game import Game
from frontend.render import draw_map, draw_repartidor

def main():
    pygame.init()
    VENTANA_ANCHO, VENTANA_ALTO = 1024, 768
    JUEGO_ANCHO, JUEGO_ALTO = 750, 700
    PANEL_ANCHO = VENTANA_ANCHO - JUEGO_ANCHO
    PANEL_ALTO = VENTANA_ALTO

    pantalla = pygame.display.set_mode((VENTANA_ANCHO, VENTANA_ALTO))
    pygame.display.set_caption("CourierQuest")

    surface_juego = pygame.Surface((JUEGO_ANCHO, JUEGO_ALTO))
    surface_panel = pygame.Surface((PANEL_ANCHO, PANEL_ALTO))

    game = Game(surface_juego, JUEGO_ANCHO, JUEGO_ALTO)

    reloj = pygame.time.Clock()
    running = True

    while running:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                running = False

        teclas = pygame.key.get_pressed()

        # Calcular tamaño real del mapa en píxeles
        mapa_w = game.mapa.width * TILE_SIZE
        mapa_h = game.mapa.height * TILE_SIZE

        if mapa_w < JUEGO_ANCHO or mapa_h < JUEGO_ALTO:
            limite_x = JUEGO_ANCHO
            limite_y = JUEGO_ALTO
            offset_x = (JUEGO_ANCHO - mapa_w) // 2 if mapa_w < JUEGO_ANCHO else 0
            offset_y = (JUEGO_ALTO - mapa_h) // 2 if mapa_h < JUEGO_ALTO else 0
        else:
            limite_x = mapa_w
            limite_y = mapa_h
            offset_x = 0
            offset_y = 0

        # Movimiento del repartidor con lógica de bloqueo
        game.repartidor.mover(teclas)

        # Actualizar cámara y HUD
        game.camara.update(game.repartidor.rect)
        game.hud.update_energy(-0.05)
        game.hud.add_score(1)

        # --- Dibujo del panel HUD
        surface_panel.fill((40, 40, 40))
        game.hud.draw(surface_panel)

        # --- Dibujo del área de juego
        surface_juego.fill((0, 0, 0))
        if mapa_w < JUEGO_ANCHO or mapa_h < JUEGO_ALTO:
            subsurface = surface_juego.subsurface(pygame.Rect(offset_x, offset_y, mapa_w, mapa_h))
            draw_map(subsurface, game.mapa, game.camara, TILE_SIZE)
            draw_repartidor(subsurface, game.repartidor, game.camara)
        else:
            draw_map(surface_juego, game.mapa, game.camara, TILE_SIZE)
            draw_repartidor(surface_juego, game.repartidor, game.camara)

        # --- Composición final
        pantalla.fill((0, 0, 0))
        pantalla.blit(surface_panel, (JUEGO_ANCHO, 0))
        pantalla.blit(surface_juego, (0, 0))
        pygame.display.flip()
        reloj.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
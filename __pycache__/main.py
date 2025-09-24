import pygame
from core.config import ANCHO, ALTO
from core.game import Game
from core.loop import game_loop

def main():
    pygame.init()
    VENTANA_ANCHO, VENTANA_ALTO = 1024, 768
    JUEGO_ANCHO, JUEGO_ALTO = 750, 700

    pantalla = pygame.display.set_mode((VENTANA_ANCHO, VENTANA_ALTO))
    pygame.display.set_caption("CourierQuest")

    # Surface para el área de juego
    surface_juego = pygame.Surface((JUEGO_ANCHO, JUEGO_ALTO))

    game = Game(surface_juego, JUEGO_ANCHO, JUEGO_ALTO)

    def game_loop_mod(pantalla, game, surface_juego, JUEGO_ANCHO, JUEGO_ALTO):
        import sys
        import pygame
        from pygame.locals import QUIT
        from core.config import FPS, TILE_SIZE
        from frontend.render import draw_map, draw_repartidor
        reloj = pygame.time.Clock()
        running = True
        while running:
            for evento in pygame.event.get():
                if evento.type == QUIT:
                    running = False
            # Calcular tamaño real del mapa en píxeles
            mapa_w = game.mapa.width * TILE_SIZE
            mapa_h = game.mapa.height * TILE_SIZE
            # Si el mapa es más pequeño que el área de juego, centrar el mapa y permitir que el repartidor se mueva por todo el área de juego
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
            game.repartidor.mover((limite_x, limite_y))
            game.camara.update(game.repartidor.rect)
            # Actualizar clima dinámico
            game.clima.actualizar_clima()

            # Actualizar estado climático del repartidor
            estado = game.clima.get_estado_climatico()
            game.repartidor.aplicar_clima(estado["condicion"], estado["intensidad"])

            # Aplicar efecto climático al repartidor
            multiplicador = game.clima.get_multiplicador()
            game.repartidor.aplicar_multiplicador_velocidad(multiplicador)

            game.hud.add_score(1)

            # --- Dibujo de HUD de fondo (abarca toda la pantalla)
            pantalla.fill((0, 0, 0))
            game.hud.draw(pantalla)

            # --- Dibujo del área de juego (centrada en el HUD)
            surface_juego.fill((0, 0, 0))
            if mapa_w < JUEGO_ANCHO or mapa_h < JUEGO_ALTO:
                draw_map(surface_juego.subsurface(pygame.Rect(offset_x, offset_y, mapa_w, mapa_h)), game.mapa, game.camara, TILE_SIZE)
                draw_repartidor(surface_juego, game.repartidor, game.camara)
            else:
                draw_map(surface_juego, game.mapa, game.camara, TILE_SIZE)
                draw_repartidor(surface_juego, game.repartidor, game.camara)

            # Coordenadas para centrar el área de juego en la ventana principal, pero desplazadas un poco a la izquierda y arriba
            desplazamiento_x = 133  # 2 píxeles más a la derecha
            desplazamiento_y = -0   # base
            juego_x = (VENTANA_ANCHO - JUEGO_ANCHO) // 2 - desplazamiento_x
            juego_y = (VENTANA_ALTO - JUEGO_ALTO) // 2 - desplazamiento_y - 100 + 70  # 10 píxeles más abajo
            pantalla.blit(surface_juego, (juego_x, juego_y))

            # --- Dibujo de los elementos de la interfaz (sprites PNG) sobre todo
            game.hud.draw(pantalla)

            pygame.display.flip()
            reloj.tick(FPS)
        pygame.quit()
        sys.exit()

    game_loop_mod(pantalla, game, surface_juego, JUEGO_ANCHO, JUEGO_ALTO)

if __name__ == "__main__":
    main()

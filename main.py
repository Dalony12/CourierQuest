import pygame
from core.config import ANCHO, ALTO
from core.game import Game
from core.loop import game_loop

def main():
    pygame.init()
    VENTANA_ANCHO, VENTANA_ALTO = 1024, 768
    JUEGO_ANCHO, JUEGO_ALTO = 750, 700
    PANEL_ANCHO = VENTANA_ANCHO - JUEGO_ANCHO
    PANEL_ALTO = VENTANA_ALTO

    pantalla = pygame.display.set_mode((VENTANA_ANCHO, VENTANA_ALTO))
    pygame.display.set_caption("CourierQuest")

    # Surface para el área de juego
    surface_juego = pygame.Surface((JUEGO_ANCHO, JUEGO_ALTO))
    # Surface para el panel de interfaz (opcional, aquí solo lo llenamos de color)
    surface_panel = pygame.Surface((PANEL_ANCHO, PANEL_ALTO))

    game = Game(surface_juego, JUEGO_ANCHO, JUEGO_ALTO)

    def game_loop_mod(pantalla, game, surface_juego, surface_panel, JUEGO_ANCHO, JUEGO_ALTO):
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
            # --- Actualizar lógica de pedidos ---
        tiempo_actual = game.hud.tiempo_transcurrido()

        # Recoger pedidos disponibles
        for pedido in game.gestor_pedidos.obtener_disponibles(tiempo_actual):
            if not pedido.recogido and (game.repartidor.pos_x, game.repartidor.pos_y) == tuple(pedido.pickup):
                if game.repartidor.recoger_paquete(pedido):
                    pedido.recogido = True
                    print(f"📥 Pedido {pedido.id} recogido en {pedido.pickup}")

        # Entregar pedidos activos
        for pedido in game.repartidor.inventario.obtener_items():
            if not pedido.entregado and (game.repartidor.pos_x, game.repartidor.pos_y) == tuple(pedido.dropoff):
                from datetime import datetime
                pedido.retraso = max(0, int((datetime.now() - pedido.deadline).total_seconds() / 60))
                game.repartidor.entregar_paquete(pedido)
                pedido.entregado = True
                print(f"📤 Pedido {pedido.id} entregado en {pedido.dropoff}")
            game.camara.update(game.repartidor.rect)
            game.hud.update_energy(-0.05)
            game.hud.add_score(1)
            # --- Dibujo de panel HUD (fondo)
            surface_panel.fill((40, 40, 40))
            game.hud.draw(surface_panel)
            # --- Dibujo del área de juego (encima del HUD)
            surface_juego.fill((0, 0, 0))
            # Si el mapa es más pequeño, dibujar centrado
            if mapa_w < JUEGO_ANCHO or mapa_h < JUEGO_ALTO:
                draw_map(surface_juego.subsurface(pygame.Rect(offset_x, offset_y, mapa_w, mapa_h)), game.mapa, game.camara, TILE_SIZE)
                draw_repartidor(surface_juego, game.repartidor, game.camara)
            else:
                draw_map(surface_juego, game.mapa, game.camara, TILE_SIZE)
                draw_repartidor(surface_juego, game.repartidor, game.camara)
            # --- Composición final en la ventana principal
            pantalla.fill((0, 0, 0))
            pantalla.blit(surface_panel, (JUEGO_ANCHO, 0))
            pantalla.blit(surface_juego, (0, 0))
            pygame.display.flip()
            reloj.tick(FPS)
        pygame.quit()
        sys.exit()

    game_loop_mod(pantalla, game, surface_juego, surface_panel, JUEGO_ANCHO, JUEGO_ALTO)

if __name__ == "__main__":
    main()

import sys
import pygame
from pygame.locals import QUIT
from core.config import FPS, TILE_SIZE
from frontend.render import draw_map, draw_repartidor
from datetime import datetime
from backend.paquete import Paquete

def game_loop(pantalla, game):
    reloj = pygame.time.Clock()
    running = True

    while running:
        for evento in pygame.event.get():
            if evento.type == QUIT:
                running = False

        # Actualizar lógica
        game.repartidor.mover((game.mapa.width * TILE_SIZE, game.mapa.height * TILE_SIZE))
        # Detectar recogida
        if game.pedido_activo and not getattr(game.pedido_activo, "recogido", False):
            if (game.repartidor.pos_x, game.repartidor.pos_y) == tuple(game.pedido_activo.pickup):
                game.pedido_activo.recogido = True
                print(f"[DEBUG] Pedido {game.pedido_activo.id} recogido")

        # Detectar entrega
        if game.pedido_activo and getattr(game.pedido_activo, "recogido", False) and not getattr(game.pedido_activo, "entregado", False):
            if (game.repartidor.pos_x, game.repartidor.pos_y) == tuple(game.pedido_activo.dropoff):
                game.pedido_activo.entregado = True
                print(f"[DEBUG] Pedido {game.pedido_activo.id} entregado")

        game.camara.update(game.repartidor.rect)

        # Actualizar clima dinámico
        game.clima.actualizar_clima()

        # Actualizar estado climático del repartidor
        estado = game.clima.get_estado_climatico()
        game.repartidor.aplicar_clima(estado["condicion"], estado["intensidad"])

        # Aplicar efecto climático al repartidor
        multiplicador = game.clima.get_multiplicador()
        game.repartidor.aplicar_multiplicador_velocidad(multiplicador)

        # Actualizar lógica de pedidos

        tiempo_actual = game.hud.tiempo_transcurrido()

        # Sincronizar la barra de energía del HUD con la resistencia del repartidor
        game.hud.add_score(1)

        # Dibujar
        pantalla.fill((0, 0, 0))
        draw_map(pantalla, game.mapa, game.camara, TILE_SIZE)
        dibujar_paquete_y_buzon(pantalla, game)
        draw_repartidor(pantalla, game.repartidor, game.camara)
        game.hud.draw(surface=pantalla, mapa=game.mapa, repartidor=game.repartidor)
        
                
        tiempo_actual = game.hud.tiempo_transcurrido()

        # Mostrar pedidos disponibles en la posición actual
        for pedido in game.gestor_pedidos.obtener_disponibles(tiempo_actual):
            if (game.repartidor.pos_x, game.repartidor.pos_y) == tuple(pedido.pickup):
                # Botón de aceptar pedido
                btn_aceptar = pygame.image.load("assets/ui/btnAceptar.png").convert_alpha()
                btn_aceptar = pygame.transform.scale(btn_aceptar, (100, 40))
                pantalla.blit(btn_aceptar, (30, 700))  # posición en pantalla

                # Texto informativo
                game.hud.mostrar_texto(f"Pedido disponible: {pedido.id} → {pedido.dropoff}", x=150, y=710)

                if pygame.mouse.get_pressed()[0]:
                    mx, my = pygame.mouse.get_pos()
                    if pygame.Rect(30, 700, 100, 40).collidepoint(mx, my):
                        # Aceptar pedido
                        pedido.color = game.colores_paquete[game.indice_color % len(game.colores_paquete)]
                        game.indice_color += 1

                        paquete = Paquete()
                        paquete.codigo = pedido.id
                        paquete.origen = pedido.pickup
                        paquete.destino = pedido.dropoff
                        paquete.peso = pedido.peso
                        paquete.payout = pedido.payout
                        paquete.color = pedido.color

                        game.paquete_activo = paquete
                        game.pedido_activo = pedido


        # Mostrar pedidos en inventario
        for pedido in game.repartidor.inventario.obtener_items():
            game.hud.mostrar_texto(
                f"📦 {pedido.id} → {pedido.dropoff} | peso: {pedido.weight}",
                x=30,
                y=660 - 30 * game.repartidor.inventario.obtener_items().index(pedido),
                color=(200, 200, 0)
                )

        # Mostrar ícono de GPS si hay pedidos activos
        if game.repartidor.inventario.obtener_items():
            gps_icon = pygame.image.load("assets/ui/gps.png").convert_alpha()
            gps_icon = pygame.transform.scale(gps_icon, (40, 40))
            pantalla.blit(gps_icon, (950, 20))

        # Mostrar alerta de exceso de peso
        if game.repartidor.inventario.peso_total() > game.repartidor.pesoMaximo:
            peso_icon = pygame.image.load("assets/ui/excesoPesoOn.png").convert_alpha()
        else:
            peso_icon = pygame.image.load("assets/ui/excesoPesoOff.png").convert_alpha()
        peso_icon = pygame.transform.scale(peso_icon, (40, 40))
        pantalla.blit(peso_icon, (900, 20))

        pygame.display.flip()
        reloj.tick(FPS)

    pygame.quit()
    sys.exit()

def coordenadas_a_pixeles(coord):
    from core.config import TILE_SIZE
    x, y = coord
    return x * TILE_SIZE, y * TILE_SIZE

def dibujar_paquete_y_buzon(pantalla, game):
    if not game.paquete_activo or not game.pedido_activo:
        return

    color = game.paquete_activo.color

    # Mostrar paquete si no ha sido recogido
    if not getattr(game.pedido_activo, "recogido", False):
        sprite = game.hud.sprites.get(f"paquete{color}")
        if sprite:
            x, y = coordenadas_a_pixeles(game.paquete_activo.origen)
            pantalla.blit(sprite, (x, y))

    # Mostrar buzón si fue recogido pero no entregado
    if getattr(game.pedido_activo, "recogido", False) and not getattr(game.pedido_activo, "entregado", False):
        sprite = game.hud.sprites.get(f"buzon{color}")
        if sprite:
            x, y = coordenadas_a_pixeles(game.paquete_activo.destino)
            pantalla.blit(sprite, (x, y))

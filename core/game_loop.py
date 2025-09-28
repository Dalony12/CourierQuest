import pygame
from core.config import FPS, TILE_SIZE
from frontend.render import draw_map, draw_repartidor
from backend.paquete import Paquete
import random, math
from core.menu import pause_menu
from core.screens import resultado_final

def game_loop(pantalla, game, surface_juego, JUEGO_ANCHO, JUEGO_ALTO):
    print("[DEBUG] game_loop iniciado.")
    reloj = pygame.time.Clock()
    running = True
    paused = False
    tiempo_jornada = 10 * 60  # 10 minutos en segundos
    tiempo_inicio = pygame.time.get_ticks()
    last_move_time = 0
    move_delay = 148  # ms entre movimientos (3 celdas por segundo)
    move_dir = None
    anim_scale = 1.0
    anim_growing = True
    active_dirs = set()
    anim_phase = 0.0
    anim_speed = 0.12
    sliding = False
    slide_start = None
    slide_end = None
    slide_progress = 0.0
    rep = game.repartidor
    velocidad = rep.velocidad_actual()
    slide_duration = max(40, int(80 / velocidad))
    pedido_activo = None
    pedido_timer = pygame.time.get_ticks() + random.randint(3000, 6000)
    mostrar_pedido = False
    pedido_info = None
    pedido_aceptado = False
    pedido_en_curso = None
    barra_carga = None
    barra_tipo = None  # 'recoger' o 'entregar'
    barra_inicio = None
    barra_duracion = 2000  # ms (2 segundos)

    while running:
        dx, dy, dir = 0, 0, None
        moved = False
        current_time = pygame.time.get_ticks()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                running = False
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                paused = True
            if mostrar_pedido and evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_y:
                    pedido_aceptado = True
                elif evento.key == pygame.K_n:
                    mostrar_pedido = False
                    pedido_activo = None
                    pedido_info = None
                    pedido_timer = pygame.time.get_ticks() + random.randint(3000, 6000)
            if mostrar_pedido and evento.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                btn_rect = pygame.Rect(game.hud.sprite_positions['btnAceptar'], game.hud.sprites['btnAceptar'].get_size())
                btnr_rect = pygame.Rect(game.hud.sprite_positions['btnRechazar'], game.hud.sprites['btnRechazar'].get_size())
                if btn_rect.collidepoint(mx, my):
                    pedido_aceptado = True
                elif btnr_rect.collidepoint(mx, my):
                    mostrar_pedido = False
                    pedido_activo = None
                    pedido_info = None
                    pedido_timer = pygame.time.get_ticks() + random.randint(3000, 6000)
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    active_dirs.add("arriba")
                elif evento.key == pygame.K_DOWN:
                    active_dirs.add("abajo")
                elif evento.key == pygame.K_LEFT:
                    active_dirs.add("izq")
                elif evento.key == pygame.K_RIGHT:
                    active_dirs.add("der")
            if evento.type == pygame.KEYUP:
                if evento.key == pygame.K_UP:
                    active_dirs.discard("arriba")
                elif evento.key == pygame.K_DOWN:
                    active_dirs.discard("abajo")
                elif evento.key == pygame.K_LEFT:
                    active_dirs.discard("izq")
                elif evento.key == pygame.K_RIGHT:
                    active_dirs.discard("der")
        if active_dirs:
            move_dir = list(active_dirs)[-1]
        else:
            move_dir = None
        if not pedido_activo and not mostrar_pedido and pygame.time.get_ticks() > pedido_timer:
            disponibles = game.gestor_pedidos.obtener_disponibles(pygame.time.get_ticks() // 1000)
            if disponibles:
                pedido_activo = random.choice(disponibles)
                pedido_info = pedido_activo
                mostrar_pedido = True
        game.clima.actualizar_clima()
        estado = game.clima.get_estado_climatico()
        game.repartidor.aplicar_clima(estado["condicion"], estado["intensidad"])
        bloqueado = getattr(rep, '_bloqueado', False)
        if rep.resistencia <= 0:
            bloqueado = True
            rep._bloqueado = True
        if bloqueado and rep.resistencia >= 30:
            bloqueado = False
            rep._bloqueado = False
        game.clima.actualizar_clima()
        estado = game.clima.get_estado_climatico()
        game.repartidor.aplicar_clima(estado["condicion"], estado["intensidad"])
        multiplicador = game.clima.get_multiplicador()
        if move_dir and current_time - last_move_time > move_delay and not bloqueado and not sliding:
            velocidad = rep.velocidad_actual()
            if move_dir == "arriba":
                dy = -1
                dir = "arriba"
            elif move_dir == "abajo":
                dy = 1
                dir = "abajo"
            elif move_dir == "izq":
                dx = -1
                dir = "izq"
            elif move_dir == "der":
                dx = 1
                dir = "der"
            celda_x = (rep.rect.centerx // TILE_SIZE) + dx
            celda_y = (rep.rect.centery // TILE_SIZE) + dy
            new_x = celda_x * TILE_SIZE + TILE_SIZE // 2
            new_y = celda_y * TILE_SIZE + TILE_SIZE // 2
            if rep.puede_moverse_a(celda_x, celda_y):
                slide_start = (rep.rect.centerx, rep.rect.centery)
                slide_end = (new_x, new_y)
                slide_progress = 0.0
                sliding = True
                rep.direccion = dir
                rep.imagen_mostrar = rep.sprites[dir]
                rep._consumir_energia()
                rep._actualizar_estado()
                moved = True
                last_move_time = current_time
        if sliding and slide_start and slide_end:
            elapsed = reloj.get_time()
            slide_progress += elapsed / slide_duration
            if slide_progress >= 1.0:
                rep.rect.centerx, rep.rect.centery = slide_end
                sliding = False
            else:
                rep.rect.centerx = int(slide_start[0] + (slide_end[0] - slide_start[0]) * slide_progress)
                rep.rect.centery = int(slide_start[1] + (slide_end[1] - slide_start[1]) * slide_progress)
        # --- NUEVO FLUJO PAQUETE/BUZON ---
        from frontend.render import draw_paquete, draw_buzon, draw_barra_carga
        paquete = game.paquete_activo
        sprites_pb = game.hud.sprites_paquete_buzon
        tile_size = TILE_SIZE
        # Normalizar color para acceder a los sprites
        def color_key(base, color):
            return f"{base}{color.lower()}"
        # Dibuja paquete y buzón
        if paquete:
            paquete_sprite_key = color_key("paquete", paquete.color)
            buzon_sprite_key = color_key("buzon", paquete.color)
            draw_paquete(surface_juego, paquete, game.camara, tile_size, {paquete_sprite_key: sprites_pb.get(paquete_sprite_key)})
            draw_buzon(surface_juego, paquete, game.camara, tile_size, {buzon_sprite_key: sprites_pb.get(buzon_sprite_key)})
        # Detectar si repartidor está EN la celda del paquete para recoger
        if paquete and not paquete.recogido:
            px, py = paquete.origen
            rx, ry = rep.rect.centerx // tile_size, rep.rect.centery // tile_size
            if barra_carga is None and rx == px and ry == py:
                barra_carga = pygame.time.get_ticks()
                barra_tipo = 'recoger'
                barra_inicio = barra_carga
            if barra_carga is not None:
                progreso = min(1.0, (pygame.time.get_ticks()-barra_inicio)/barra_duracion)
                draw_barra_carga(surface_juego, px, py, progreso, tile_size, barra_tipo)
                # Solo completa la acción si sigue en la celda correcta
                if progreso >= 1.0 and rx == px and ry == py:
                    paquete.recogido = True
                    barra_carga = None
                    barra_tipo = None
                    barra_inicio = None
                elif progreso >= 1.0 and (rx != px or ry != py):
                    # Si se movió, reinicia la barra
                    barra_carga = None
                    barra_tipo = None
                    barra_inicio = None
        # Detectar si repartidor está EN la celda del buzón para entregar
        if paquete and paquete.recogido and not paquete.entregado:
            bx, by = paquete.destino
            rx, ry = rep.rect.centerx // tile_size, rep.rect.centery // tile_size
            if barra_carga is None and rx == bx and ry == by:
                barra_carga = pygame.time.get_ticks()
                barra_tipo = 'entregar'
                barra_inicio = barra_carga
            if barra_carga is not None:
                progreso = min(1.0, (pygame.time.get_ticks()-barra_inicio)/barra_duracion)
                draw_barra_carga(surface_juego, bx, by, progreso, tile_size, barra_tipo)
                # Solo completa la acción si sigue en la celda correcta
                if progreso >= 1.0 and rx == bx and ry == by:
                    paquete.entregado = True
                    payout = getattr(pedido_en_curso, 'payout', 100)
                    dinero += payout
                    game.repartidor.ingresos = dinero
                    barra_carga = None
                    barra_tipo = None
                    barra_inicio = None
                elif progreso >= 1.0 and (rx != bx or ry != by):
                    barra_carga = None
                    barra_tipo = None
                    barra_inicio = None
        if (move_dir and moved and not bloqueado) or sliding:
            anim_phase += anim_speed
            anim_scale = 1.0 + 0.18 * math.sin(anim_phase)
            base_img = rep.sprites[rep.direccion]
            w, h = base_img.get_width(), base_img.get_height()
            new_img = pygame.transform.scale(base_img, (int(w * anim_scale), int(h * anim_scale)))
            rep.imagen_mostrar = new_img
        else:
            anim_phase = 0.0
            anim_scale = 1.0
            rep.imagen_mostrar = rep.sprites[rep.direccion]
        if (not move_dir or bloqueado) and not sliding:
            rep.descansar()
            rep._actualizar_estado()
        game.camara.update(rep.rect)
        if paused:
            if not pause_menu(pantalla):
                return
            paused = False
        tiempo_actual = (pygame.time.get_ticks() - tiempo_inicio) // 1000
        tiempo_restante = max(0, tiempo_jornada - tiempo_actual)
        minutos = tiempo_restante // 60
        segundos = tiempo_restante % 60
        pantalla.fill((0, 0, 0))
        surface_juego.fill((0, 0, 0))
        draw_map(surface_juego, game.mapa, game.camara, TILE_SIZE)
        draw_repartidor(surface_juego, game.repartidor, game.camara)
        # Animaciones de clima visuales (puedes modularizar si lo prefieres)
        # ... (puedes copiar la lógica de clima visual aquí)
        # --- Renderizar paquete, buzón y barra de carga arriba de todo ---
        from frontend.render import draw_paquete, draw_buzon, draw_barra_carga
        paquete = game.paquete_activo
        sprites_pb = game.hud.sprites_paquete_buzon
        tile_size = TILE_SIZE
        def color_key(base, color):
            return f"{base}{color.lower()}"
        if paquete:
            paquete_sprite_key = color_key("paquete", paquete.color)
            buzon_sprite_key = color_key("buzon", paquete.color)
            draw_paquete(surface_juego, paquete, game.camara, tile_size, {paquete_sprite_key: sprites_pb.get(paquete_sprite_key)})
            draw_buzon(surface_juego, paquete, game.camara, tile_size, {buzon_sprite_key: sprites_pb.get(buzon_sprite_key)})
        # Barra de carga (si corresponde) SIEMPRE por encima de todo, sobre pantalla principal
        if paquete and not paquete.recogido and barra_carga is not None:
            px, py = paquete.origen
            progreso = min(1.0, (pygame.time.get_ticks()-barra_inicio)/barra_duracion)
            zoom = getattr(game.camara, 'zoom', 1.0)
            pantalla_x = int(px * tile_size * zoom) + juego_x
            pantalla_y = int(py * tile_size * zoom) + juego_y
            from frontend.render import draw_barra_carga
            draw_barra_carga(pantalla, pantalla_x, pantalla_y, progreso, int(tile_size * zoom), barra_tipo)
        if paquete and paquete.recogido and not paquete.entregado and barra_carga is not None:
            bx, by = paquete.destino
            progreso = min(1.0, (pygame.time.get_ticks()-barra_inicio)/barra_duracion)
            zoom = getattr(game.camara, 'zoom', 1.0)
            pantalla_x = int(bx * tile_size * zoom) + juego_x
            pantalla_y = int(by * tile_size * zoom) + juego_y
            from frontend.render import draw_barra_carga
            draw_barra_carga(pantalla, pantalla_x, pantalla_y, progreso, int(tile_size * zoom), barra_tipo)
        juego_x = (pantalla.get_width() - JUEGO_ANCHO) // 2 - 133
        juego_y = (pantalla.get_height() - JUEGO_ALTO) // 2 - 0 - 100 + 70
        pantalla.blit(surface_juego, (juego_x, juego_y))
        game.hud.draw(pantalla)
        game.hud.draw_minimap(game.mapa, game.repartidor, pantalla)
        if mostrar_pedido and pedido_info:
            game.hud.mostrar_pedido_app(pantalla, pedido_info)
        if pedido_aceptado and pedido_info:
            paquete = Paquete()
            paquete.codigo = pedido_info.id
            paquete.origen = tuple(pedido_info.pickup)
            paquete.destino = tuple(pedido_info.dropoff)
            paquete.peso = pedido_info.peso
            paquete.payout = pedido_info.payout
            paquete.color = random.choice(game.colores_paquete).lower()
            game.paquete_activo = paquete
            pedido_en_curso = pedido_info
            # El renderizado de paquete y buzón ahora se hace solo con las funciones draw_paquete/draw_buzon
            pedido_info.recogido = True
            mostrar_pedido = False
            pedido_activo = None
            pedido_info = None
            pedido_aceptado = False
            pedido_timer = pygame.time.get_ticks() + random.randint(3000, 6000)
        font = pygame.font.Font(None, 32)
        cronometro_txt = f"Fin de turno: {minutos:02d}:{segundos:02d}"
        cronometro = font.render(cronometro_txt, True, (255,255,255))
        bg_width = cronometro.get_width() + 18
        bg_height = cronometro.get_height() + 10
        bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
        bg_surface.fill((30, 30, 30, 160))
        pantalla.blit(bg_surface, (10, 10))
        pantalla.blit(cronometro, (18, 13))
    # --- Renderizar marcador de dinero por encima de todo ---
        # Renderizar marcador de dinero solo si el juego está en curso y el repartidor existe
        if hasattr(game, 'repartidor') and hasattr(game.repartidor, 'ingresos') and hasattr(game.repartidor, 'meta_ingresos'):
            dinero = getattr(game.repartidor, 'ingresos', 0)
            meta = getattr(game.repartidor, 'meta_ingresos', 1000)
            dinero_txt = f"${int(dinero):03d} / ${int(meta)}"
            dinero_render = font.render(dinero_txt, True, (255,255,255))
            dinero_bg_width = dinero_render.get_width() + 18
            dinero_bg_height = dinero_render.get_height() + 10
            dinero_bg_surface = pygame.Surface((dinero_bg_width, dinero_bg_height), pygame.SRCALPHA)
            dinero_bg_surface.fill((30, 30, 30, 160))
            pantalla.blit(dinero_bg_surface, (pantalla.get_width() - dinero_bg_width - 10, 10))
            pantalla.blit(dinero_render, (pantalla.get_width() - dinero_bg_width + 8, 13))
        pygame.display.flip()
        reloj.tick(FPS)
        if tiempo_restante <= 0:
            print(f"[DEBUG] game_loop termina por tiempo: tiempo_restante={tiempo_restante}")
            running = False
    resultado_final(pantalla, game.repartidor.meta_ingresos, game.repartidor.ingresos)
    return
